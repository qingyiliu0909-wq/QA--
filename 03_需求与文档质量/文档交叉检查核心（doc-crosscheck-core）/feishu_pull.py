# -*- coding: utf-8 -*-
"""飞书文档自动拉取(零搬运)
输入飞书文档(wiki 节点 token / docx token / URL),自动:
  1. 解析出文档里所有嵌入的【文件附件(PDF等)】和【图片】token
  2. 全部下载到功能目录,PDF 按原名、图片按序号
策划在飞书改完,这条命令重拉最新版,无需任何人发文件。

依赖: requests(自动从 Tools/markitdown 的 site-packages 借) + 飞书 UAT(lark-mcp 授权后)
用法: python feishu_pull.py <doc_id或URL> <输出目录> [--no-images]

前置: 飞书应用需开通 docs:document.media:download 权限并授权(lark_mcp.py auth)。
UAT ~2 小时过期, 过期时本脚本会提示重新授权。
"""
import sys, os, re, json, base64, time

# 自包含:把 markitdown venv 的 site-packages 加进来以借用 requests
_TOOL = os.path.dirname(os.path.abspath(__file__))
_SITE = os.path.normpath(os.path.join(_TOOL, "..", "markitdown", "Lib", "site-packages"))
if os.path.isdir(_SITE):
    sys.path.insert(0, _SITE)
import requests  # noqa: E402

B = "https://open.feishu.cn"
UAT_PATH = os.path.expanduser(r"~/.claude/skills/lark-mcp/config/uat_token.json")


def load_uat():
    if not os.path.exists(UAT_PATH):
        sys.exit(f"[错误] 找不到 UAT: {UAT_PATH}\n  先跑 lark-mcp 授权: lark_mcp.py auth")
    uat = json.load(open(UAT_PATH, encoding="utf-8"))["uat"]
    pl = uat.split(".")[1]; pl += "=" * (-len(pl) % 4)
    claims = json.loads(base64.urlsafe_b64decode(pl))
    if claims.get("exp", 0) < time.time():
        sys.exit("[错误] UAT 已过期, 请重新授权: lark_mcp.py auth")
    if "media:download" not in claims.get("scope", ""):
        print("[警告] 当前 token 没有 media:download 权限, 图片/附件可能下不了。"
              "后台开通 docs:document.media:download 并重新授权。")
    return uat


def parse_doc_id(s):
    m = re.search(r"/(?:wiki|docx|docs)/([A-Za-z0-9]+)", s)
    return m.group(1) if m else s.strip()


def resolve_docx(node, hdr):
    """wiki 节点 -> docx obj_token;若本就是 docx token 则原样返回。"""
    r = requests.get(f"{B}/open-apis/wiki/v2/spaces/get_node", headers=hdr,
                     params={"token": node}, timeout=30).json()
    obj = r.get("data", {}).get("node", {}).get("obj_token")
    return obj or node


def list_blocks(doc_id, hdr):
    blocks, page = [], None
    while True:
        p = {"page_size": 500}
        if page:
            p["page_token"] = page
        r = requests.get(f"{B}/open-apis/docx/v1/documents/{doc_id}/blocks",
                         headers=hdr, params=p, timeout=60).json()
        d = r.get("data", {})
        blocks += d.get("items", [])
        page = d.get("page_token")
        if not d.get("has_more"):
            break
    return blocks


def collect_media(blocks):
    files, images = [], []
    for b in blocks:
        if b.get("file", {}).get("token"):
            files.append((b["file"]["token"], b["file"].get("name", "")))
        if b.get("image", {}).get("token"):
            images.append(b["image"]["token"])
    return files, images


def download(token, route, hdr, dst):
    r = requests.get(f"{B}/open-apis/drive/v1/medias/{token}/download", headers=hdr,
                     params={"extra": json.dumps({"drive_route_token": route})}, timeout=180)
    ct = r.headers.get("Content-Type", "")
    if r.status_code == 200 and not ct.startswith("application/json"):
        open(dst, "wb").write(r.content)
        return len(r.content)
    raise RuntimeError(f"{r.status_code} {r.text[:120]}")


def safe_name(name, fallback):
    name = re.sub(r'[\\/:*?"<>|]', "_", name).strip()
    return name or fallback


def main():
    if len(sys.argv) < 3:
        sys.exit("用法: python feishu_pull.py <doc_id或URL> <输出目录> [--no-images]")
    raw, out = sys.argv[1], sys.argv[2]
    want_images = "--no-images" not in sys.argv
    os.makedirs(out, exist_ok=True)
    uat = load_uat()
    hdr = {"Authorization": f"Bearer {uat}"}

    node = parse_doc_id(raw)
    docx = resolve_docx(node, hdr)
    print(f"[飞书] 文档 {node} -> docx {docx}")
    files, images = collect_media(list_blocks(docx, hdr))
    print(f"[飞书] 发现 附件 {len(files)} 个, 图片 {len(images)} 张")

    manifest = {"doc_id": node, "docx": docx, "files": [], "images": []}
    for i, (tok, name) in enumerate(files):
        fn = safe_name(name, f"file_{i}.bin")
        try:
            n = download(tok, docx, hdr, os.path.join(out, fn))
            print(f"  [附件] {fn}  {n} bytes")
            manifest["files"].append({"name": fn, "token": tok, "bytes": n})
        except Exception as e:
            print(f"  [附件] {fn}  失败: {e}")

    if want_images:
        imgdir = os.path.join(out, "feishu_images")
        os.makedirs(imgdir, exist_ok=True)
        for i, tok in enumerate(images):
            fn = f"img_{i:02d}_{tok[:8]}.png"
            try:
                n = download(tok, docx, hdr, os.path.join(imgdir, fn))
                print(f"  [图片] {fn}  {n} bytes")
                manifest["images"].append({"name": fn, "token": tok, "bytes": n})
            except Exception as e:
                print(f"  [图片] {fn}  失败: {e}")

    json.dump(manifest, open(os.path.join(out, "feishu_manifest.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(f"[完成] 输出目录: {out}  (清单: feishu_manifest.json)")


if __name__ == "__main__":
    main()
