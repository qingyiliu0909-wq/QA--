# -*- coding: utf-8 -*-
"""一键跑一个功能:飞书拉取 → 切条 → 文本层 → 组装抽取prompt →(抽IR人工/haiku)→ 校验 → 比对 → 出报告

设计:幂等 + 在"抽 IR"那步自然停下(那步需要模型,脚本不替代)。
  - 第一次跑:把 0~2 段全做完,停在抽取,提示你用 haiku 抽 IR。
  - 抽完(ir_interaction.json + ir_system.json 就位)后再跑同一条命令:自动续做 3~5 段出报告。

用法: python run_feature.py <功能目录> [--force]
  功能目录需有 feature.json: {"doc_id":"<飞书URL或id>", "title":"...", "extract_hints":"..."}
  统一用 markitdown venv 的 python 跑(自带 fitz/PIL/requests):
    Tools/markitdown/Scripts/python.exe Tools/doc_crosscheck/run_feature.py <功能目录>
"""
import sys, os, json, glob, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fpaths

TOOL = os.path.dirname(os.path.abspath(__file__))
MARKIT = os.path.normpath(os.path.join(TOOL, "..", "markitdown"))
ENV = dict(os.environ, PYTHONIOENCODING="utf-8")


def sh(script, *args):
    cmd = [sys.executable, script, *map(str, args)]
    print(f"  $ {os.path.basename(script)} {' '.join(map(str, args))}")
    subprocess.run(cmd, env=ENV, check=True)


def banner(n, t):
    print(f"\n{'='*54}\n[{n}] {t}\n{'='*54}")


def platform_tag(pdf_basename, seen):
    """从文件名猜平台标签(手柄/手机/PC),用于每份交互PDF各自一个 strips_<tag> 目录,
    避免多份 PDF 共用一个 strips 目录时 page_01.png 互相覆盖(page图片名不含PDF来源名)。"""
    name = pdf_basename
    if "手柄" in name or "gamepad" in name.lower():
        tag = "pad"
    elif "手机" in name or "mobile" in name.lower():
        tag = "mobile"
    else:
        tag = "pc"
    if tag in seen:
        i = 2
        while f"{tag}{i}" in seen:
            i += 1
        tag = f"{tag}{i}"
    seen.add(tag)
    return tag


def main():
    if len(sys.argv) < 2:
        sys.exit("用法: python run_feature.py <功能目录> [--force]")
    out = os.path.abspath(sys.argv[1])
    force = "--force" in sys.argv
    feat = json.load(open(os.path.join(out, "feature.json"), encoding="utf-8")) \
        if os.path.exists(os.path.join(out, "feature.json")) else {}
    doc_id = feat.get("doc_id")
    source = fpaths.doc_dir(out, "interaction")

    # 0) 飞书自动拉取
    banner(0, "飞书拉取嵌入 PDF/图片")
    if not doc_id:
        print("  feature.json 没有 doc_id,跳过拉取(假设 PDF 已在 source/)")
    elif force or not glob.glob(os.path.join(source, "*.pdf")):
        sh(os.path.join(TOOL, "feishu_pull.py"), doc_id, source)
    else:
        print("  已有 PDF,跳过(--force 可强制重拉)")
    pdfs = sorted(glob.glob(os.path.join(source, "*.pdf")))
    print(f"  PDF 共 {len(pdfs)} 份")

    # 1) PDF -> 条带图 + 文本层(每份 PDF 各自一个 strips_<tag> 目录,
    #    因为 pdf_to_strips 渲染出的页图叫 page_01.png,不含来源PDF名,多份共用一个目录会互相覆盖)
    banner(1, "渲染切条 + 文本层")
    seen_tags = set()
    for pdf in pdfs:
        base = os.path.splitext(os.path.basename(pdf))[0]
        tag = platform_tag(base, seen_tags)
        strips = fpaths.inp(out, f"strips_{tag}")
        if force or not glob.glob(os.path.join(strips, "*strip*.png")):
            sh(os.path.join(TOOL, "pdf_to_strips.py"), pdf, strips)
        else:
            print(f"  strips_{tag} 已存在,跳过(--force 可强制重切)")
        md = fpaths.inp(out, base + ".md")
        if force or not os.path.exists(md):
            sh(os.path.join(MARKIT, "to_md.py"), pdf, fpaths.inp(out))

    # 2) 组装抽取 prompt(注入词表菜单)
    banner(2, "组装抽取 prompt(交互侧)")
    sh(os.path.join(TOOL, "extract", "build_prompt.py"), out, "interaction")

    # 抽取闸门:需要 ir_interaction.json + ir_system.json
    irx = fpaths.ir(out, "ir_interaction.json")
    irs = fpaths.ir(out, "ir_system.json")
    if not (os.path.exists(irx) and os.path.exists(irs)):
        banner("停", "抽取闸门(需模型介入)")
        print("  下一步(人/haiku 干):")
        print(f"   1. 用 haiku 按 {os.path.join(out, '_extract_prompt_interaction.txt')} 抽出 ir_interaction.json")
        if not os.path.exists(irs):
            print("   2. 补 ir_system.json(系统文档侧;可对系统飞书文档同样 feishu_pull + 抽取)")
        print("   3. 再跑一次本命令,自动续做 校验→比对→出报告")
        return

    # 3) 校验 IR
    banner(3, "校验 IR")
    subprocess.run([sys.executable, os.path.join(TOOL, "validate_ir.py"), out], env=ENV)

    # 4) 确定性比对
    banner(4, "确定性比对")
    sh(os.path.join(TOOL, "crosscheck.py"), out, fpaths.out(out, "report.json"))

    # 5) 出报告
    banner(5, "生成 HTML 报告")
    html = fpaths.out(out, "冲突报告.html")
    sh(os.path.join(TOOL, "gen_conflict_report.py"), fpaths.out(out, "report.json"), html)
    print(f"\n[完成] 报告: {html}")


if __name__ == "__main__":
    main()
