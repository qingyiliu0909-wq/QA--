# -*- coding: utf-8 -*-
"""文档交叉比对·冲突报告生成器
输入: 一个 report.json(标题/元信息/冲突条目, 每条可挂证据图与链接)
输出: 自包含 HTML(图片 base64 内嵌, 单文件可分享给策划/QA)
用法: python gen_conflict_report.py report.json out.html

report.json 结构:
{
  "title": "...", "meta": "...",
  "items": [{
    "id": "C1",
    "sev": "must_add|follow_ix|miss_info",
    "title": "...", "desc": "...",
    "sources": ["交互文","系统1"],          # 可选, 来源标记
    "links":   [{"text":"..","url":".."}],  # 可选, 外部链接(如飞书原文)
    "images":  [{"path":"evidence/x.png","cap":"..."}],  # 可选, 证据图(相对功能根目录)
    "ask": "需策划裁决的问题"               # 可选
  }]
}

出两个模块给策划看(同一份文件,不拆多份):
  模块① 文档冲突     = must_add(交互必须补做) + follow_ix(以交互为准)  —— 两份文档互相对不上
  模块② 需求清晰度   = miss_info(缺失/含糊)                           —— 单份文档本身够不够让 AI 确定怎么做
(★ 2026-07-24:原「模块③ 蓝图校验/轴二」已移除。蓝图完整性/可实现性改由独立的 Flow B 读真实蓝图审查。)
每条用原生 <details> 折叠(默认收起,只显示标签+标题),避免报告过长不好看;
每个模块头部有"展开全部/收起全部"按钮。
"""
import sys, os, json, base64, mimetypes, html

# 颜色按 sev 固定;文案(label)按 sev + side(哪边该注意)动态生成,别用"必须做"这种生硬措辞
SEV_COLOR = {
    "must_add": "#e23b3b", "follow_ix": "#2e9e5b", "miss_info": "#8b3fd6", "todo": "#888",
    # 兼容旧档(已不再产出)
    "conflict": "#e23b3b", "miss_ix": "#d39e00", "miss_sys": "#e8730c",
}
SEV_ICON = {"must_add": "🔴", "follow_ix": "🟢", "miss_info": "🟣", "todo": "⚪",
            "conflict": "🔴", "miss_ix": "🟡", "miss_sys": "🟠"}
LEGEND = [
    ("must_add", "交互注意 / 系统注意"),
    ("follow_ix", "以交互为准(知会)"),
    ("miss_info", "交互注意 / 系统注意(缺失、含糊)"),
]


def sev_label(it):
    """标签文案:按 side 分是"交互注意"还是"系统注意",别叫"必须做"。"""
    sev, side = it["sev"], it.get("side")
    icon = SEV_ICON.get(sev, "⚪")
    if sev == "must_add":
        return f"{icon} {side or '交互'}注意"
    if sev == "miss_info":
        return f"{icon} {side}注意(缺失/含糊)" if side in ("交互", "系统") else f"{icon} 需求待确认(缺失/含糊)"
    if sev == "follow_ix":
        return f"{icon} 以交互为准(知会)"
    if sev == "todo":
        return f"{icon} 交互↔蓝图待办"
    return f"{icon} {sev}"

MODULES = [
    ("mod-conflict", "📎 文档冲突", "两份文档互相对不上的地方(术语/文案/覆盖不一致)",
     {"must_add", "follow_ix", "conflict", "miss_ix", "miss_sys"}),
    ("mod-clarity", "🔎 需求清晰度", "单份文档本身够不够让 AI 确定怎么做(缺失/含糊,不涉及跨文档比对)",
     {"miss_info"}),
]

def ask_label(it):
    sev, side = it["sev"], it.get("side")
    if sev in ("must_add", "miss_info"):
        return f"{side or '策划'}确认"
    return {"follow_ix": "结论", "todo": "下一步"}.get(sev, "需确认")


def img_b64(path):
    mime = mimetypes.guess_type(path)[0] or "image/png"
    with open(path, "rb") as f:
        return f"data:{mime};base64,{base64.b64encode(f.read()).decode()}"


def esc(s):
    return html.escape(str(s)).replace("\n", "<br>")


def render_item(it, base_dir, open_=False):
    label, color = sev_label(it), SEV_COLOR.get(it["sev"], "#888")
    out = [f"<details class='card' style='border-left-color:{color}'{' open' if open_ else ''}>"]
    out.append("<summary>"
               f"<span class='tag' style='background:{color}'>{label}</span>"
               f"<span class='cid'>{esc(it['id'])}</span> "
               f"<span class='ctitle'>{esc(it['title'])}</span>"
               "</summary>")
    out.append("<div class='body'>")
    out.append("<div>" + "".join(f"<span class='src'>{esc(s)}</span>"
               for s in it.get("sources", [])) + "</div>")
    out.append(f"<div class='desc'>{esc(it['desc'])}</div>")
    for lk in it.get("links", []):
        out.append(f"<div class='desc'>🔗 <a href='{html.escape(lk['url'])}' "
                   f"target='_blank'>{esc(lk['text'])}</a></div>")
    if it.get("images"):
        out.append("<div class='imgs'>")
        for im in it["images"]:
            p = im["path"] if os.path.isabs(im["path"]) else os.path.join(base_dir, im["path"])
            out.append(f"<figure><img src='{img_b64(p)}' onclick=\"zoom(this.src)\">"
                       f"<figcaption>{esc(im.get('cap',''))}</figcaption></figure>")
        out.append("</div>")
    if it.get("ask"):
        out.append(f"<div class='ask'><b>{ask_label(it)}:</b> {esc(it['ask'])}</div>")
    out.append("</div></details>")
    return "".join(out)


