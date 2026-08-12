# -*- coding: utf-8 -*-
"""抽取 prompt 组装器
把项目词表(vocab.json)的受控键菜单 + 功能材料,注入抽取模板,
生成可直接喂给模型(本地 haiku 子 agent / 任意 LLM)的完整 prompt。

用法: python build_prompt.py <功能目录> [interaction|system]
  功能目录下可放 feature.json:
    {"materials": ["xxx.md", "strips"], "extract_hints": "罗盘弹窗三个按钮必抽 ..."}
  不写则自动扫描:目录下所有 *.md + strips/ 子目录。
输出: <功能目录>/_extract_prompt_<side>.txt
"""
import sys, os, json, glob
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import fpaths

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.dirname(HERE)


def load_json(p, d):
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else d


def load_vocab(feature_dir):
    v = load_json(os.path.join(TOOL, "vocab.json"), {"term_alias": {}, "ui_tokens": {}, "scenarios": {}})
    ov = load_json(os.path.join(feature_dir, "vocab.json"), None)
    if ov:
        for k in ("term_alias", "ui_tokens", "scenarios"):
            v.setdefault(k, {}).update(ov.get(k, {}))
    return v


def menu_fn(alias):
    return "\n".join(f"  - {k}: {'/'.join(v)}" for k, v in alias.items()) or "  (词表为空)"


def menu_kv(d):
    return "\n".join(f"  - {k}: {cn}" for k, cn in d.items()) or "  (词表为空)"


def collect_materials(feature_dir, feature, side="interaction"):
    mats = feature.get("materials")
    if mats:
        out = []
        for m in mats:
            p = m if os.path.isabs(m) else os.path.join(feature_dir, m)
            out.append(p)
        return out
    if side == "system":
        # 系统文档通常是纯文本(md/txt),直接从 策划/系统文档 递归扫,不需要经过切条转换
        sys_dir = fpaths.doc_dir(feature_dir, "system")
        out = sorted(glob.glob(os.path.join(sys_dir, "**", "*.md"), recursive=True))
        out += sorted(glob.glob(os.path.join(sys_dir, "**", "*.txt"), recursive=True))
        if out:
            return out
    # 兜底/interaction 默认:自动扫描 _内部数据 下的 *.md(PDF转出的文本层) + 任意 strips* 子目录
    in_dir = fpaths.inp(feature_dir)
    out = sorted(glob.glob(os.path.join(in_dir, "*.md")))
    out += sorted(d for d in glob.glob(os.path.join(in_dir, "strips*")) if os.path.isdir(d))
    return out


def main():
    d = sys.argv[1]
    side = sys.argv[2] if len(sys.argv) > 2 else "interaction"
    vocab = load_vocab(d)
    feature = load_json(os.path.join(d, "feature.json"), {})
    tmpl = open(os.path.join(HERE, "extract_prompt.md"), encoding="utf-8").read()

    mats = collect_materials(d, feature, side)
    mat_lines = "\n".join(f"  - {m}" for m in mats) or "  (未找到材料)"
    os.makedirs(fpaths.ir(d), exist_ok=True)
    out_path = fpaths.ir(d, f"ir_{side}.json")

    prompt = (tmpl
              .replace("{{MATERIALS}}", mat_lines)
              .replace("{{FN_LIST}}", menu_fn(vocab["term_alias"]))
              .replace("{{SCENARIO_LIST}}", menu_kv(vocab["scenarios"]))
              .replace("{{TOKEN_LIST}}", menu_kv(vocab["ui_tokens"]))
              .replace("{{HINTS}}", feature.get("extract_hints", "(无)"))
              .replace("{{OUT_PATH}}", out_path))

    dst = os.path.join(d, f"_extract_prompt_{side}.txt")
    open(dst, "w", encoding="utf-8").write(prompt)
    print(f"[build_prompt] side={side}  材料 {len(mats)} 项  词表: "
          f"fn={len(vocab['term_alias'])} scenario={len(vocab['scenarios'])} token={len(vocab['ui_tokens'])}")
    print(f"[written] {dst}")


if __name__ == "__main__":
    main()
