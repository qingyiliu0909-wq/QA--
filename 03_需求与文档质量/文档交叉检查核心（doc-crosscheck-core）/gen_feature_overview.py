# -*- coding: utf-8 -*-
"""功能概述生成器(替代原 compile_spec.py / "工单"概念,已弃用)

以前的"工单"是靠 IR 机械拼 T1..Tn 任务清单,挂标准卡/蓝图控件/数据字段,想在开发前驱动 AI 一项项做。
用户决定:开发直接照 `<功能>_开发文档.md`(§2.8 产出,业务规则+复用+数据来源已经够详细)来做,
不需要另开一份 IR 任务清单;工单这个角色**完全取消**。

这个脚本换了个更小的角色:**开发完成后**生成一份纯给人看的"功能概述"——只有
概述 / 交互流程 / 数据来源 三块,用来"以后忘了这个功能是干嘛的/数据在哪"时回来查。
不做 IR 匹配、不做标准卡匹配、不做蓝图控件匹配——这些已经不需要了。

输入: feature.json 的 overview(summary/flow) + <功能>_开发文档.md 的"数据来源"章节。
输出: 程序/工单/功能概述.json + 功能概述.html(和开发文档放一起)。

用法: python gen_feature_overview.py <功能目录>
"""
import sys, os, json, re, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fpaths

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def load(p, d):
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else d


def extract_section(md_text, keyword):
    """找标题(#号行)里含 keyword 的那一节,把正文抠到下一个同级/更高级标题为止。找不到返回 None。"""
    lines = md_text.splitlines()
    start, start_level = None, None
    for i, line in enumerate(lines):
        m = re.match(r"(#+)\s*.*" + re.escape(keyword), line)
        if m:
            start, start_level = i + 1, len(m.group(1))
            break
    if start is None:
        return None
    end = len(lines)
    for j in range(start, len(lines)):
        m = re.match(r"(#+)\s", lines[j])
        if m and len(m.group(1)) <= start_level:
            end = j
            break
    return "\n".join(lines[start:end]).strip()


def md_inline(s):
    """极简行内 markdown → html:`code` / **bold** / <br>。

    先整体转义(防注入),再把这三样还原回真标签。不这么做的话,文档里写的反引号和
    星号会被原样转义成字面量显示在页面上(表格里满屏 `xx` 和 **xx**,非常难读)。
    """
    s = html.escape(s)
    s = s.replace("&lt;br&gt;", "<br>").replace("&lt;br/&gt;", "<br>")
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    return s


def md_paragraphs(s):
    """把带换行的文本渲染成多个 <p>,免得长概述堆成一大坨读不下去。"""
    parts = [p.strip() for p in s.splitlines() if p.strip()]
    return "".join(f"<p>{md_inline(p)}</p>" for p in parts)


def md_table_to_html(md_table_text):
    """极简 markdown 表格转 html,只吃 `| a | b |` 这种行,够用就行,不追求通用 markdown 解析。"""
    rows = [l.strip() for l in md_table_text.splitlines() if l.strip().startswith("|")]
    if not rows:
        return f"<pre>{html.escape(md_table_text)}</pre>"
    out = ["<table>"]
    for i, r in enumerate(rows):
        cells_raw = r.strip("|").split("|")
        if i == 1 and all(set(c.strip()) <= set("-: ") for c in cells_raw):
            continue  # 分隔行 |---|---|
        tag = "th" if i == 0 else "td"
        out.append("<tr>" + "".join(f"<{tag}>{md_inline(c.strip())}</{tag}>" for c in cells_raw) + "</tr>")
    out.append("</table>")
    return "".join(out)


def build(d):
    feat = load(os.path.join(d, "feature.json"), {})
    ov = feat.get("overview", {})
    fd = feat.get("feature_doc")
    dev_md_path = os.path.join(d, fd) if fd else fpaths.workorder_dir(d, "开发文档.md")
    dev_md = open(dev_md_path, encoding="utf-8").read() if os.path.exists(dev_md_path) else ""
    data_section = extract_section(dev_md, "数据来源") if dev_md else None
    return {
        "feature": os.path.basename(d.rstrip("/\\")),
        "summary": ov.get("summary", ""),
        "flow": ov.get("flow", []),
        "test_guide": ov.get("test_guide", {}),
        "data_sources_raw": data_section,
        "source_doc": fd,
    }


