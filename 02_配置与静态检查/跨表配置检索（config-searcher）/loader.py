#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
loader.py - 通用表格加载器 v2.0
=================================
职责：递归扫描目录，自动识别所有 .xlsx/.xls/.csv 文件并加载到内存。
新增功能：
  1. 解析Excel第1行中文名称作为字段备注
  2. 自动识别每张表的主键（通常是第一个以Id结尾的字段）
  3. 存储完整的表头元数据（中文名、类型、英文名、可见性）
"""

import os
import pandas as pd
from typing import Dict, Optional, List

from utils import (
    is_excel_or_csv,
    extract_table_name,
    collect_files_recursive,
    resolve_path,
)


class FieldMeta:
    """单个字段的元数据"""
    
    def __init__(self, name: str, chinese_name: str = "", data_type: str = "", visibility: str = ""):
        self.name = name              # 英文字段名（如 DynQuestId）
        self.chinese_name = chinese_name  # 中文名称/备注（如 "事件ID"）
        self.data_type = data_type    # 数据类型（如 Int, String, List）
        self.visibility = visibility  # 可见性（如 server/client）
    
    def __repr__(self) -> str:
        return f"FieldMeta(name='{self.name}', chinese='{self.chinese_name}', type='{self.data_type}')"


class TableData:
    """单个表格数据的封装，表名从文件名自动识别"""

    def __init__(self, filepath: str, table_name: str, dataframe: pd.DataFrame, 
                 field_metas: List[FieldMeta] = None, primary_key: str = None):
        self.filepath = resolve_path(filepath)
        self.table_name = table_name
        self.dataframe = dataframe
        self.columns = list(dataframe.columns)
        self.row_count = len(dataframe)
        self.col_count = len(self.columns)
        self.field_metas = field_metas or []  # 字段元数据列表
        self.primary_key = primary_key        # 主键字段名
        
        # 构建字段名到元数据的映射
        self.meta_map: Dict[str, FieldMeta] = {}
        for meta in self.field_metas:
            self.meta_map[meta.name] = meta
    
    def get_chinese_name(self, field_name: str) -> str:
        """获取字段的中文名称/备注"""
        if field_name in self.meta_map:
            return self.meta_map[field_name].chinese_name
        return ""
    
    def __repr__(self) -> str:
        return (f"TableData(name='{self.table_name}', "
                f"rows={self.row_count}, cols={self.col_count}, "
                f"pk='{self.primary_key}')")


class TableLoader:
    """
    通用表格加载器 v2.0
    用法:
        loader = TableLoader("ExportDatas/datas")
        loader.scan()
        loader.load_all()
        loader.tables  -> {表名: TableData}
    """

    def __init__(self, workspace_path: str):
        self.workspace_path = resolve_path(workspace_path)
        self.tables: Dict[str, TableData] = {}
        self.valid_files: list = []
        self.errors: list = []

    def scan(self) -> list:
        """扫描目录，收集所有 Excel/CSV 文件"""
        print(f"\n[扫描] 工作区: {self.workspace_path}")
        all_files = collect_files_recursive(self.workspace_path)
        self.valid_files = [
            f for f in all_files if is_excel_or_csv(f)
            and not os.path.basename(f).startswith('~$')
        ]
        print(f"  找到 {len(self.valid_files)} 个表格文件")
        return self.valid_files

    def load_all(self) -> Dict[str, TableData]:
        """加载所有表格文件到内存"""
        if not self.valid_files:
            self.scan()

        success = fail = 0
        for filepath in self.valid_files:
            try:
                name = extract_table_name(filepath)
                df, field_metas = self._read_file_with_meta(filepath)
                if df is None:
                    fail += 1
                    continue
                name = self._dedup_name(name)
                # 自动识别主键
                primary_key = self._find_primary_key(df.columns, field_metas)
                self.tables[name] = TableData(filepath, name, df, field_metas, primary_key)
                if len(self.valid_files) <= 40 or success < 5 or success % 25 == 0:
                    print(f"  [OK] {name}  ({df.shape[0]}行, {df.shape[1]}列, 主键={primary_key})")
                success += 1
            except Exception as e:
                self.errors.append(f"{filepath}: {e}")
                fail += 1

        total_rows = sum(t.row_count for t in self.tables.values())
        print(f"\n[加载完成] 成功: {success}, 失败: {fail}, 数据行数: {total_rows}")
        return self.tables

    def _read_file_with_meta(self, filepath: str) -> tuple:
        """
        读取文件并返回 (dataframe, field_metas)
        field_metas: 字段元数据列表，包含中文名、类型、英文名、可见性
        """
        ext = os.path.splitext(filepath)[1].lower()

        # 跳过临时文件
        if os.path.basename(filepath).startswith('~$'):
            return None, []

        if ext == '.csv':
            return self._read_csv_with_meta(filepath)
        elif ext in ('.xlsx', '.xls'):
            try:
                return self._read_excel_with_meta(filepath, ext)
            except Exception as e:
                print(f"  [ERR] 读取 Excel 失败 {os.path.basename(filepath)}: {e}")
                return None, []
        return None, []

    def _read_excel_with_meta(self, filepath: str, ext: str) -> tuple:
        """
        读取Excel文件，解析完整的表头元数据
        
        Excel结构（从实际文件分析）：
        第0行：可能是Sheet名称行（如 "--- Sheet: 动态事件表|DynQuest ---"）
        第1行：中文名称（如"事件ID"、"事件名称"）
        第2行：数据类型（如 Int、String、List）
        第3行：英文字段名（如 DynQuestId、DynName）
        第4行：可见性标记（如 server/client）
        第5行+：实际数据
        """
        raw = pd.read_excel(filepath, engine='openpyxl' if ext == '.xlsx' else None,
                            header=None)
        
        if raw.empty or raw.shape[0] < 4:
            return raw, []
        
        # 检查第0行是否是Sheet名称行
        row0_str = str(raw.iloc[0].iloc[0]) if raw.shape[1] > 0 else ""
        data_start_row = 0
        
        if row0_str.startswith('---'):
            # 第0行是Sheet名称，从第1行开始解析
            data_start_row = 1
        
        # 解析表头元数据
        header_row_idx = data_start_row  # 中文名称行
        type_row_idx = data_start_row + 1  # 数据类型行
        field_row_idx = data_start_row + 2  # 英文字段名行
        visibility_row_idx = data_start_row + 3  # 可见性行
        data_row_idx = data_start_row + 4  # 数据起始行
        
        # 确保有足够的行
        if raw.shape[0] <= data_row_idx:
            return raw, []
        
        # 提取元数据
        chinese_names = raw.iloc[header_row_idx].tolist()
        data_types = raw.iloc[type_row_idx].tolist()
        field_names = raw.iloc[field_row_idx].tolist()
        visibilities = raw.iloc[visibility_row_idx].tolist()
        
        # 构建字段元数据列表
        field_metas = []
        valid_columns = []
        
        for i, field_name in enumerate(field_names):
            field_name = str(field_name).strip() if pd.notna(field_name) else ""
            if not field_name or field_name.lower() in ('nan', 'none', ''):
                field_name = f"col_{i}"
            
            chinese_name = str(chinese_names[i]).strip() if i < len(chinese_names) and pd.notna(chinese_names[i]) else ""
            data_type = str(data_types[i]).strip() if i < len(data_types) and pd.notna(data_types[i]) else ""
            visibility = str(visibilities[i]).strip() if i < len(visibilities) and pd.notna(visibilities[i]) else ""
            
            field_metas.append(FieldMeta(
                name=field_name,
                chinese_name=chinese_name,
                data_type=data_type,
                visibility=visibility
            ))
            valid_columns.append(field_name)
        
        # 提取数据
        data = raw.iloc[data_row_idx:].copy()
        data.columns = valid_columns
        data = data.reset_index(drop=True)
        
        return self._clean_df(data), field_metas

    def _read_csv_with_meta(self, filepath: str) -> tuple:
        """读取CSV文件（CSV通常没有完整的元数据行，使用第一行作为列名）"""
        for enc in ['utf-8-sig', 'utf-8', 'gbk', 'gb18030', 'latin1']:
            try:
                df = pd.read_csv(filepath, encoding=enc)
                # CSV没有元数据行，创建空的field_metas
                field_metas = [FieldMeta(name=str(col)) for col in df.columns]
                return self._clean_df(df), field_metas
            except (UnicodeDecodeError, Exception):
                continue
        print(f"  [ERR] CSV 解码失败 {os.path.basename(filepath)}")
        return None, []

    def _find_primary_key(self, columns: list, field_metas: list = None) -> str:
        """
        自动识别表的主键
        规则：
        1. 优先查找 {TableName}Id 格式的字段
        2. 其次查找以 Id 结尾的字段
        3. 最后返回第一个字段
        """
        # 从表名推断主键名
        table_name = getattr(self, '_current_table_name', '')
        expected_pk = f"{table_name}Id"
        
        if expected_pk in columns:
            return expected_pk
        
        # 查找以Id结尾的字段
        for col in columns:
            if col.endswith('Id'):
                return col
        
        # 查找包含Id的字段
        for col in columns:
            if 'Id' in col:
                return col
        
        # 默认返回第一个字段
        return columns[0] if columns else ""

    def _clean_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """清洗DataFrame"""
        # 兼容不同版本的pandas
        if hasattr(df.columns, 'dtype') and df.columns.dtype == 'object':
            df.columns = df.columns.str.strip()
        elif hasattr(df.columns, 'inferred_type') and df.columns.inferred_type == 'string':
            df.columns = [c.strip() if isinstance(c, str) else c for c in df.columns]
        
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].apply(
                    lambda x: x.strip() if isinstance(x, str) else x
                )
        return df

    def _dedup_name(self, name: str) -> str:
        """表名去重"""
        if name not in self.tables:
            return name
        i = 1
        while f"{name}_{i}" in self.tables:
            i += 1
        return f"{name}_{i}"

    def get_table(self, name: str) -> Optional[TableData]:
        """获取指定表"""
        return self.tables.get(name)

    def list_table_names(self) -> list:
        """列出所有表名"""
        return list(self.tables.keys())

    def find_tables(self, pattern: str) -> list:
        """模糊匹配表名（不区分大小写）"""
        p = pattern.lower()
        return [n for n in self.tables if p in n.lower()]

    def get_by_key(self, table_name: str, key_field: str, key_value: str) -> Optional[dict]:
        """
        根据某字段精确查找一行数据
        返回: {字段名: 值} 或 None
        """
        td = self.tables.get(table_name)
        if td is None:
            return None
        if key_field not in td.columns:
            return None
        df = td.dataframe
        mask = df[key_field].astype(str).str.strip() == str(key_value).strip()
        match = df[mask]
        if match.empty:
            return None
        row = match.iloc[0]
        return {col: (row[col] if pd.notna(row[col]) else "") for col in td.columns}