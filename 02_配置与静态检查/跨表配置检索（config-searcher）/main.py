#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
main.py - 跨表格关联检索工具 主入口
====================================
一个完全通用的跨表格关联检索工具。

核心设计原则：
  - 不绑定任何表名、字段名、业务逻辑
  - 表名 = 文件名自动识别
  - 字段含义、外键关联全部由 config.json 驱动
  - 支持任意关键词搜索任意表任意字段

使用方法:
  python main.py
        → 交互式模式，会提示输入工作区目录
  python main.py <工作区目录>
        → 直接进入交互式模式
  python main.py <工作区目录> <关键词>
        → 直接搜索模式
  python main.py <工作区目录> --list
        → 列出所有表格
"""

import os
import sys

import utils
from utils import fix_encoding, header, separator
from loader import TableLoader
from searcher import GlobalSearcher

# 修复 Windows 终端编码
fix_encoding()

# 确保当前目录在 Python 路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def load_config():
    """加载 config.json，处理可能的缺失"""
    cfg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    cfg = utils.load_json(cfg_path)
    if not cfg:
        # 返回空配置，仍可搜索但无含义和关联
        cfg = {"field_meanings": {}, "foreign_keys": {},
               "search_settings": {}, "output_settings": {}}
    return cfg


def build_searcher(workspace: str) -> GlobalSearcher:
    """构造搜索器"""
    config = load_config()
    loader = TableLoader(workspace)
    loader.load_all()
    return GlobalSearcher(loader, config)


def interactive(tool: GlobalSearcher):
    """交互式搜索模式（两级检索：先摘要列表 → 输入编号看详情）"""
    print(header("交互式搜索模式（两级检索）"))
    print("  输入关键词搜索 | list=列所有表 | q=退出\n")
    print("  搜索后显示摘要列表，输入编号(如 1) 查看某条详情")
    print("  支持: all=重新显示摘要 | simple=切换外键关联\n")

    show_fk = True
    last_results = []

    while True:
        try:
            cmd = input("[搜索] > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[退出]")
            break

        if not cmd:
            continue

        if cmd.lower() in ("quit", "exit", "q"):
            print("[退出]")
            break
        if cmd.lower() == "list":
            print(tool.list_tables_info())
            continue

        # 纯数字：在结果范围内当编号看详情，否则当关键词搜索
        if cmd.isdigit():
            num = int(cmd)
            if last_results and 1 <= num <= len(last_results):
                print(tool.format_detail(last_results[num - 1], show_fk=show_fk))
                print()
                continue
            # 数字不在结果范围内 → 当作关键词继续搜索

        if cmd.lower() == "all":
            if not last_results:
                print("\n  [提示] 还没有搜索结果，请先搜索关键词\n")
                continue
            print(tool.format_summary("上一次搜索", last_results))
            continue

        if cmd.lower() == "simple":
            show_fk = not show_fk
            mode = "简单模式 (仅搜索，不关联)" if not show_fk else "完整模式 (含关联数据)"
            print(f"\n[切换] 当前模式: {mode}\n")
            continue

        print(f"\n[搜索] '{cmd}' ...")
        last_results = tool.search(cmd)
        print(tool.format_summary(cmd, last_results))


def main():
    args = sys.argv[1:]

    if not args:
        # 无参：交互式，询问目录
        print(header("跨表格关联检索工具 v2.0"))
        print("  这是一个完全通用的跨表检索工具。")
        print("  支持任意关键词搜索任意表任意字段。\n")
        ws = input("请输入工作区目录路径: ").strip()
        if not ws:
            print("[退出]")
            return
        valid, msg = utils.validate_workspace(ws)
        if not valid:
            print(f"[错误] {msg}")
            return
        tool = build_searcher(ws)
        interactive(tool)
        return

    workspace = args[0]
    valid, msg = utils.validate_workspace(workspace)
    if not valid:
        print(f"[错误] {msg}")
        return

    if "--list" in args:
        tool = build_searcher(workspace)
        print(tool.list_tables_info())
        return

    if len(args) >= 2:
        keyword = " ".join(args[1:])
        tool = build_searcher(workspace)
        print(f"\n[搜索] '{keyword}'")
        results = tool.search(keyword)
        print(tool.format_results(keyword, results, show_fk=True))
        return

    # 只有目录参数：交互式
    tool = build_searcher(workspace)
    interactive(tool)


if __name__ == "__main__":
    main()
