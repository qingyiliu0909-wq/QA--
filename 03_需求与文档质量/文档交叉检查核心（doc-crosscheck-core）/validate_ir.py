# -*- coding: utf-8 -*-
"""IR 校验器(确定性护栏)
在比对之前校验 ir_*.json:结构合法、受控键都在词表内、关键字段不缺。
把"抽取准确率"从事后发现,提前成产出即拦截。

检查项:
  [ERROR] 结构非法 / kind 缺失 / 用了未知 kind
  [WARN ] scenario/fn/token 不在 vocab(可能是抽错, 或词表该加词 -> 见提案)
  [WARN ] toast/reward_area 缺 text;mechanism 缺 tokens
  [INFO ] 各 kind 计数 / 打了 scenario 的比例 / _proposals 汇总

用法: python validate_ir.py <功能目录>
退出码: 有 ERROR 返回 1, 否则 0(可接 CI)
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fpaths

HERE = os.path.dirname(os.path.abspath(__file__))
KINDS = {"button", "shop_entry", "state", "toast", "reward_area", "mechanism", "reddot", "hotkey", "anim", "field", "gamepad", "new_mark", "item_frame", "tab"}


def load_json(p, d):
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else d


def load_vocab(d):
    v = load_json(os.path.join(HERE, "vocab.json"), {"term_alias": {}, "ui_tokens": {}, "scenarios": {}})
    ov = load_json(os.path.join(d, "vocab.json"), None)
    if ov:
        for k in ("term_alias", "ui_tokens", "scenarios"):
            v.setdefault(k, {}).update(ov.get(k, {}))
    return v


def check(ir, name, vocab):
    errors, warns, proposals = [], [], []
    fns = set(vocab["term_alias"]); scns = set(vocab["scenarios"]); toks = set(vocab["ui_tokens"])
    kinds = {}
    n_scn = 0
    if not isinstance(ir.get("entities"), list):
        errors.append(f"{name}: 缺 entities 数组")
        return errors, warns, proposals, kinds, 0
    for i, e in enumerate(ir["entities"]):
        tag = f"{name}#{i}"
        k = e.get("kind")
        if not k:
            errors.append(f"{tag}: 缺 kind"); continue
        if k not in KINDS:
            errors.append(f"{tag}: 未知 kind '{k}'")
        kinds[k] = kinds.get(k, 0) + 1
        a = e.get("attrs", {})
        if e.get("fn") and e["fn"] not in fns:
            warns.append(f"{tag}: fn '{e['fn']}' 不在词表")
            proposals.append(("fn", e["fn"]))
        if e.get("scenario"):
            n_scn += 1
            sc = e["scenario"]
            if sc not in scns:
                warns.append(f"{tag}: scenario '{sc}' 不在词表")
                proposals.append(("scenario", sc))
            else:
                allowed = vocab.get("scenario_kinds", {}).get(sc)
                if allowed and k not in allowed:
                    warns.append(f"{tag}: scenario '{sc}' 贴在了 kind '{k}' 上,该场景只允许 {allowed}(疑似语义错位)")
        for t in a.get("tokens", []):
            if t not in toks:
                warns.append(f"{tag}: token '{t}' 不在词表")
                proposals.append(("token", t))
        if k in ("toast", "reward_area") and not a.get("text"):
            warns.append(f"{tag}({k}): 缺 text 文案")
        if k == "mechanism" and not a.get("tokens"):
            warns.append(f"{tag}(mechanism): 缺 tokens 表现")
    # 模型自带的 _proposals
    for p in ir.get("_proposals", []):
        proposals.append((p.get("type", "?"), p.get("key", "?")))
    return errors, warns, proposals, kinds, n_scn


def staleness(d):
    """源文档比 IR 新 -> IR 可能过时(策划改了文档/拉了新文件却没重抽)。
    interaction 和 system 分开各查各的源文档,不要用交互侧的新旧去判断系统侧(反之亦然)。"""
    import glob
    warns = []
    side_docs = {
        "interaction": glob.glob(os.path.join(fpaths.doc_dir(d, "interaction"), "*.pdf")),
        "system": glob.glob(os.path.join(fpaths.doc_dir(d, "system"), "**", "*.md"), recursive=True)
                  + glob.glob(os.path.join(fpaths.doc_dir(d, "system"), "**", "*.txt"), recursive=True)
                  + glob.glob(os.path.join(fpaths.doc_dir(d, "system"), "**", "*.pdf"), recursive=True),
    }
    for side, docs in side_docs.items():
        if not docs:
            continue
        newest = max(os.path.getmtime(p) for p in docs)
        ir = fpaths.ir(d, f"ir_{side}.json")
        if os.path.exists(ir) and newest > os.path.getmtime(ir) + 1:
            warns.append(f"源文档比 ir_{side}.json 新 -> IR 可能过时,文档改过后请重抽这一侧的 IR")
    return warns


def main():
    d = sys.argv[1]
    vocab = load_vocab(d)
    all_err, all_warn, all_prop = [], staleness(d), []
    for side in ("interaction", "system", "blueprint"):
        p = fpaths.ir(d, f"ir_{side}.json")
        if not os.path.exists(p):
            continue
        ir = load_json(p, {})
        err, warn, prop, kinds, n_scn = check(ir, side, vocab)
        all_err += err; all_warn += warn; all_prop += prop
        total = sum(kinds.values())
        print(f"\n=== ir_{side}.json ===  实体 {total}  打 scenario {n_scn}")
        print("  kind: " + ", ".join(f"{k}={v}" for k, v in sorted(kinds.items())))

    print("\n" + "=" * 40)
    if all_err:
        print(f"[ERROR] {len(all_err)} 条:")
        for e in all_err:
            print("   ✗ " + e)
    if all_warn:
        print(f"[WARN ] {len(all_warn)} 条:")
        for w in all_warn:
            print("   ! " + w)
    # 未知键提案(去重)汇总 -> 提示加词表
    uniq = sorted(set(all_prop))
    if uniq:
        print(f"[提案] 菜单外的 key {len(uniq)} 个(确认后加进 vocab.json):")
        for t, k in uniq:
            print(f"   + {t}: {k}")
    if not all_err and not all_warn:
        print("[PASS] IR 结构合法、受控键全部命中词表 ✓")
    print(f"\n结论: {'FAIL(有ERROR)' if all_err else 'OK'}")
    sys.exit(1 if all_err else 0)


if __name__ == "__main__":
    main()
