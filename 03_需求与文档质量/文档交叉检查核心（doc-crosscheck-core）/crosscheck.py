# -*- coding: utf-8 -*-
"""确定性交叉比对内核(功能无关 / feature-agnostic)—— 只做 交互↔系统(旧「轴一」)
输入: <功能目录>/ir_interaction.json + ir_system.json
处理: 纯 Python 通用规则, 完全确定性(同输入同输出)。
输出: report.json(喂 gen_conflict_report.py 出 HTML) + 控制台摘要 + 内容指纹

★ 2026-07-24 收缩:原「轴二(交互↔蓝图)」整块移除。蓝图完整性/可实现性改由**独立的
  Flow B**(blueprint-review skill,读真实 UMG)负责,不再靠手写蓝图文档/ir_blueprint.json。
  本内核回归纯「交互↔系统」文档冲突检查。

== 架构分层(回答"换功能要不要改 py")==
1. 引擎(本文件): 只有通用规则, 不认识任何具体功能词(门票/上限/深境...)。**永不为某功能改。**
2. 词表 vocab.json: 项目级共享(术语别名 / UI 表现 token / 场景 key 的中文)。新功能一般只在这加词。
3. 每个功能: 只产 IR(ir_*.json)。实体用受控 key(scenario / fn / tokens)打标, 引擎据此比对。

规则全部基于 IR 里的**受控 key**, 不依赖任何文案子串匹配:
  - must_add : 系统某 scenario 交互没有(整条缺) / 或 tokens 没覆盖全(部分缺) -> 交互必须补做
  - follow_ix: 同 scenario 两边都有但 text/术语不同 -> 以交互为准(知会)
  - 交互有、系统没有 -> 不报

用法: python crosscheck.py <功能目录> [out.json]
"""
import sys, os, json, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fpaths

KIND_CN = {"mechanism": "表现", "reward_area": "界面状态", "toast": "提示(Toast)", "state": "状态"}


def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_ir(d, name):
    return load_json(fpaths.ir(d, name), {"doc": "(缺失)", "entities": []})


def load_vocab(feature_dir):
    """功能目录下的 vocab.json 优先, 否则用工具目录的项目级默认。"""
    here = os.path.dirname(os.path.abspath(__file__))
    v = load_json(os.path.join(here, "vocab.json"),
                  {"term_alias": {}, "ui_tokens": {}, "scenarios": {}})
    override = load_json(os.path.join(feature_dir, "vocab.json"), None)
    if override:
        for k in ("term_alias", "ui_tokens", "scenarios"):
            v.setdefault(k, {}).update(override.get(k, {}))
    return v


def by_kind(ir, kind):
    return [e for e in ir["entities"] if e["kind"] == kind]


def img(e):
    return [{"path": e["evidence"], "cap": e.get("term", e.get("scenario", ""))}] if e and e.get("evidence") else []


