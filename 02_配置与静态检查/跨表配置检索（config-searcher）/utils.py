#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
utils.py - 通用工具函数
=========================
字符串格式化、输出美化、文件路径处理等通用函数。
完全不绑定任何业务、任何表名、任何字段名。
"""

import os
import sys
import json


def resolve_path(path: str) -> str:
    """规范化文件路径"""
    return os.path.normpath(path)


def get_file_extension(filepath: str) -> str:
    """获取文件扩展名（小写）"""
    return os.path.splitext(filepath)[1].lower()


def is_excel_or_csv(filepath: str) -> bool:
    """判断文件是否为 Excel 或 CSV"""
    ext = get_file_extension(filepath)
    return ext in ['.xlsx', '.xls', '.csv']


def extract_table_name(filepath: str) -> str:
    """
    从文件路径提取表名
    'ExportDatas/datas/Reward.xlsx' -> 'Reward'
    """
    return os.path.splitext(os.path.basename(filepath))[0]


def collect_files_recursive(directory: str) -> list:
    """递归收集目录下所有文件，跳过隐藏/缓存目录"""
    file_list = []
    skip_dirs = {'.git', '__pycache__', 'node_modules', '.svn', '.vs',
                 '.vscode', 'logs', 'temp', 'bin', 'obj', 'py37',
                 'zoneinfo', 'Lib', 'pytz'}
    try:
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if not d.startswith('.')
                       and d not in skip_dirs]
            for f in files:
                file_list.append(os.path.join(root, f))
    except Exception as e:
        print(f"[警告] 扫描目录出错: {e}")
    return file_list


def validate_workspace(path: str) -> tuple:
    """验证工作区目录是否存在"""
    if not os.path.exists(path):
        return False, f"目录不存在: {path}"
    if not os.path.isdir(path):
        return False, f"路径不是目录: {path}"
    return True, ""


def load_json(path: str) -> dict:
    """加载 JSON 配置文件"""
    if not os.path.exists(path):
        print(f"[警告] 配置文件不存在: {path}，使用空配置")
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[错误] 加载配置失败: {e}")
        return {}


def truncate(text, max_len=500) -> str:
    """截断过长的字符串"""
    if text is None:
        return ""
    text = str(text)
    if len(text) <= max_len:
        return text
    return text[:max_len - 3] + "..."


def separator(char="─", length=72) -> str:
    """生成分隔线"""
    return char * length


def header(title: str, width=72) -> str:
    """生成标题块"""
    sep = separator("═", width)
    pad = max(0, (width - len(title)) // 2)
    return f"\n{sep}\n{' ' * pad}{title}\n{sep}"


def fmt_field(name: str, value: str, meaning: str = "", max_val=500) -> str:
    """格式化单行字段输出"""
    val = truncate(value, max_val)
    # 含义字段避免过早截断，尤其是结构化条件串（QuestChain等）
    meaning = truncate(meaning or "-", max(120, int(max_val) * 2))
    return f"│ 字段: {name:<20} │ 值: {val} │ 含义: {meaning}"


def fix_encoding():
    """修复 Windows 终端 UTF-8 编码问题"""
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
