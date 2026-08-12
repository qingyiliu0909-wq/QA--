#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试外键关联发现功能"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from loader import TableLoader
from searcher import GlobalSearcher
from utils import load_json

def main():
    print("=== 测试外键关联发现 ===\n")
    
    # 加载表格
    loader = TableLoader('ExportDatas/datas')
    loader.load_all()
    
    # 加载配置
    config = load_json('config.json')
    searcher = GlobalSearcher(loader, config)
    
    # 搜索测试ID
    keyword = '210605'
    print(f"\n[搜索关键词] {keyword}")
    results = searcher.search(keyword)
    print(f"找到 {len(results)} 条结果")
    
    if results:
        result = results[0]
        print(f"\n[匹配记录] 表: {result.table_name}, 行号: {result.row_index}")
        print(f"[匹配字段] {result.matched_columns}")
        
        # 显示Reward字段值
        reward_val = result.row_data.get('Reward', 'N/A')
        print(f"[Reward字段值] {reward_val}")
        
        # 测试关联发现
        print(f"\n[关联发现结果]")
        fk_links = searcher.discover_and_resolve_fk(result.table_name, result.row_data)
        print(f"找到 {len(fk_links)} 条关联链路")
        
        for link in fk_links:
            print(f"  ├─ {link.source_field}={link.source_value} -> {link.target_table}")
            if link.children:
                for child in link.children:
                    print(f"  │  └─ {child.source_field}={child.source_value} -> {child.target_table}")
                    # 显示目标表的关键字段
                    brief = searcher._row_brief(child.target_table, child.target_row)
                    print(f"  │     └─ {brief}")
            else:
                brief = searcher._row_brief(link.target_table, link.target_row)
                print(f"  └─ {brief}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    main()