def run(ix, sys_, vocab):
    items = []
    ALIAS = vocab.get("term_alias", {})
    TOK = vocab.get("ui_tokens", {})
    SCN = vocab.get("scenarios", {})

    def tcn(toks):
        return [TOK.get(t, t) for t in toks]

    def label(e, sc):
        return e.get("attrs", {}).get("cn") or SCN.get(sc, sc)

    # 交互侧: scenario -> 实体列表
    ix_scn = {}
    for e in ix["entities"]:
        sc = e.get("scenario")
        if sc:
            ix_scn.setdefault(sc, []).append(e)

    # ===== 遍历系统的"功能点"(带 scenario 的实体):交互覆盖了没 =====
    for s in sys_["entities"]:
        sc = s.get("scenario")
        if not sc:
            continue
        if s.get("attrs", {}).get("required") is False:   # 选填, 不强制
            continue
        a = s.get("attrs", {})
        lab = label(s, sc)
        kcn = KIND_CN.get(s["kind"], "表现")
        matches = ix_scn.get(sc, [])

        if not matches:
            # 整条 scenario 交互没有 -> 必须补
            what = a.get("text") or lab
            items.append({
                "id": f"A-{sc}", "sev": "must_add", "side": "交互",
                "title": f"交互缺「{lab}」",
                "sources": ["系统"],
                "desc": f"【系统要求】{a.get('when','')}:{what}。\n"
                        f"【交互现状】交互稿里没有这个{kcn}。\n"
                        f"【结论】这是系统明确要的功能,交互需要补上。",
                "links": [a["link"]] if a.get("link") else [],
                "ask": f"交互补上「{lab}」。",
            })
            continue

        # tokens 部分覆盖检查
        need = set(a.get("tokens", []))
        if need:
            have = set()
            for m in matches:
                have |= set(m.get("attrs", {}).get("tokens", []))
            miss = sorted(need - have)
            if miss:
                items.append({
                    "id": f"A-tok-{sc}", "sev": "must_add", "side": "交互",
                    "title": f"交互缺「{lab}」的部分表现",
                    "sources": ["系统", "交互"],
                    "desc": f"【系统要求】{a.get('when','')}后,需要这些表现:\n"
                            f"  · " + "\n  · ".join(tcn(miss)) + "\n"
                            f"【交互现状】交互只画了:" + ("、".join(tcn(sorted(have & need))) or "基础态") + ",上面这些没画。\n"
                            f"【结论】系统要的功能,交互需要把这些表现补到稿里。",
                    "images": sum((img(m) for m in matches), []),
                    "ask": "交互补画:" + "、".join(tcn(miss)) + "。",
                })

        # 文案差异 -> 以交互为准
        stext = a.get("text")
        if stext:
            itext = next((m.get("attrs", {}).get("text") for m in matches if m.get("attrs", {}).get("text")), None)
            if itext and itext != stext:
                items.append({
                    "id": f"B-text-{sc}", "sev": "follow_ix",
                    "title": f"「{lab}」文案两边不同 → 以交互为准",
                    "sources": ["系统", "交互"],
                    "desc": f"系统:“{stext}”;交互:“{itext}”。\n"
                            f"交互是具体表现,UI 用交互这版;系统文案视为概括。",
                    "images": sum((img(m) for m in matches), []),
                    "ask": "(无需裁决)文案用交互这版。",
                })

    # ===== 术语别名(都有但叫法不同)-> 以交互为准 =====
    for fn in ALIAS:
        ix_terms = {e.get("term") for e in ix["entities"] if e.get("fn") == fn} - {None}
        sys_terms = {e.get("term") for e in sys_["entities"] if e.get("fn") == fn} - {None}
        if ix_terms and (sys_terms - ix_terms):
            items.append({
                "id": f"B-term-{fn}", "sev": "follow_ix",
                "title": f"术语不一致({fn}) → UI 以交互为准",
                "sources": ["系统", "交互"],
                "desc": f"交互用 {sorted(ix_terms)};系统用 {sorted(sys_terms)}。\n"
                        f"UI/命名以交互为准,系统用词视为功能概括。",
                "ask": "(无需裁决)代码/资产命名跟交互。",
            })

    # ===== 手柄端:纯交互内容,交互↔系统不冲突(系统不涉及输入),此处不报 =====
    # 手柄端「能不能实现」(蓝图撑不撑得起按键映射/焦点导航)由 Flow B 对真实蓝图审查,不在本内核。

    # ===== 需求待确认(缺失/含糊):缺失硬查 + 模型标的 unclear 汇总 =====
    seen = set()

    def add_info(key, title, desc, ask, side):
        if key in seen:
            return
        seen.add(key)
        items.append({"id": f"Q-{key}", "sev": "miss_info", "side": side,
                      "title": title, "sources": ["—"], "desc": desc, "ask": ask})

    for side, ir in (("交互", ix), ("系统", sys_)):
        for e in ir["entities"]:
            a = e.get("attrs", {})
            name = e.get("term") or e.get("scenario") or e.get("key") or e["kind"]
            if a.get("unclear"):  # 模型读文档时标的语义含糊(数据来源/用什么控件/判定边界没写清)
                add_info(f"unclear-{name}", f"需求不清:{name}",
                         f"[{side}] {name}:{a['unclear']}", "策划补充明确。", side)
            st = str(a.get("status", ""))
            # 只抓真正"需求含糊"的标记;"待配"是开发任务(加列导表),不算需求不清
            if any(kw in st for kw in ("澄清", "待确认", "待定", "不明", "未定")):
                k = "newmark" if e["kind"] == "new_mark" else f"status-{name}"
                t = "待确认:New 解锁提醒机制" if e["kind"] == "new_mark" else f"待确认:{name}"
                add_info(k, t, f"[{side}] {name} 标注「{st}」。", "确认后落实。", side)
    for e in by_kind(ix, "shop_entry"):  # 入口没写位置
        if not e.get("attrs", {}).get("location"):
            n = e.get("term", "入口")
            add_info(f"loc-{n}", f"入口位置未指明:{n}",
                     f"[交互] {n} 没写在哪个界面/位置进入。", "交互补入口位置。", "交互")
    for f in by_kind(sys_, "field"):  # 字段既无场景关联又无用途说明
        a = f.get("attrs", {})
        if a.get("scenarios") == [] and not a.get("name"):
            col = f"{a.get('table')}.{a.get('column')}"
            add_info(f"field-{col}", f"字段用途不清:{col}",
                     f"[系统] 字段 {col} 没关联场景、也没写用途。", "系统说明该字段用途。", "系统")

    order = {"must_add": 0, "follow_ix": 1, "miss_info": 2, "todo": 3}
    items.sort(key=lambda x: (order.get(x["sev"], 9), x["id"]))
    return items


def main():
    d = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else fpaths.report_dir(d, "report.json")
    os.makedirs(fpaths.report_dir(d), exist_ok=True)
    ix = load_ir(d, "ir_interaction.json")
    sys_ = load_ir(d, "ir_system.json")
    vocab = load_vocab(d)
    feature = load_json(os.path.join(d, "feature.json"), {})
    items = run(ix, sys_, vocab)

    title = feature.get("title") or f"{os.path.basename(d.rstrip('/\\'))} · 系统↔交互 比对报告"
    report = {
        "title": title,
        "meta": feature.get("meta") or
                (f"来源:{ix['doc']} × {sys_['doc']} | 模型:系统给功能概括,具体表现由交互完善;"
                 f"只筛①交互/系统需注意的功能点②以交互为准的差异。蓝图完整性/可实现性由 Flow B 独立审查。可复现。"),
        "items": items,
    }
    with open(out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    canon = json.dumps([{k: v for k, v in it.items() if k != "images"} for it in items],
                       ensure_ascii=False, sort_keys=True)
    h = hashlib.sha256(canon.encode("utf-8")).hexdigest()[:16]
    cnt = {}
    for it in items:
        cnt[it["sev"]] = cnt.get(it["sev"], 0) + 1
    print(f"[crosscheck] 共 {len(items)} 条: " + " ".join(f"{k}={v}" for k, v in sorted(cnt.items())))
    for it in items:
        print(f"  {it['sev']:9} {it['id']:26} {it['title']}")
    print(f"[fingerprint] {h}")
    print(f"[written] {out}")


if __name__ == "__main__":
    main()
