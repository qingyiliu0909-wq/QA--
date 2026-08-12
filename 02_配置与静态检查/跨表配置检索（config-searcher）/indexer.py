#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
indexer.py - 游戏配表检索工具索引管理器
=========================================
核心功能：
  1. 目录索引校验 - 检查索引状态，判断是否需要重建/增量更新
  2. 全量建索引 - 遍历目录下所有配表文件，生成倒排索引
  3. 增量更新 - 只更新变更的文件，避免全量重扫
  4. 索引查询 - 直接从索引库中查询关键词，返回匹配结果

技术栈：
  - msgpack: 高效的二进制序列化格式，比 JSON 快 3-5 倍
  - zlib: 压缩索引数据，减小文件体积
  - hashlib: MD5 哈希计算，用于生成索引文件名

使用方法:
    from indexer import IndexManager, IndexMatch
    
    # 创建索引管理器
    manager = IndexManager("config_analysis/tool/.index")
    
    # 检查索引状态
    status = manager.check_index_status("D:/ExportDatas")
    
    # 全量建索引
    manager.build_full_index("D:/ExportDatas", loader)
    
    # 增量更新
    manager.update_incremental_index("D:/ExportDatas", loader)
    
    # 索引查询
    results = manager.search_index("80104")
"""

import os
import hashlib
import zlib
import msgpack
import logging
import pandas as pd
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple, Set
from enum import Enum
from datetime import datetime

# 配置日志
logger = logging.getLogger(__name__)

# ================================================================
#  数据结构定义
# ================================================================


class IndexStatus(Enum):
    """
    索引状态枚举
    
    属性:
        NONE: 无索引文件，需要全量建立
        VALID: 索引有效，可直接使用
        INCREMENTAL: 索引部分过期，需要增量更新
        FULL: 索引完全过期，需要全量重建
        CORRUPTED: 索引文件损坏，需要重建
    """
    NONE = "none"           # 无索引文件
    VALID = "valid"         # 索引有效
    INCREMENTAL = "incremental"  # 需要增量更新
    FULL = "full"           # 需要全量重建
    CORRUPTED = "corrupted" # 索引文件损坏


@dataclass
class IndexMatch:
    """
    索引匹配结果
    
    属性:
        table_name: 匹配的表名
        file_path: 文件相对路径（相对于工作区）
        row_index: 行号（从1开始）
        field_name: 字段名
        field_value: 字段值
    """
    table_name: str      # 匹配的表名
    file_path: str       # 文件相对路径
    row_index: int       # 行号（从1开始）
    field_name: str      # 字段名
    field_value: str     # 字段值


@dataclass
class FileIndexEntry:
    """
    文件索引条目 - 记录单个配表文件的索引元数据
    
    属性:
        file_path: 文件相对路径
        table_name: 表名（从文件名提取）
        mtime: 文件修改时间戳
        row_count: 数据行数
        col_count: 数据列数
        field_count: 字段数量（索引中的词条数）
    """
    file_path: str       # 文件相对路径
    table_name: str      # 表名
    mtime: float         # 文件修改时间戳
    row_count: int = 0   # 数据行数
    col_count: int = 0   # 数据列数
    field_count: int = 0 # 字段数量


@dataclass 
class InvertedIndexEntry:
    """
    倒排索引条目 - 记录关键词出现的位置
    
    属性:
        table_name: 表名
        row_index: 行号
        field_name: 字段名
    """
    table_name: str      # 表名
    row_index: int       # 行号
    field_name: str      # 字段名


# ================================================================
#  索引管理器核心类
# ================================================================


class IndexManager:
    """
    索引管理器 - 负责索引的创建、更新、查询、持久化
    
    这是整个索引系统的核心类，协调所有索引操作。
    
    属性:
        index_dir: 索引文件存储目录
        index_data: 当前加载的索引数据
        supported_extensions: 支持的文件扩展名列表
    """
    
    # 支持的文件扩展名
    SUPPORTED_EXTENSIONS = {'.xlsx', '.xls', '.csv', '.json', '.xml'}
    
    # 索引文件扩展名
    INDEX_EXTENSION = '.msgpack.zlib'
    
    # 索引版本号 - 用于兼容性检查
    INDEX_VERSION = "1.0"
    
    # 增量更新的变更阈值 - 超过此比例触发全量重建
    FULL_REBUILD_THRESHOLD = 0.5  # 50%
    
    def __init__(self, index_dir: str = ".index"):
        """
        初始化索引管理器
        
        参数:
            index_dir: 索引文件存储目录路径（相对或绝对路径）
                       默认值为 ".index"，会在当前工作目录创建
        
        示例:
            # 使用默认索引目录
            manager = IndexManager()
            
            # 指定自定义索引目录
            manager = IndexManager("D:/my_project/indexes")
        """
        # 规范化索引目录路径
        self.index_dir = os.path.normpath(index_dir)
        
        # 当前加载的索引数据
        self.index_data = None
        self.last_error = ""
        self.log_file_path = ""
        
        # 确保索引目录存在
        os.makedirs(self.index_dir, exist_ok=True)
        self._setup_logger()
        
        logger.info(f"索引管理器初始化完成，索引目录: {self.index_dir}")

    def _setup_logger(self):
        """为索引模块配置文件日志，便于排查构建失败"""
        try:
            self.log_file_path = os.path.join(self.index_dir, "indexer.log")
            logger.setLevel(logging.DEBUG)
            logger.propagate = False

            # 避免重复添加 handler
            file_handler_exists = False
            stream_handler_exists = False
            for h in logger.handlers:
                if isinstance(h, logging.FileHandler):
                    try:
                        if os.path.normpath(getattr(h, "baseFilename", "")) == os.path.normpath(self.log_file_path):
                            file_handler_exists = True
                    except Exception:
                        pass
                if isinstance(h, logging.StreamHandler):
                    stream_handler_exists = True

            formatter = logging.Formatter(
                "%(asctime)s | %(levelname)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )

            if not file_handler_exists:
                fh = logging.FileHandler(self.log_file_path, encoding="utf-8")
                fh.setLevel(logging.DEBUG)
                fh.setFormatter(formatter)
                logger.addHandler(fh)

            if not stream_handler_exists:
                sh = logging.StreamHandler()
                sh.setLevel(logging.INFO)
                sh.setFormatter(formatter)
                logger.addHandler(sh)
        except Exception:
            # 日志初始化失败不影响主流程
            pass
    
    # ================================================================
    #  1. 目录索引校验模块
    # ================================================================
    
    def _get_workspace_hash(self, workspace_path: str) -> str:
        """
        计算工作区目录路径的 MD5 哈希值
        
        用于生成唯一的索引文件名，确保不同目录对应不同的索引文件。
        
        参数:
            workspace_path: 工作区目录路径
        
        返回:
            str: MD5 哈希值（32位十六进制字符串）
        
        示例:
            >>> manager._get_workspace_hash("D:/ExportDatas")
            'a1b2c3d4e5f6789012345678901234ab'
        """
        # 规范化路径并转为小写（确保大小写不敏感）
        normalized_path = os.path.normpath(workspace_path).lower()
        return hashlib.md5(normalized_path.encode('utf-8')).hexdigest()
    
    def _get_index_file_path(self, workspace_path: str) -> str:
        """
        根据工作区路径获取索引文件的完整路径
        
        索引文件名格式: index_{目录哈希}.msgpack.zlib
        
        参数:
            workspace_path: 工作区目录路径
        
        返回:
            str: 索引文件的完整路径
        
        示例:
            >>> manager._get_index_file_path("D:/ExportDatas")
            'D:/OBT/.index/index_a1b2c3d4.msgpack.zlib'
        """
        hash_value = self._get_workspace_hash(workspace_path)
        filename = f"index_{hash_value}{self.INDEX_EXTENSION}"
        return os.path.join(self.index_dir, filename)
    
    def _get_current_files(self, workspace_path: str) -> Dict[str, float]:
        """
        扫描工作区目录，获取所有配表文件及其修改时间
        
        递归扫描目录，只收集支持的文件类型。
        
        参数:
            workspace_path: 工作区目录路径
        
        返回:
            Dict[str, float]: 文件相对路径 -> 修改时间戳 的映射
        
        示例:
            >>> manager._get_current_files("D:/ExportDatas")
            {
                'datas/Reward.xlsx': 1698765432.0,
                'datas/Condition.xlsx': 1698765433.0
            }
        """
        result = {}
        workspace_path = os.path.normpath(workspace_path)
        
        for root, dirs, files in os.walk(workspace_path):
            for filename in files:
                filepath = os.path.join(root, filename)
                ext = os.path.splitext(filename)[1].lower()
                
                if ext in self.SUPPORTED_EXTENSIONS:
                    # 计算相对路径
                    rel_path = os.path.relpath(filepath, workspace_path)
                    mtime = os.path.getmtime(filepath)
                    result[rel_path] = mtime
        
        return result
    
    def check_index_status(self, workspace_path: str) -> Tuple[IndexStatus, str]:
        """
        检查索引状态，判断是否需要重建/增量更新/可以直接使用
        
        这是索引校验的核心方法，会检查：
        1. 索引文件是否存在
        2. 索引文件是否损坏
        3. 索引文件对应的工作区路径是否匹配
        4. 文件变更情况，判断是否需要更新
        
        参数:
            workspace_path: 工作区目录路径
        
        返回:
            Tuple[IndexStatus, str]: (索引状态, 状态描述信息)
                - IndexStatus.NONE: 无索引文件
                - IndexStatus.VALID: 索引有效，可直接使用
                - IndexStatus.INCREMENTAL: 需要增量更新
                - IndexStatus.FULL: 需要全量重建
                - IndexStatus.CORRUPTED: 索引文件损坏
        
        示例:
            >>> status, msg = manager.check_index_status("D:/ExportDatas")
            >>> print(msg)
            '需要增量更新：3个文件变更'
        """
        workspace_path = os.path.normpath(workspace_path)
        index_file = self._get_index_file_path(workspace_path)
        
        # 检查索引文件是否存在
        if not os.path.exists(index_file):
            return IndexStatus.NONE, "索引文件不存在，需要全量建立"
        
        # 尝试加载索引文件
        try:
            self.index_data = self._load_index(index_file)
        except Exception as e:
            logger.error(f"加载索引文件失败: {e}")
            return IndexStatus.CORRUPTED, f"索引文件损坏: {e}"
        
        # 检查工作区路径是否匹配
        if self.index_data.get("workspace_path", "").lower() != workspace_path.lower():
            return IndexStatus.FULL, "索引文件对应的工作区路径不匹配，需要重建"
        
        # 检查索引版本
        if self.index_data.get("index_version") != self.INDEX_VERSION:
            return IndexStatus.FULL, f"索引版本不兼容 (当前{self.INDEX_VERSION}，文件{self.index_data.get('index_version')})，需要重建"
        
        # 获取当前文件状态
        current_files = self._get_current_files(workspace_path)
        file_index = self.index_data.get("file_index", {})
        
        # 统计变更情况
        added_files = set(current_files.keys()) - set(file_index.keys())      # 新增文件
        deleted_files = set(file_index.keys()) - set(current_files.keys())    # 删除文件
        modified_files = set()  # 修改文件
        
        for rel_path, mtime in current_files.items():
            if rel_path in file_index:
                stored_mtime = file_index[rel_path].get("mtime", 0)
                if abs(mtime - stored_mtime) > 1.0:  # 允许1秒误差
                    modified_files.add(rel_path)
        
        total_changes = len(added_files) + len(deleted_files) + len(modified_files)
        total_files = len(current_files)
        
        if total_files == 0:
            return IndexStatus.FULL, "工作区目录为空，无需索引"
        
        # 计算变更比例
        change_ratio = total_changes / total_files
        
        if total_changes == 0:
            return IndexStatus.VALID, "索引有效，所有文件未变更"
        elif change_ratio > self.FULL_REBUILD_THRESHOLD:
            return IndexStatus.FULL, f"变更文件过多 ({total_changes}/{total_files} = {change_ratio:.1%})，建议全量重建"
        else:
            change_details = []
            if added_files:
                change_details.append(f"新增{len(added_files)}个")
            if deleted_files:
                change_details.append(f"删除{len(deleted_files)}个")
            if modified_files:
                change_details.append(f"修改{len(modified_files)}个")
            return IndexStatus.INCREMENTAL, f"需要增量更新：{'、'.join(change_details)}"
    
    # ================================================================
    #  2. 全量建索引模块
    # ================================================================
    
    def _build_inverted_index(self, loader) -> Tuple[Dict[str, List[dict]], Dict[str, dict]]:
        """
        从已加载的表格数据构建倒排索引
        
        遍历所有表格的所有单元格，提取值作为关键词，
        记录每个关键词出现的位置（表名、行号、字段名）。
        
        参数:
            loader: TableLoader 实例，必须已加载所有表格
        
        返回:
            Tuple[Dict[str, List[dict]], Dict[str, dict]]: 
                (倒排索引, 文件索引)
                - 倒排索引: 关键词 -> [{"table": 表名, "row": 行号, "field": 字段名}, ...]
                - 文件索引: 文件路径 -> FileIndexEntry 的字典表示
        
        示例:
            >>> inverted_index, file_index = manager._build_inverted_index(loader)
            >>> print(inverted_index["80104"][:2])
            [
                {"table": "Condition", "row": 869, "field": "ConditionId"},
                {"table": "Condition", "row": 869, "field": "ConditionMap"}
            ]
        """
        inverted_index: Dict[str, List[dict]] = {}
        file_index: Dict[str, dict] = {}
        logger.info(f"开始构建倒排索引，表数量: {len(loader.tables)}")
        
        for table_name, td in loader.tables.items():
            logger.debug(f"处理表: {table_name}, 文件: {td.filepath}, 行数: {td.row_count}, 列数: {td.col_count}")
            rel_path = os.path.relpath(td.filepath, loader.workspace_path)
            
            # 记录文件索引
            file_index[rel_path] = {
                "file_path": rel_path,
                "table_name": table_name,
                "mtime": os.path.getmtime(td.filepath),
                "row_count": td.row_count,
                "col_count": td.col_count,
                "field_count": 0  # 稍后计算
            }
            
            # 遍历所有行和列
            field_count = 0
            for idx, row in td.dataframe.iterrows():
                row_num = int(idx) + 1  # 行号从1开始
                
                for col_name in td.columns:
                    cell_value = row[col_name]
                    
                    if pd.isna(cell_value):
                        continue
                    
                    value_str = str(cell_value).strip()
                    if not value_str or value_str.lower() in ("nan", "none", "null", ""):
                        continue
                    
                    # 提取关键词（支持复合值拆分）
                    keywords = self._extract_keywords(value_str)
                    
                    for keyword in keywords:
                        keyword_lower = keyword.lower()
                        
                        if keyword_lower not in inverted_index:
                            inverted_index[keyword_lower] = []
                        
                        inverted_index[keyword_lower].append({
                            "table": table_name,
                            "row": row_num,
                            "field": col_name
                        })
                        field_count += 1
            
            # 更新字段数量
            file_index[rel_path]["field_count"] = field_count
            logger.debug(f"表索引完成: {table_name}, 关键词条目: {field_count}")
        
        logger.info(f"倒排索引构建完成: 文件数={len(file_index)}, 关键词数={len(inverted_index)}")
        return inverted_index, file_index
    
    def _extract_keywords(self, value: str) -> List[str]:
        """
        从字段值中提取关键词
        
        支持多种格式的关键词提取：
        - 单个值: "80104" -> ["80104"]
        - 逗号分隔: "1,2,3" -> ["1", "2", "3"]
        - 结构化: "Type:[100],Count:[5]" -> ["type", "100", "count", "5"]
        - 混合分隔: "[1,2|3]" -> ["1", "2", "3"]
        
        参数:
            value: 字段值字符串
        
        返回:
            List[str]: 提取出的关键词列表（全部小写）
        
        示例:
            >>> manager._extract_keywords("QuestChain:[100405],PlayerLevelMin:[12]")
            ['questchain', '100405', 'playerlevelmin', '12']
        """
        keywords = set()
        
        # 移除方括号
        cleaned = value.replace('[', '').replace(']', '')
        
        # 按多种分隔符拆分
        import re
        parts = re.split(r'[,\|;/，、\s:]+', cleaned)
        
        for part in parts:
            part = part.strip().strip("'").strip('"')
            if part and len(part) >= 1:  # 至少1个字符
                keywords.add(part.lower())
        
        return list(keywords)
    
    def build_full_index(self, workspace_path: str, loader) -> bool:
        """
        全量建立索引 - 遍历目录下所有配表文件，生成倒排索引
        
        这是最耗时的操作，会：
        1. 使用 loader 加载所有表格
        2. 遍历每个表格的所有单元格
        3. 提取关键词并构建倒排索引
        4. 将索引数据序列化并压缩保存到文件
        
        参数:
            workspace_path: 工作区目录路径
            loader: TableLoader 实例（必须已加载所有表格）
        
        返回:
            bool: 是否成功
        
        示例:
            >>> success = manager.build_full_index("D:/ExportDatas", loader)
            >>> print(f"索引建立{'成功' if success else '失败'}")
            索引建立成功
        """
        workspace_path = os.path.normpath(workspace_path)
        index_file = self._get_index_file_path(workspace_path)
        
        logger.info(f"开始全量建立索引: {workspace_path}")
        start_time = datetime.now()
        
        try:
            self.last_error = ""
            logger.info(f"[FULL] 开始全量索引, workspace={workspace_path}")
            # 构建倒排索引
            inverted_index, file_index = self._build_inverted_index(loader)
            
            # 组装完整的索引数据
            self.index_data = {
                "index_version": self.INDEX_VERSION,
                "workspace_path": workspace_path,
                "created_at": start_time.isoformat(),
                "updated_at": datetime.now().isoformat(),
                "file_index": file_index,
                "inverted_index": inverted_index,
                "stats": {
                    "total_files": len(file_index),
                    "total_keywords": len(inverted_index),
                    "total_entries": sum(len(v) for v in inverted_index.values())
                }
            }
            
            # 保存索引文件
            self._save_index(index_file)
            
            elapsed = (datetime.now() - start_time).total_seconds()
            stats = self.index_data["stats"]
            logger.info(f"全量索引建立完成: {stats['total_files']}个文件, "
                       f"{stats['total_keywords']}个关键词, "
                       f"{stats['total_entries']}个条目, 耗时{elapsed:.1f}秒")
            
            return True
            
        except Exception as e:
            logger.exception(f"全量索引建立失败: {e}")
            self.last_error = str(e)
            self.index_data = None
            return False
    
    # ================================================================
    #  3. 增量更新模块
    # ================================================================
    
    def update_incremental_index(self, workspace_path: str, loader) -> bool:
        """
        增量更新索引 - 只更新变更的文件
        
        对比索引中记录的文件修改时间和当前文件状态，
        只对新增/修改/删除的文件进行索引更新，避免全量重扫。
        
        更新流程：
        1. 加载现有索引
        2. 扫描当前文件状态
        3. 识别变更文件（新增/修改/删除）
        4. 删除旧索引条目（针对修改和删除的文件）
        5. 为新增/修改的文件重新建立索引
        6. 保存更新后的索引
        
        参数:
            workspace_path: 工作区目录路径
            loader: TableLoader 实例（必须已加载变更的表格）
        
        返回:
            bool: 是否成功
        
        示例:
            >>> success = manager.update_incremental_index("D:/ExportDatas", loader)
            >>> print(f"增量更新{'成功' if success else '失败'}")
        """
        workspace_path = os.path.normpath(workspace_path)
        index_file = self._get_index_file_path(workspace_path)
        
        logger.info(f"开始增量更新索引: {workspace_path}")
        start_time = datetime.now()
        
        try:
            self.last_error = ""
            logger.info(f"[INCREMENTAL] 开始增量索引, workspace={workspace_path}")
            # 加载现有索引
            if self.index_data is None:
                self.index_data = self._load_index(index_file)
            
            file_index = self.index_data["file_index"]
            inverted_index = self.index_data["inverted_index"]
            current_files = self._get_current_files(workspace_path)
            
            # 识别变更文件
            added_files = set(current_files.keys()) - set(file_index.keys())
            deleted_files = set(file_index.keys()) - set(current_files.keys())
            modified_files = set()
            
            for rel_path, mtime in current_files.items():
                if rel_path in file_index:
                    stored_mtime = file_index[rel_path].get("mtime", 0)
                    if abs(mtime - stored_mtime) > 1.0:
                        modified_files.add(rel_path)
            
            logger.info(f"检测到变更: 新增{len(added_files)}个, "
                       f"修改{len(modified_files)}个, 删除{len(deleted_files)}个")
            
            # 1. 删除被删除文件的索引条目
            for rel_path in deleted_files:
                self._remove_file_index_entries(inverted_index, rel_path)
                del file_index[rel_path]
            
            # 2. 删除被修改文件的旧索引条目
            for rel_path in modified_files:
                self._remove_file_index_entries(inverted_index, rel_path)
            
            # 3. 为新增和修改的文件重新建立索引
            files_to_index = added_files | modified_files
            
            for rel_path in files_to_index:
                filepath = os.path.join(workspace_path, rel_path)
                table_name = os.path.splitext(os.path.basename(filepath))[0]
                
                # 获取表格数据
                td = loader.tables.get(table_name)
                if td is None:
                    logger.warning(f"找不到表格: {table_name}")
                    continue
                
                # 更新文件索引
                file_index[rel_path] = {
                    "file_path": rel_path,
                    "table_name": table_name,
                    "mtime": os.path.getmtime(filepath),
                    "row_count": td.row_count,
                    "col_count": td.col_count,
                    "field_count": 0
                }
                
                # 构建该文件的倒排索引
                field_count = 0
                for idx, row in td.dataframe.iterrows():
                    row_num = int(idx) + 1
                    
                    for col_name in td.columns:
                        cell_value = row[col_name]
                        
                        if pd.isna(cell_value):
                            continue
                        
                        value_str = str(cell_value).strip()
                        if not value_str or value_str.lower() in ("nan", "none", "null", ""):
                            continue
                        
                        keywords = self._extract_keywords(value_str)
                        
                        for keyword in keywords:
                            keyword_lower = keyword.lower()
                            
                            if keyword_lower not in inverted_index:
                                inverted_index[keyword_lower] = []
                            
                            inverted_index[keyword_lower].append({
                                "table": table_name,
                                "row": row_num,
                                "field": col_name
                            })
                            field_count += 1
                
                file_index[rel_path]["field_count"] = field_count
            
            # 清理空关键词条目
            inverted_index = {k: v for k, v in inverted_index.items() if v}
            
            # 更新索引元数据
            self.index_data["updated_at"] = datetime.now().isoformat()
            self.index_data["stats"] = {
                "total_files": len(file_index),
                "total_keywords": len(inverted_index),
                "total_entries": sum(len(v) for v in inverted_index.values())
            }
            
            # 保存索引文件
            self._save_index(index_file)
            
            elapsed = (datetime.now() - start_time).total_seconds()
            stats = self.index_data["stats"]
            logger.info(f"增量索引更新完成: {stats['total_files']}个文件, "
                       f"{stats['total_keywords']}个关键词, "
                       f"耗时{elapsed:.1f}秒")
            
            return True
            
        except Exception as e:
            logger.exception(f"增量索引更新失败: {e}")
            self.last_error = str(e)
            return False
    
    def _remove_file_index_entries(self, inverted_index: Dict[str, List[dict]], file_rel_path: str):
        """
        从倒排索引中删除指定文件的所有条目
        
        参数:
            inverted_index: 倒排索引字典
            file_rel_path: 文件相对路径（用于通过 file_index 查找表名）
        """
        # 获取表名
        table_name = None
        if self.index_data and "file_index" in self.index_data:
            file_entry = self.index_data["file_index"].get(file_rel_path)
            if file_entry:
                table_name = file_entry.get("table_name")
        
        if table_name is None:
            return
        
        # 遍历所有关键词，删除匹配表名的条目
        keys_to_delete = []
        for keyword, entries in inverted_index.items():
            inverted_index[keyword] = [e for e in entries if e.get("table") != table_name]
            if not inverted_index[keyword]:
                keys_to_delete.append(keyword)
        
        # 删除空关键词
        for key in keys_to_delete:
            del inverted_index[key]
    
    # ================================================================
    #  4. 索引查询模块
    # ================================================================
    
    def search_index(self, keyword: str) -> List[IndexMatch]:
        """
        从索引库中查询关键词，返回所有匹配结果
        
        这是搜索的核心方法，直接从倒排索引中查找关键词，
        避免了全量遍历配表文件，速度提升显著。
        
        参数:
            keyword: 搜索关键词（不区分大小写）
        
        返回:
            List[IndexMatch]: 匹配结果列表
                - 如果没有索引或关键词不存在，返回空列表
                - 每个 IndexMatch 包含: table_name, file_path, row_index, field_name, field_value
        
        示例:
            >>> results = manager.search_index("80104")
            >>> for r in results:
            ...     print(f"{r.table_name} 行{r.row_index} {r.field_name}")
            Condition 行869 ConditionId
            Condition 行869 ConditionMap
        """
        if self.index_data is None or keyword is None:
            return []
        
        keyword_lower = keyword.lower().strip()
        if not keyword_lower:
            return []
        
        inverted_index = self.index_data.get("inverted_index", {})
        file_index = self.index_data.get("file_index", {})
        
        # 直接查找关键词
        entries = inverted_index.get(keyword_lower, [])
        
        results = []
        for entry in entries:
            table_name = entry.get("table", "")
            row_index = entry.get("row", 0)
            field_name = entry.get("field", "")
            
            # 获取文件路径
            file_path = ""
            for rel_path, fentry in file_index.items():
                if fentry.get("table_name") == table_name:
                    file_path = rel_path
                    break
            
            results.append(IndexMatch(
                table_name=table_name,
                file_path=file_path,
                row_index=row_index,
                field_name=field_name,
                field_value=keyword  # 索引中不存储原始值，这里用关键词代替
            ))
        
        return results
    
    def search_index_fuzzy(self, keyword: str) -> List[IndexMatch]:
        """
        模糊搜索索引 - 支持部分匹配
        
        遍历所有关键词，查找包含指定字符串的关键词。
        比精确搜索慢，但能匹配更多结果。
        
        参数:
            keyword: 搜索关键词（部分匹配）
        
        返回:
            List[IndexMatch]: 匹配结果列表
        
        示例:
            >>> results = manager.search_index_fuzzy("8010")
            >>> # 会匹配 "80104", "80108", "8010" 等
        """
        if self.index_data is None or keyword is None:
            return []
        
        keyword_lower = keyword.lower().strip()
        if not keyword_lower:
            return []
        
        inverted_index = self.index_data.get("inverted_index", {})
        file_index = self.index_data.get("file_index", {})
        
        results = []
        seen = set()
        
        for stored_keyword, entries in inverted_index.items():
            if keyword_lower in stored_keyword:
                for entry in entries:
                    # 去重
                    key = (entry.get("table"), entry.get("row"), entry.get("field"))
                    if key in seen:
                        continue
                    seen.add(key)
                    
                    table_name = entry.get("table", "")
                    file_path = ""
                    for rel_path, fentry in file_index.items():
                        if fentry.get("table_name") == table_name:
                            file_path = rel_path
                            break
                    
                    results.append(IndexMatch(
                        table_name=table_name,
                        file_path=file_path,
                        row_index=entry.get("row", 0),
                        field_name=entry.get("field", ""),
                        field_value=stored_keyword
                    ))
        
        return results
    
    # ================================================================
    #  索引文件 I/O
    # ================================================================
    
    def _save_index(self, filepath: str) -> bool:
        """
        将索引数据序列化并压缩保存到文件
        
        使用 msgpack 进行二进制序列化，再用 zlib 压缩，
        可以有效减小索引文件体积（通常压缩比 3-5 倍）。
        
        参数:
            filepath: 索引文件保存路径
        
        返回:
            bool: 是否成功
        """
        try:
            # msgpack 序列化
            packed = msgpack.packb(self.index_data, use_bin_type=True)
            
            # zlib 压缩
            compressed = zlib.compress(packed, level=6)
            
            # 写入文件
            with open(filepath, 'wb') as f:
                f.write(compressed)
            
            file_size = os.path.getsize(filepath)
            logger.info(f"索引文件已保存: {filepath} ({file_size / 1024:.1f} KB)")
            return True
            
        except Exception as e:
            logger.error(f"保存索引文件失败: {e}")
            return False
    
    def _load_index(self, filepath: str) -> dict:
        """
        从文件加载并解压索引数据
        
        参数:
            filepath: 索引文件路径
        
        返回:
            dict: 索引数据字典
        
        抛出:
            Exception: 如果文件不存在或格式错误
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"索引文件不存在: {filepath}")
        
        try:
            # 读取文件
            with open(filepath, 'rb') as f:
                compressed = f.read()
            
            # zlib 解压
            packed = zlib.decompress(compressed)
            
            # msgpack 反序列化
            data = msgpack.unpackb(packed, raw=False)
            
            logger.info(f"索引文件已加载: {filepath}")
            return data
            
        except Exception as e:
            logger.error(f"加载索引文件失败: {e}")
            raise
    
    def delete_index(self, workspace_path: str) -> bool:
        """
        删除指定工作区的索引文件
        
        参数:
            workspace_path: 工作区目录路径
        
        返回:
            bool: 是否成功
        """
        index_file = self._get_index_file_path(workspace_path)
        
        try:
            if os.path.exists(index_file):
                os.remove(index_file)
                self.index_data = None
                logger.info(f"索引文件已删除: {index_file}")
            return True
        except Exception as e:
            logger.error(f"删除索引文件失败: {e}")
            return False
    
    def get_index_stats(self) -> Optional[dict]:
        """
        获取当前索引的统计信息
        
        返回:
            Optional[dict]: 统计信息字典，包括：
                - total_files: 索引文件数量
                - total_keywords: 关键词数量
                - total_entries: 总条目数
                - created_at: 创建时间
                - updated_at: 更新时间
            如果没有加载索引，返回 None
        """
        if self.index_data is None:
            return None
        
        return self.index_data.get("stats", {})
    
    def clear(self):
        """
        清空当前索引数据（不删除文件）
        """
        self.index_data = None


# ================================================================
#  工具函数
# ================================================================


def calculate_directory_hash(workspace_path: str) -> str:
    """
    计算目录路径的 MD5 哈希值（工具函数）
    
    参数:
        workspace_path: 目录路径
    
    返回:
        str: MD5 哈希值
    """
    normalized = os.path.normpath(workspace_path).lower()
    return hashlib.md5(normalized.encode('utf-8')).hexdigest()


def get_index_file_size(workspace_path: str, index_dir: str = ".index") -> Optional[int]:
    """
    获取指定工作区索引文件的大小
    
    参数:
        workspace_path: 工作区目录路径
        index_dir: 索引目录路径
    
    返回:
        Optional[int]: 索引文件大小（字节），如果不存在返回 None
    """
    manager = IndexManager(index_dir)
    index_file = manager._get_index_file_path(workspace_path)
    
    if os.path.exists(index_file):
        return os.path.getsize(index_file)
    return None