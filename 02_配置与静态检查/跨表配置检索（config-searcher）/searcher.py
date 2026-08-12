#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
searcher.py - 通用跨表检索 + 自动关联发现引擎 v2.0
=====================================================
核心功能：
  1. 全局关键词检索——在所有表的所有单元格中搜索
  2. 自动外键关联发现——基于命名约定自动发现关联，无需手动配置
  3. 递归关联查询——自动追踪完整的关联链路
  4. 两级输出模式：摘要视图 + 详情视图

关联发现规则：
  规则1: 字段名 = "XXId" → 查找表 "XX" 的主键 "XXId"
         例: RegionId → Region表.RegionId
  规则2: 字段名包含表名关键词 → 模糊匹配
         例: UnlockCondition → Condition表.ConditionId
  规则3: List/Dict字段解析其中的ID进行关联
"""

from typing import Dict, List, Optional, Tuple, Set
import pandas as pd
import re

from loader import TableLoader, TableData, FieldMeta
from utils import header, separator, fmt_field, truncate


class SearchResult:
    """单条搜索结果"""

    def __init__(self, table_name: str, row_index: int, row_data: dict,
                 matched_columns: List[str]):
        self.table_name = table_name
        self.row_index = row_index          # 行号（从1开始）
        self.row_data = row_data            # {字段名: 值}
        self.matched_columns = matched_columns  # 命中的字段名列表


class FKLink:
    """外键关联链路"""
    
    def __init__(self, source_table: str, source_field: str, source_value: str,
                 target_table: str, target_field: str, target_row: dict):
        self.source_table = source_table
        self.source_field = source_field
        self.source_value = source_value
        self.target_table = target_table
        self.target_field = target_field
        self.target_row = target_row
        self.children: List['FKLink'] = []  # 递归子关联
    
    def __repr__(self) -> str:
        return f"FKLink({self.source_table}.{self.source_field}={self.source_value} -> {self.target_table})"


class AutoFKDiscoverer:
    """
    自动外键关联发现器
    
    基于命名约定自动发现表之间的关联关系，无需手动配置foreign_keys。
    """
    
    def __init__(self, loader: TableLoader):
        self.loader = loader
        # 缓存：表名 -> 主键字段
        self._table_pk_cache: Dict[str, str] = {}
        # 缓存：字段名 -> 可能的目标表列表
        self._field_target_cache: Dict[str, List[str]] = {}
        # 构建表名索引（用于快速查找）
        self._build_table_index()
    
    def _build_table_index(self):
        """构建表名索引，支持快速查找"""
        self._table_names_lower = {}
        for name, td in self.loader.tables.items():
            self._table_names_lower[name.lower()] = name
            # 缓存主键
            if td.primary_key:
                self._table_pk_cache[name] = td.primary_key
    
    def _find_table_by_name(self, table_name: str) -> Optional[str]:
        """根据表名查找实际表名（支持模糊匹配）"""
        key = table_name.lower()
        if key in self._table_names_lower:
            return self._table_names_lower[key]
        # 模糊匹配：包含关系
        for name_lower, name_orig in self._table_names_lower.items():
            if key in name_lower or name_lower in key:
                return name_orig
        return None
    
    def _extract_table_name_from_field(self, field_name: str) -> List[str]:
        """
        从字段名中提取可能的表名
        
        例: 
        - RegionId -> ["Region"]
        - UnlockCondition -> ["Condition"]
        - DispatchCondition -> ["Condition", "Dispatch"]
        - Reward -> ["Reward"]
        - PetUnitId -> ["Pet", "PetUnit"]
        """
        candidates = []
        field_lower = field_name.lower()
        
        # 规则1: 去掉"Id"或"ID"后缀
        for suffix in ['Id', 'ID', '_Id', '_ID']:
            if field_name.endswith(suffix):
                base = field_name[:-len(suffix)]
                if base:
                    candidates.append(base)
                break
        
        # 规则2: 字段名本身就是表名（如 Reward, Condition, Quest）
        # 扩展的常见表名列表
        common_tables = [
            'Condition', 'Reward', 'Quest', 'Region', 'SubRegion', 
            'Dispatch', 'Resource', 'Dungeon', 'Character', 'Monster',
            'Item', 'Skill', 'Buff', 'Story', 'Dialogue', 'NPC',
            'Player', 'Account', 'Guild', 'Shop', 'Gacha', 'Mail',
            'Title', 'Achievement', 'BattlePass', 'Pet', 'Mount',
            'Weapon', 'Armor', 'Accessory', 'Material', 'Currency',
            'Drop', 'Avatar', 'Hero', 'Task', 'Event', 'Config',
            'TextMap', 'Talk', 'Chapter', 'Scene', 'Map', 'Point',
            'Trigger', 'Box', 'Unit', 'Static', 'Impression',
            'Teleport', 'Waypoint', 'Spawn', 'Group'
        ]
        
        for table in common_tables:
            table_lower = table.lower()
            # 精确匹配或包含匹配
            if field_lower == table_lower or table_lower in field_lower:
                candidates.append(table)
        
        # 规则3: 特殊字段名映射
        special_mappings = {
            'reward': 'Reward',
            'condition': 'Condition', 
            'quest': 'Quest',
            'region': 'Region',
            'subregion': 'SubRegion',
            'dispatch': 'Dispatch',
            'resource': 'Resource',
            'petunit': 'Pet',
            'petstatic': 'Pet',
            'triggerbox': 'InteractTrigger',
            'storypath': 'Story',
            'dynimpression': 'Impression',
            'excId': 'Dispatch',  # 互斥派遣ID
            'questchain': 'Quest',
            'unlockcondition': 'Condition',
            'dispatchcondition': 'Condition',
            'showcondition': 'Condition',
            'regiondispcondition': 'Condition',
        }
        
        for key, table in special_mappings.items():
            if key.lower() in field_lower:
                candidates.append(table)
        
        # 去重并保持顺序
        return list(dict.fromkeys(candidates))
    
    def discover_fk(self, field_name: str, field_value: str) -> List[Tuple[str, str]]:
        """
        发现字段的外键关联
        
        返回: [(目标表名, 目标主键字段), ...]
        """
        cache_key = field_name
        if cache_key in self._field_target_cache:
            return self._field_target_cache[cache_key]
        
        results = []
        
        # 提取可能的表名
        table_candidates = self._extract_table_name_from_field(field_name)
        
        for candidate in table_candidates:
            target_table = self._find_table_by_name(candidate)
            if target_table:
                target_pk = self._table_pk_cache.get(target_table, f"{candidate}Id")
                results.append((target_table, target_pk))
        
        self._field_target_cache[cache_key] = results
        return results


class GlobalSearcher:
    """
    全局搜索引擎 v2.0
    
    支持自动关联发现的跨表检索引擎。
    """

    def __init__(self, loader: TableLoader, config: dict):
        """
        参数:
            loader: 已加载所有表格的 TableLoader 实例
            config: 完整配置字典
        """
        self.loader = loader
        self.config = config
        
        # 自动关联发现器
        self.fk_discoverer = AutoFKDiscoverer(loader)
        
        # 配置项
        self.auto_discover_cfg = config.get("auto_discover", {})
        self.auto_discover_enabled = self.auto_discover_cfg.get("enabled", True)
        self.max_fk_depth = self.auto_discover_cfg.get("max_fk_depth", 5)
        self.max_per_table = self.auto_discover_cfg.get("max_results_per_table", 200)
        
        self.output_cfg = config.get("output_settings", {})
        self.max_val_len = self.output_cfg.get("max_field_value_length", 500)
        self.max_fk_rows_per_link = self.output_cfg.get("max_fk_rows_per_link", 3)
        self.inline_fk_depth = self.output_cfg.get("inline_fk_depth", 3)
        self.detail_mode_default = self.output_cfg.get("detail_mode", "compact")
        
        self.enum_mappings = config.get("enum_mappings", {})
        self.table_display_fields = config.get("table_display_fields", {})
        self.field_meanings_cfg = config.get("field_meanings", {})
        
        # 缓存
        self._exact_rows_cache = {}
        self._fk_explain_cache = {}
        self._fk_explaining = set()
        
        # 构建含义到字段的反向映射
        self.meaning_to_keys: Dict[str, List[str]] = {}
        for k, v in self.field_meanings_cfg.items():
            vv = str(v).strip()
            if vv:
                self.meaning_to_keys.setdefault(vv, []).append(k)
    
    # ================================================================
    #  搜索
    # ================================================================

    def search(self, keyword: str) -> List[SearchResult]:
        """全局搜索关键词，返回所有匹配结果"""
        keyword = keyword.strip()
        if not keyword:
            return []

        results = []
        seen = set()
        for table_name, td in self.loader.tables.items():
            table_results = self._search_table(td, keyword)
            for r in table_results:
                key = (r.table_name, r.row_index)
                if key not in seen:
                    seen.add(key)
                    results.append(r)

        # ID语义扩展检索
        if self._looks_like_id(keyword):
            for r in self._expand_id_hits(keyword):
                key = (r.table_name, r.row_index)
                if key not in seen:
                    seen.add(key)
                    results.append(r)

        return results

    def _search_table(self, td: TableData, keyword: str) -> List[SearchResult]:
        """在单个表中搜索关键词"""
        results = []
        df = td.dataframe
        kw = keyword.lower() if not self.auto_discover_cfg.get("case_sensitive", False) else keyword

        for idx, row in df.iterrows():
            matched_cols = []
            for col in td.columns:
                cell = row[col]
                cell_str = str(cell).lower() if pd.notna(cell) else ""
                
                if not self.auto_discover_cfg.get("case_sensitive", False):
                    if kw in cell_str:
                        matched_cols.append(col)
                else:
                    if kw in str(cell):
                        matched_cols.append(col)

            if matched_cols:
                row_data = {}
                for col in td.columns:
                    val = row[col]
                    row_data[col] = val if pd.notna(val) else ""
                results.append(SearchResult(
                    table_name=td.table_name,
                    row_index=int(idx) + 1,
                    row_data=row_data,
                    matched_columns=matched_cols,
                ))
                if len(results) >= self.max_per_table:
                    break

        return results

    def search_all_exact(self, table_name: str, field_name: str, value: str) -> List[dict]:
        """精确查找某表某字段等于某值的所有行"""
        cache_key = (table_name, field_name, str(value).strip())
        if cache_key in self._exact_rows_cache:
            return self._exact_rows_cache[cache_key]
        
        td = self.loader.get_table(table_name)
        if td is None:
            return []
        
        if field_name not in td.columns:
            return []
        
        df = td.dataframe
        # 将字段值和查找值都转为字符串进行比较
        search_val = str(value).strip()
        mask = df[field_name].apply(lambda x: str(x).strip() == search_val if pd.notna(x) else False)
        match = df[mask]
        
        if match.empty:
            self._exact_rows_cache[cache_key] = []
            return []
        
        rows = []
        for _, row in match.iterrows():
            rows.append({col: (row[col] if pd.notna(row[col]) else "") for col in td.columns})
        
        self._exact_rows_cache[cache_key] = rows
        return rows

    # ================================================================
    #  自动关联发现
    # ================================================================
    
    def discover_and_resolve_fk(self, table_name: str, row_data: dict, 
                                 depth: int = 0, visited: Set[str] = None) -> List[FKLink]:
        """
        自动发现并解析一行数据中的所有外键关联
        
        返回: [FKLink, ...] 关联链路列表
        """
        if depth >= self.max_fk_depth:
            return []
        
        if visited is None:
            visited = set()
        
        results = []
        td = self.loader.get_table(table_name)
        if td is None:
            return results
        
        for field_name, field_value in row_data.items():
            if not field_value or str(field_value).strip() == "":
                continue
            
            # 自动发现外键关联
            fk_targets = self.fk_discoverer.discover_fk(field_name, str(field_value))
            
            if not fk_targets:
                continue
            
            for target_table, target_pk in fk_targets:
                # 提取可能的ID值
                fk_values = self._extract_id_tokens(field_value)
                if not fk_values:
                    fk_values = [str(field_value).strip()]
                
                for one_val in fk_values:
                    # 防止循环引用
                    link_id = f"{table_name}.{field_name}->{target_table}.{target_pk}={one_val}"
                    if link_id in visited:
                        continue
                    visited.add(link_id)
                    
                    # 在目标表中查找匹配行
                    target_rows = self.search_all_exact(target_table, target_pk, str(one_val))
                    
                    for target_row in target_rows:
                        link = FKLink(
                            source_table=table_name,
                            source_field=field_name,
                            source_value=one_val,
                            target_table=target_table,
                            target_field=target_pk,
                            target_row=target_row
                        )
                        # 递归子关联
                        link.children = self.discover_and_resolve_fk(
                            target_table, target_row, depth + 1, visited
                        )
                        results.append(link)
        
        # 特殊处理：Reward表中的Type和Id字段需要关联到具体资源表
        if table_name == "Reward":
            for i in range(1, 35):
                type_field = f"Type_{i}"
                id_field = f"Id_{i}"
                count_field = f"Count_{i}"
                
                if type_field in row_data and id_field in row_data:
                    type_val = str(row_data[type_field]).strip()
                    id_val = str(row_data[id_field]).strip()
                    
                    if type_val and id_val and type_val.lower() not in ("nan", "none", ""):
                        # 根据类型查找对应的表
                        type_table_map = {
                            "Resource": "Resource",
                            "Walnut": "Walnut", 
                            "Item": "Item",
                            "Weapon": "Weapon",
                            "Skill": "Skill",
                            "Buff": "Buff"
                        }
                        
                        for type_key, target_table in type_table_map.items():
                            if type_key.lower() in type_val.lower():
                                actual_table = self.fk_discoverer._find_table_by_name(target_table)
                                if actual_table:
                                    target_pk = self.fk_discoverer._table_pk_cache.get(actual_table, f"{target_table}Id")
                                    target_rows = self.search_all_exact(actual_table, target_pk, id_val)
                                    
                                    for target_row in target_rows:
                                        link = FKLink(
                                            source_table=table_name,
                                            source_field=f"{type_field}/{id_field}",
                                            source_value=f"{type_val}/{id_val}",
                                            target_table=actual_table,
                                            target_field=target_pk,
                                            target_row=target_row
                                        )
                                        link.children = self.discover_and_resolve_fk(
                                            actual_table, target_row, depth + 1, visited
                                        )
                                        results.append(link)
                                break
        
        return results
    
    # ================================================================
    #  辅助方法
    # ================================================================
    
    def _looks_like_id(self, text: str) -> bool:
        """判断文本是否像ID"""
        text = str(text).strip()
        if not text:
            return False
        return bool(re.fullmatch(r"[A-Za-z_]*\d+[A-Za-z_]*", text))
    
    def _extract_id_tokens(self, value) -> List[str]:
        """从单元格中提取可能的ID token"""
        if value is None:
            return []
        if isinstance(value, (int, float)) and pd.notna(value):
            return [str(int(value)) if float(value).is_integer() else str(value)]
        
        text = str(value).strip()
        if not text or text.lower() in ("nan", "none", "null"):
            return []
        
        text = text.strip("[](){}")
        parts = re.split(r"[,\|;/，、\s]+", text)
        tokens = []
        for p in parts:
            p = p.strip().strip("'").strip('"')
            if p:
                tokens.append(p)
        
        if not tokens:
            return [text]
        return tokens
    
    def get_meaning(self, field_name: str) -> str:
        """获取字段含义（优先从Excel元数据获取，其次从配置获取）"""
        # 先尝试从配置获取
        if field_name in self.field_meanings_cfg:
            return self.field_meanings_cfg[field_name]
        
        # 模糊匹配配置
        for cfg_key, meaning in self.field_meanings_cfg.items():
            if cfg_key.lower() == field_name.lower():
                return meaning
            if cfg_key in field_name or field_name in cfg_key:
                return meaning
        
        return ""
    
    def get_chinese_name(self, table_name: str, field_name: str) -> str:
        """获取字段的中文名称（从TableData元数据获取）"""
        td = self.loader.get_table(table_name)
        if td:
            return td.get_chinese_name(field_name)
        return ""
    
    def _map_enum_value(self, field_name: str, raw_val: str) -> str:
        """把枚举值映射为中文业务语义"""
        mp = self.enum_mappings.get(field_name, {})
        if not mp:
            return ""
        if raw_val in mp:
            return str(mp[raw_val])
        key = raw_val.strip().lower()
        for k, v in mp.items():
            if str(k).strip().lower() == key:
                return str(v)
        return ""
    
    def _is_truthy_text(self, text: str) -> Optional[bool]:
        x = text.strip().lower()
        if x in ("1", "true", "yes", "y"):
            return True
        if x in ("0", "false", "no", "n"):
            return False
        return None
    
    def _infer_time_unit(self, field_name: str, meaning: str) -> str:
        s = f"{field_name} {meaning}".lower()
        if "毫秒" in s or "ms" in s:
            return "ms"
        if "分钟" in s or "min" in s:
            return "min"
        if "小时" in s or "hour" in s:
            return "hour"
        if "秒" in s or s.endswith("cd") or "cooldown" in s:
            return "sec"
        return ""
    
    def _translate_structured_map(self, field_name: str, text: str, depth=0) -> str:
        """解析结构化配置串"""
        raw = str(text).strip()
        if not raw or raw.lower() in ("nan", "none", "null"):
            return ""
        
        pairs = re.findall(r"([A-Za-z0-9_]+)\s*:\s*\[([^\]]*)\]", raw)
        if not pairs:
            return ""
        
        parts = []
        for key, vals in pairs:
            vals = vals.strip()
            key_meaning = self.get_meaning(key)
            base = f"{key}=[{vals}]"
            if key_meaning:
                base = f"{key_meaning}：{base}"
            parts.append(base)
        
        return "；".join(parts)
    
    def _explain_field_value(self, table_name: str, field_name: str, value, depth=0) -> Tuple[str, str]:
        """
        返回: (展示值, 业务释义)
        - 从TableData元数据获取中文名称
        - 时间自动换算
        - 布尔值中文化
        """
        raw = "" if value is None else str(value)
        meaning = self.get_meaning(field_name)
        chinese_name = self.get_chinese_name(table_name, field_name)
        
        # 优先使用Excel中的中文名称
        if chinese_name:
            meaning = chinese_name if not meaning else f"{chinese_name}（{meaning}）"
        
        v = raw.strip()
        if not v or v.lower() in ("nan", "none", "null"):
            return raw, "空值（未配置）"
        
        bool_hint = self._is_truthy_text(v)
        if bool_hint is not None and (field_name.lower().startswith("is") or "是否" in meaning):
            return ("是" if bool_hint else "否",
                    f"布尔配置：{meaning} = {'开启' if bool_hint else '关闭'}")
        
        enum_text = self._map_enum_value(field_name, v)
        if enum_text:
            if meaning:
                return raw, f"枚举配置：{meaning} = {enum_text}"
            return raw, f"枚举配置：{enum_text}"
        
        # 结构化配置
        struct_text = self._translate_structured_map(field_name, v, depth=depth)
        if struct_text:
            if meaning:
                return raw, f"结构化配置：{meaning} = {struct_text}"
            return raw, f"结构化配置：{struct_text}"
        
        # 时间换算
        unit = self._infer_time_unit(field_name, meaning)
        if unit and re.fullmatch(r"-?\d+(\.\d+)?", v):
            num = float(v)
            if unit == "ms":
                explain = f"{meaning}：{num:.0f} 毫秒 (= {num / 1000:.2f} 秒)"
            elif unit == "sec":
                explain = f"{meaning}：{num:.0f} 秒 (= {num / 60:.2f} 分钟)"
            elif unit == "min":
                explain = f"{meaning}：{num:.0f} 分钟 (= {num * 60:.0f} 秒)"
            else:
                explain = f"{meaning}：{num:.2f} 小时 (= {num * 60:.0f} 分钟)"
            return raw, explain
        
        if re.fullmatch(r"-?\d+(\.\d+)?", v):
            if meaning:
                return raw, f"数值配置：{meaning} = {v}"
            return raw, f"数值={v}"
        
        if meaning:
            return raw, f"文本配置：{meaning} = {v}"
        return raw, ""
    
    def _pick_display_columns(self, table_name: str, row_data: dict) -> List[str]:
        """挑选关联显示字段"""
        picks = [c for c in self.table_display_fields.get(table_name, []) if c in row_data]
        if picks:
            return picks[:8]
        
        fallback = []
        for k, v in row_data.items():
            if not str(v).strip():
                continue
            lk = k.lower()
            if lk.endswith("id") or "name" in lk or "type" in lk or lk in ("count", "value"):
                fallback.append(k)
            if len(fallback) >= 8:
                break
        return fallback if fallback else list(row_data.keys())[:8]
    
    def _row_brief(self, table_name: str, row_data: dict, depth=0) -> str:
        """输出行摘要"""
        picks = self.table_display_fields.get(table_name, [])
        parts = []
        for f in picks:
            if f in row_data and str(row_data[f]).strip():
                display_val, _ = self._explain_field_value(table_name, f, row_data[f], depth=depth + 1)
                parts.append(f"{f}={display_val}")
        
        if not parts:
            fallback = []
            for k, v in row_data.items():
                if not str(v).strip():
                    continue
                if k.lower().endswith("id") or "name" in k.lower():
                    display_val, _ = self._explain_field_value(table_name, k, v, depth=depth + 1)
                    fallback.append(f"{k}={display_val}")
                if len(fallback) >= 3:
                    break
            parts = fallback
        
        return ", ".join(parts) if parts else "无可展示关键字段"
    
    def _expand_id_hits(self, keyword: str) -> List[SearchResult]:
        """按ID语义扩展检索"""
        out: List[SearchResult] = []
        kw = str(keyword).strip()
        
        for td in self.loader.tables.values():
            # 只扫描可能相关的列
            scan_cols = [c for c in td.columns if c.lower().endswith("id") or "id" in c.lower()]
            if not scan_cols:
                scan_cols = td.columns[:10]  # 限制扫描范围
            
            for idx, row in td.dataframe.iterrows():
                matched = []
                for col in scan_cols:
                    cell = row[col]
                    tokens = self._extract_id_tokens(cell)
                    if any(str(t).strip() == kw for t in tokens):
                        matched.append(col)
                
                if matched:
                    row_data = {col: (row[col] if pd.notna(row[col]) else "") for col in td.columns}
                    out.append(SearchResult(td.table_name, int(idx) + 1, row_data, matched))
        
        return out
    
    # ================================================================
    #  格式化输出
    # ================================================================

    def format_summary(self, keyword: str, results: List[SearchResult]) -> str:
        """一级输出：摘要视图"""
        if not results:
            return f"\n  [无结果] 未找到包含 '{keyword}' 的数据\n"

        lines = []
        lines.append(header(f"搜索关键词: '{keyword}'"))
        lines.append(f"  共找到 {len(results)} 条匹配记录\n")

        # 按表分组
        by_table: Dict[str, List[SearchResult]] = {}
        for r in results:
            by_table.setdefault(r.table_name, []).append(r)

        for tbl_name, tbl_results in by_table.items():
            sep = separator("─")
            lines.append(f"\n{sep}")
            lines.append(f"  [表] {tbl_name}  ({len(tbl_results)} 条匹配)")
            lines.append(f"{sep}")

            col_values: Dict[str, set] = {}
            col_rows: Dict[str, List[int]] = {}
            for res in tbl_results:
                for col in res.matched_columns:
                    col_values.setdefault(col, set()).add(str(res.row_data[col]))
                    col_rows.setdefault(col, []).append(res.row_index)

            for col_name, vals in col_values.items():
                chinese_name = self.get_chinese_name(tbl_name, col_name)
                meaning = self.get_meaning(col_name)
                display_name = chinese_name or meaning or col_name
                val_list = sorted(vals)[:5]
                val_str = ", ".join(truncate(v, 40) for v in val_list)
                if len(vals) > 5:
                    val_str += f"... (共{len(vals)}个不同值)"
                lines.append(f"  [{col_name}] ({display_name})")
                lines.append(f"    匹配值: {val_str}")
                lines.append(f"    匹配行数: {len(col_rows[col_name])} 行")

        lines.append(f"\n{separator('━')}")
        lines.append(f"  共 {len(results)} 条匹配，输入数字（如 1）查看详情")
        lines.append(f"  输入 all=重新显示摘要 | q=返回搜索\n")

        return "\n".join(lines)

    def format_detail(self, result: SearchResult, show_fk: bool = True,
                      detail_mode: str = None) -> str:
        """
        二级输出：单条完整详情 + 关联链路
        """
        mode = (detail_mode or self.detail_mode_default or "compact").lower()
        compact = mode != "full"
        lines = []
        
        # 获取表的中文名称（如果有）
        td = self.loader.get_table(result.table_name)
        table_chinese = ""
        if td and td.field_metas:
            # 从第一个字段的中文名推断表名
            pass
        
        lines.append(separator("═"))
        lines.append(f"  [详情] 表: {result.table_name}  |  行号: {result.row_index}  |  模式: {'简洁' if compact else '完整'}")
        lines.append(separator("─"))

        # 显示命中字段
        for col_name in result.matched_columns:
            marker = " <-- 命中"
            val = result.row_data[col_name]
            display_val, explain = self._explain_field_value(result.table_name, col_name, val)
            lines.append(f"  {fmt_field(col_name + marker, display_val, explain, self.max_val_len)}")

        # 显示整行所有字段
        lines.append(f"  ── 该行完整数据 ──")
        shown_cols = set(result.matched_columns)
        
        if compact:
            keep_cols = set(self._pick_display_columns(result.table_name, result.row_data))
            keep_cols.update(result.matched_columns)
            for col_name in result.row_data.keys():
                if col_name not in keep_cols or col_name in shown_cols:
                    continue
                col_val = result.row_data[col_name]
                display_val, explain = self._explain_field_value(result.table_name, col_name, col_val)
                lines.append(f"  {fmt_field(col_name, display_val, explain, self.max_val_len)}")
            omitted = len([c for c in result.row_data.keys() if c not in keep_cols and c not in shown_cols])
            if omitted > 0:
                lines.append(f"  ... 已省略 {omitted} 个非关键字段（切换完整模式可查看全部）")
        else:
            for col_name, col_val in result.row_data.items():
                if col_name in shown_cols:
                    continue
                display_val, explain = self._explain_field_value(result.table_name, col_name, col_val)
                lines.append(f"  {fmt_field(col_name, display_val, explain, self.max_val_len)}")

        # 外键关联查询（自动发现）
        if show_fk:
            fk_links = self.discover_and_resolve_fk(result.table_name, result.row_data)
            if fk_links:
                lines.append(f"  ── 关联数据（自动发现） ──")
                self._format_fk_links(lines, fk_links, indent=1, compact=compact)

        return "\n".join(lines)
    
    def _format_fk_links(self, lines: list, fk_links: List[FKLink], indent=1, compact=True):
        """格式化外键关联链路"""
        prefix = "  " * indent
        max_rows = self.max_fk_rows_per_link if compact else 5
        
        for link in fk_links[:max_rows]:
            # 获取源字段的中文名称
            source_chinese = self.get_chinese_name(link.source_table, link.source_field)
            source_display = source_chinese or link.source_field
            
            # 获取目标表的简要信息
            target_brief = self._row_brief(link.target_table, link.target_row)
            
            lines.append(f"{prefix}→ [{link.target_table}] {source_display}={link.source_value}")
            lines.append(f"{prefix}   └─ {target_brief}")
            
            # 显示目标表的关键字段
            show_cols = self._pick_display_columns(link.target_table, link.target_row)
            for col_name in show_cols[:5]:
                col_val = link.target_row.get(col_name, "")
                display_val, explain = self._explain_field_value(link.target_table, col_name, col_val)
                chinese = self.get_chinese_name(link.target_table, col_name)
                display_name = chinese or col_name
                lines.append(f"{prefix}      {display_name}: {display_val}")
            
            # 递归子关联
            if link.children:
                lines.append(f"{prefix}      └─ [下级关联]")
                self._format_fk_links(lines, link.children, indent + 2, compact)
        
        if len(fk_links) > max_rows:
            lines.append(f"{prefix}... 省略 {len(fk_links) - max_rows} 条关联")

    def format_results(self, keyword: str, results: List[SearchResult],
                       show_fk: bool = True) -> str:
        """（保留兼容）等价于 format_summary"""
        return self.format_summary(keyword, results)

    def list_tables_info(self) -> str:
        """列出所有已加载的表格信息"""
        lines = [header("已加载的表格列表")]
        total_rows = 0
        for name, td in self.loader.tables.items():
            total_rows += td.row_count
            pk_info = f"主键={td.primary_key}" if td.primary_key else ""
            lines.append(
                f"  • {name:<30}  {td.row_count:>6}行  {td.col_count}列  {pk_info}"
            )
        lines.append(f"\n  总计: {len(self.loader.tables)} 个表, {total_rows} 行数据")
        return "\n".join(lines)