def render_html(spec, out):
    def esc(s):
        return html.escape(str(s))
    p = [f"""<!doctype html><html lang=zh><head><meta charset=utf-8>
<title>功能概述 · {esc(spec['feature'])}</title><style>
 body{{font-family:'Microsoft YaHei',sans-serif;background:#f5f6f8;margin:0;line-height:1.65}}
 .w{{max-width:860px;margin:0 auto;padding:24px}}
 h1{{font-size:21px}} .sub{{color:#888;font-size:13px;margin-bottom:16px}}
 .sec{{background:#fff;border-radius:9px;padding:16px 20px;margin:14px 0;box-shadow:0 1px 4px rgba(0,0,0,.08)}}
 .sec h2{{font-size:15px;margin:0 0 8px}}
 table{{border-collapse:collapse;width:100%;font-size:13px}} td,th{{border:1px solid #eee;padding:7px 10px;text-align:left;vertical-align:top}}
 th{{background:#fafafa}}
 td:first-child{{white-space:nowrap}}
 code{{background:#f3f4f6;border-radius:3px;padding:1px 5px;font-family:Consolas,monospace;font-size:12px;color:#c7254e}}
 .sec p{{margin:0 0 9px}} .sec p:last-child{{margin-bottom:0}}
 .sec h3{{font-size:13px;margin:14px 0 6px;color:#555}} .sec h3:first-of-type{{margin-top:4px}}
 .sec h3.warn{{color:#b45309}}
 ol,ul{{padding-left:22px}} li{{margin:5px 0}}
</style></head><body><div class=w>"""]
    p.append(f"<h1>功能概述 · {esc(spec['feature'])}</h1>")
    p.append(f"<div class=sub>开发完成后生成,给人回忆需求用(不是开发期任务清单)。"
             f"业务权威详情见 <code>{esc(spec.get('source_doc') or '开发文档.md')}</code></div>")
    p.append("<div class=sec><h2>概述</h2>" +
             (md_paragraphs(spec["summary"]) if spec.get("summary")
              else "<p><i>(空,先做 §2.8 业务层生成)</i></p>") + "</div>")
    if spec.get("flow"):
        p.append("<div class=sec><h2>交互流程</h2><ol>" +
                 "".join(f"<li>{md_inline(x)}</li>" for x in spec["flow"]) + "</ol></div>")
    # 测试指引(可选):给测试同学的"怎么测",有 overview.test_guide 才渲染
    tg = spec.get("test_guide") or {}
    if tg:
        t = ["<div class=sec><h2>测试指引</h2>"]
        if tg.get("preconditions"):
            t.append("<h3>前置条件</h3><ul>" +
                     "".join(f"<li>{md_inline(x)}</li>" for x in tg["preconditions"]) + "</ul>")
        if tg.get("cases"):
            t.append("<h3>测试点</h3><table><tr><th>测试点</th><th>怎么造条件</th><th>预期表现</th></tr>" +
                     "".join("<tr><td>{}</td><td>{}</td><td>{}</td></tr>".format(
                         md_inline(c.get("点", "")), md_inline(c.get("怎么造", "")), md_inline(c.get("预期", "")))
                         for c in tg["cases"]) + "</table>")
        if tg.get("known_issues"):
            t.append("<h3 class=warn>已知问题 / 测不出来的点</h3><ul>" +
                     "".join(f"<li>{md_inline(x)}</li>" for x in tg["known_issues"]) + "</ul>")
        t.append("</div>")
        p.append("".join(t))
    p.append("<div class=sec><h2>数据来源</h2>" +
              (md_table_to_html(spec["data_sources_raw"]) if spec.get("data_sources_raw")
               else "<i>(开发文档.md 里没找到『数据来源』章节)</i>") + "</div>")
    p.append("</div></body></html>")
    open(out, "w", encoding="utf-8").write("".join(p))


def main():
    if len(sys.argv) < 2:
        sys.exit("用法: python gen_feature_overview.py <功能目录>")
    d = sys.argv[1]
    spec = build(d)
    os.makedirs(fpaths.workorder_dir(d), exist_ok=True)
    out_json = fpaths.workorder_dir(d, "功能概述.json")
    json.dump(spec, open(out_json, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    out_html = fpaths.workorder_dir(d, "功能概述.html")
    render_html(spec, out_html)
    print(f"[功能概述] {spec['feature']} -> {out_json}")
    print(f"[written] {out_html}")
    if not spec["summary"]:
        print("[! 提醒] feature.json.overview 是空的——先做 §2.8 业务层生成再跑这个。")
    if not spec.get("data_sources_raw"):
        print("[! 提醒] 开发文档.md 里没找到标题含『数据来源』的章节,数据来源部分会是空的,检查一下标题措辞。")


if __name__ == "__main__":
    main()
