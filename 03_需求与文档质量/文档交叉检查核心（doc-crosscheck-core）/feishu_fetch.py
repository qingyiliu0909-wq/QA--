# -*- coding: utf-8 -*-
"""飞书文档正文抓取(纯文本 docx → 干净 md)
feishu_pull.py 只下载嵌入的附件/图片(交互稿那种索引页);
纯文本系统稿的正文在文档本体里,要用本脚本经 lark-mcp 的 feishu_fetch_doc 抓 markdown 正文。

用法: python feishu_fetch.py <doc_id或URL> <输出.md>
前提: 飞书已授权(lark_mcp.py auth;UAT ~2h 过期重扫)。
"""
import sys, os, re, json, subprocess

TOOL = os.path.dirname(os.path.abspath(__file__))
TRUNK = os.path.normpath(os.path.join(TOOL, "..", ".."))
SITE = os.path.join(TRUNK, "Tools", "markitdown", "Lib", "site-packages")
PY311 = os.path.join(TRUNK, "Validation", "Python311", "python.exe")
LARK = os.path.expanduser(r"~/.claude/skills/lark-mcp/scripts/lark_mcp.py")


def parse_id(s):
    m = re.search(r"/(?:wiki|docx|docs)/([A-Za-z0-9]+)", s)
    return m.group(1) if m else s.strip()


def fetch(doc_id):
    env = dict(os.environ, PYTHONPATH=SITE, PYTHONIOENCODING="utf-8")
    r = subprocess.run([PY311, LARK, "invoke", "feishu_fetch_doc",
                        json.dumps({"doc_id": doc_id})],
                       env=env, capture_output=True, text=True, encoding="utf-8")
    raw = r.stdout or ""
    # 健壮解析:lark_mcp 输出有日志 + 末尾一块 JSON-RPC 结果
    i = raw.rfind('{\n  "jsonrpc"')
    if i < 0:
        i = raw.rfind('{"jsonrpc"')
    if i >= 0:
        try:
            obj = json.loads(raw[i:])
            res = obj.get("result", {})
            if res.get("error"):
                sys.exit(f"[错误] 拉取失败:{res['error'].get('message')}"
                         f"(可能 UAT 过期 → 先跑 lark_mcp.py auth 重新授权)")
            inner = json.loads(res["content"][0]["text"])
            return inner.get("title", ""), inner.get("markdown", "")
        except Exception:
            pass
    # 兜底:正则直接抓 markdown 字段
    m = re.search(r'"markdown"\s*:\s*"(.*?)"\s*,\s*"message"', raw, re.S)
    if m:
        md = m.group(1).encode().decode("unicode_escape", "ignore")
        return "", md
    sys.exit(f"[错误] 解析失败,原始输出尾部:\n{raw[-300:]}")


def main():
    if len(sys.argv) < 3:
        sys.exit("用法: python feishu_fetch.py <doc_id或URL> <输出.md>")
    doc_id = parse_id(sys.argv[1])
    out = sys.argv[2]
    title, md = fetch(doc_id)
    os.makedirs(os.path.dirname(os.path.abspath(out)) or ".", exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"[feishu_fetch] {title or doc_id}  {len(md)} 字符 -> {out}")


if __name__ == "__main__":
    main()