def render(report, base_dir):
    items = report["items"]
    out = [f"""<!doctype html><html lang="zh"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(report['title'])}</title>
<style>
 body{{font-family:'Microsoft YaHei',sans-serif;margin:0;background:#f5f6f8;color:#222}}
 .wrap{{max-width:980px;margin:0 auto;padding:24px}}
 h1{{font-size:22px;margin:0 0 6px}}
 .meta{{color:#666;font-size:13px;margin-bottom:8px;line-height:1.7}}
 .legend span{{display:inline-block;margin-right:14px;font-size:13px}}
 .modsec{{margin-top:22px}}
 .modhead{{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;
   background:#fff;border-radius:10px;padding:12px 18px;box-shadow:0 1px 4px rgba(0,0,0,.08)}}
 .modh-left b{{font-size:16px}}
 .modh-left p{{margin:2px 0 0;font-size:12px;color:#777}}
 .modh-right button{{font-size:12px;border:1px solid #ccc;background:#f7f7f7;border-radius:6px;
   padding:4px 10px;cursor:pointer;margin-left:6px}}
 .modh-right button:hover{{background:#eee}}
 .empty{{color:#999;font-size:13px;padding:10px 18px}}
 .card{{background:#fff;border-radius:10px;padding:0;margin:12px 0;box-shadow:0 1px 4px rgba(0,0,0,.08);border-left:6px solid #ccc}}
 .card summary{{list-style:none;cursor:pointer;padding:14px 20px;display:block}}
 .card summary::-webkit-details-marker{{display:none}}
 .card summary::before{{content:'▸ ';color:#999}}
 .card[open] summary::before{{content:'▾ ';color:#999}}
 .card .body{{padding:0 20px 16px 20px}}
 .tag{{display:inline-block;padding:2px 10px;border-radius:12px;font-size:12px;font-weight:bold;color:#fff;margin-right:8px}}
 .cid{{color:#999;font-size:13px;font-weight:bold}}
 .ctitle{{font-size:15px;font-weight:bold}}
 .src{{font-size:12px;color:#555;background:#eef;border-radius:4px;padding:1px 7px;margin-right:6px;display:inline-block}}
 .desc{{line-height:1.8;font-size:14px;margin:8px 0}}
 .ask{{background:#f6faf6;border:1px dashed #5aa15a;border-radius:6px;padding:8px 12px;font-size:13px;margin-top:10px}}
 .ask b{{color:#2e7d32}}
 .imgs{{display:flex;flex-wrap:wrap;gap:10px;margin-top:10px}}
 .imgs figure{{margin:0;max-width:46%}}
 .imgs img{{width:100%;border:1px solid #ddd;border-radius:6px;cursor:zoom-in}}
 .imgs figcaption{{font-size:12px;color:#777;margin-top:4px}}
 .modal{{display:none;position:fixed;inset:0;background:rgba(0,0,0,.85);z-index:9;align-items:center;justify-content:center}}
 .modal img{{max-width:95%;max-height:95%}}
</style></head><body><div class="wrap">"""]
    out.append(f"<h1>{esc(report['title'])}</h1>")
    out.append(f"<div class='meta'>{esc(report.get('meta',''))}</div>")
    out.append("<div class='legend'>" + "".join(
        f"<span>{SEV_ICON[k]} {t}</span>" for k, t in LEGEND) + "</div>")

    for mid, mtitle, mdesc, sevs in MODULES:
        mitems = [it for it in items if it["sev"] in sevs]
        out.append(f"<div class='modsec' id='{mid}'>")
        out.append("<div class='modhead'><div class='modh-left'>"
                   f"<b>{esc(mtitle)}</b><p>{esc(mdesc)}</p></div>")
        out.append(f"<div class='modh-right'>"
                   f"<button onclick=\"toggleAll('{mid}',true)\">全部展开</button>"
                   f"<button onclick=\"toggleAll('{mid}',false)\">全部收起</button></div></div>")
        if not mitems:
            out.append("<div class='empty'>(本模块暂无条目 ✓)</div>")
        else:
            for it in mitems:
                out.append(render_item(it, base_dir))
        out.append("</div>")

    out.append("""<div class='modal' id='m' onclick="this.style.display='none'"><img id='mi'></div>
<script>
function zoom(s){document.getElementById('mi').src=s;document.getElementById('m').style.display='flex';}
function toggleAll(modId,open){
  document.getElementById(modId).querySelectorAll('details.card').forEach(function(d){d.open=open;});
}
</script>
</div></body></html>""")
    return "".join(out)


def find_root(start):
    """从 report.json 往上找,直到看见 feature.json 所在目录(功能根目录)。
    evidence 路径是"功能根目录相对"(如 _内部数据/strips_pc/x.png),不依赖固定层级深度。"""
    d = os.path.dirname(os.path.abspath(start))
    for _ in range(6):
        if os.path.exists(os.path.join(d, "feature.json")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    return os.path.dirname(os.path.abspath(start))


if __name__ == "__main__":
    spec, out_html = sys.argv[1], sys.argv[2]
    with open(spec, encoding="utf-8") as f:
        report = json.load(f)
    base_dir = find_root(spec)
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(render(report, base_dir))
    print("written:", out_html)
