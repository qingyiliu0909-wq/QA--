#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
gui_app.py - 游戏配表检索工具 Windows桌面端GUI版
=================================================
基于Tkinter的图形界面工具，支持：
  1. 双击.exe直接运行（不弹出终端）
  2. 手动选择游戏项目根目录
  3. 搜索配表中的ID/关键词
  4. 自动跨表翻译关联ID的中文含义
  5. 时间字段换算、布尔值转中文
  6. 结果分层展示
  7. 索引管理（建立/刷新/删除/状态显示）

技术栈：Python + Tkinter
打包：PyInstaller -> 单文件.exe
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

# 确保当前目录在Python路径中（用于导入同目录下的模块）
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from loader import TableLoader
from searcher import GlobalSearcher, SearchResult
from indexer import IndexManager, IndexStatus
from utils import validate_workspace, load_json

# ========== [新增] 导入详情表格渲染器 ==========
# DetailTableFrame 用于将单条搜索结果的字段详情
# 以「字段名(固定宽)|值(自适应)|含义(自适应)」三列表格形式展示
from detail_renderer import DetailTableFrame


class GameConfigSearcherApp:
    """
    游戏配表检索工具 - 主GUI应用类
    
    界面布局（从上到下）：
    ┌─────────────────────────────────┐
    │  目录选择区                     │
    │  [路径显示]    [选择目录按钮]   │
    ├─────────────────────────────────┤
    │  索引管理区                     │
    │  [状态显示] [建立][刷新][删除]  │
    │  [进度条]                       │
    ├─────────────────────────────────┤
    │  搜索区                         │
    │  [输入框]      [搜索按钮]       │
    ├─────────────────────────────────┤
    │  状态栏                         │
    │  [加载状态/搜索状态提示]        │
    ├─────────────────────────────────┤
    │  结果展示区                     │
    │  ┌───────────────────────────┐  │
    │  │                           │  │
    │  │    搜索结果（只读）        │  │
    │  │                           │  │
    │  └───────────────────────────┘  │
    └─────────────────────────────────┘
    """

    def __init__(self, root):
        """初始化GUI窗口"""
        self.root = root
        self.root.title("游戏配表检索工具 v1.1")
        self.root.geometry("900x750")
        self.root.minsize(700, 550)

        # 核心数据
        self.workspace_path = ""       # 当前选中的项目根目录
        self.searcher = None           # 全局搜索器实例
        self.loader = None             # 表格加载器实例
        self.last_results = []         # 上次搜索结果
        self.show_fk = True            # 是否显示外键关联
        self.detail_mode = "compact"   # 详情模式: compact/full
        self.show_chinese_names = True  # 是否显示中文名称备注

        # 索引相关
        self.index_manager = None      # IndexManager实例
        self.index_status = IndexStatus.NONE  # 当前索引状态
        self.index_building = False    # 是否正在建立索引
        self.index_progress_cancel = False  # 取消索引建立标志
        self.index_dir = self._get_persistent_index_dir()  # 固定索引目录（源码/EXE统一）

        # 加载配置
        self.config = self._load_config()

        # 构建界面
        self._build_ui()

        # 绑定回车键搜索
        self.root.bind('<Return>', self._on_enter_search)

    def _load_config(self) -> dict:
        """加载config.json配置文件"""
        cfg_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "config.json"
        )
        cfg = load_json(cfg_path)
        if not cfg:
            cfg = {
                "field_meanings": {},
                "foreign_keys": {},
                "search_settings": {},
                "output_settings": {}
            }
        return cfg

    def _get_persistent_index_dir(self) -> str:
        """
        获取持久化索引目录。
        优先放在 dist 目录（exe 同目录），便于打包后统一收集日志与索引：
        - 打包 exe 运行：<exe_dir>/.index  -> 通常是 config_analysis/tool/dist/.index
        - 源码运行：若存在 config_analysis/tool/dist，也写入 dist/.index；否则写入脚本目录/.index
        """
        # 1) 打包后的 exe：索引/日志放 exe 同目录
        if getattr(sys, "frozen", False):
            base_dir = os.path.dirname(sys.executable)
            return os.path.join(base_dir, ".index")

        # 2) 源码运行：优先放在 tool/dist 目录，便于与 exe 行为一致
        tool_dir = os.path.dirname(os.path.abspath(__file__))
        dist_dir = os.path.join(tool_dir, "dist")
        if os.path.isdir(dist_dir):
            return os.path.join(dist_dir, ".index")

        # 3) 兜底：脚本目录
        return os.path.join(tool_dir, ".index")

    def _build_ui(self):
        """构建全部GUI界面组件"""
        # 设置整体padding
        pad = {'padx': 8, 'pady': 5}

        # ===================== 顶部：目录选择区 =====================
        frame_top = ttk.LabelFrame(self.root, text="  项目目录选择  ", padding=8)
        self.frame_top = frame_top
        frame_top.pack(fill=tk.X, **pad)

        # 路径显示（只读）
        self.path_var = tk.StringVar(value="尚未选择项目目录，请点击右侧按钮选择...")
        self.path_entry = ttk.Entry(frame_top, textvariable=self.path_var, state='readonly')
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        # 选择目录按钮
        btn_browse = ttk.Button(frame_top, text="📁 选择目录", command=self._browse_directory)
        btn_browse.pack(side=tk.RIGHT)

        # ===================== 索引管理区 =====================
        self._build_index_frame()

        # ===================== 中间：搜索区 =====================
        frame_search = ttk.LabelFrame(self.root, text="  搜索配置  ", padding=8)
        self.frame_search = frame_search
        frame_search.pack(fill=tk.X, **pad)

        # 搜索输入框（一级检索）
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(frame_search, textvariable=self.search_var, font=("", 11))
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        self.search_entry.config(state='disabled')  # 初始禁用，选择目录后才启用

        # 搜索按钮
        btn_search = ttk.Button(frame_search, text="🔍 搜索", command=self._do_search)
        btn_search.pack(side=tk.RIGHT)
        btn_search.config(state='disabled')  # 初始禁用
        self.btn_search = btn_search

        # 二级检索区：输入编号查看详情
        frame_detail = ttk.Frame(self.root)
        self.frame_detail = frame_detail
        frame_detail.pack(fill=tk.X, **pad)
        ttk.Label(frame_detail, text="二级检索（输入结果编号）:").pack(side=tk.LEFT)
        self.detail_var = tk.StringVar()
        self.detail_entry = ttk.Entry(frame_detail, textvariable=self.detail_var, width=10)
        self.detail_entry.pack(side=tk.LEFT, padx=(6, 8))
        self.detail_entry.config(state='disabled')
        self.btn_detail = ttk.Button(frame_detail, text="查看详情", command=self._show_detail_by_index)
        self.btn_detail.pack(side=tk.LEFT)
        self.btn_detail.config(state='disabled')

        # 右侧按钮区：把索引按钮 + 常用按钮都放到“查看详情”右边，保证永远可见
        right_bar = ttk.Frame(frame_detail)
        right_bar.pack(side=tk.RIGHT)

        # 复制/清空（原底部按钮）
        btn_clear = ttk.Button(right_bar, text="清空结果", command=self._clear_result)
        btn_clear.pack(side=tk.RIGHT, padx=(5, 0))
        btn_copy = ttk.Button(right_bar, text="复制结果", command=self._copy_result)
        btn_copy.pack(side=tk.RIGHT, padx=(0, 5))

        # 显示模式开关（原底部开关）
        self.compact_var = tk.BooleanVar(value=True)
        chk_compact = ttk.Checkbutton(
            right_bar, text="简洁模式",
            variable=self.compact_var, command=self._toggle_detail_mode
        )
        chk_compact.pack(side=tk.RIGHT, padx=(10, 0))

        self.fk_var = tk.BooleanVar(value=True)
        chk_fk = ttk.Checkbutton(
            right_bar, text="显示关联数据",
            variable=self.fk_var, command=self._toggle_fk
        )
        chk_fk.pack(side=tk.RIGHT, padx=(10, 0))

        # 索引按钮（原“索引管理区”里的 3 个按钮）
        # 直接复用同一套回调与状态更新逻辑（self.btn_build_index 等）
        self.btn_delete_index = ttk.Button(right_bar, text="🗑️ 删除索引", command=self._delete_index, state='disabled')
        self.btn_delete_index.pack(side=tk.RIGHT, padx=(10, 0))
        self.btn_refresh_index = ttk.Button(right_bar, text="🔄 刷新索引", command=self._refresh_index, state='disabled')
        self.btn_refresh_index.pack(side=tk.RIGHT, padx=(5, 0))
        self.btn_build_index = ttk.Button(right_bar, text="🔨 建立索引", command=self._build_index, state='disabled')
        self.btn_build_index.pack(side=tk.RIGHT, padx=(5, 0))

        # ===================== 状态栏 =====================
        frame_status = ttk.Frame(self.root)
        self.frame_status = frame_status
        frame_status.pack(fill=tk.X, **pad)

        self.status_var = tk.StringVar(value="就绪 - 请先选择游戏项目根目录")
        lbl_status = ttk.Label(frame_status, textvariable=self.status_var, font=("", 9))
        lbl_status.pack(side=tk.LEFT)

        # 进度条（加载表格时显示）
        self.progress = ttk.Progressbar(frame_status, mode='indeterminate')
        self.progress.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(8, 0))

        # ===================== 底部：结果展示区 =====================
        # 布局说明：
        # ┌─ frame_result (LabelFrame) ──────────────────────┐
        # │  ┌─ 上部：搜索摘要列表 ──────────────────┐       │
        # │  │  result_text (ScrolledText, 只读)     │       │
        # │  │  显示一级搜索结果的编号列表和分组摘要    │       │
        # │  │  【优化】初始高度占窗口25%，最小高度12行 │       │
        # │  └────────────────────────────────────────┘       │
        # │  ┌─ 下部：详情表格 ──────────────────────┐       │
        # │  │  detail_table (DetailTableFrame)      │       │
        # │  │  以「字段|值|含义」三列表格展示单条详情 │       │
        # │  └────────────────────────────────────────┘       │
        # └───────────────────────────────────────────────────┘
        # 【优化】使用 ttk.PanedWindow 分割上下两部分，用户可拖动调整比例
        # 【优化】列表控件优先分配空间，详情表格按需显示
        
        frame_result = ttk.LabelFrame(self.root, text="  搜索结果  ", padding=8)
        self.frame_result = frame_result
        frame_result.pack(side=tk.TOP, fill=tk.BOTH, expand=True, **pad)
        
        # 【新增】创建 PanedWindow 用于分割列表和详情表格
        # 注意：ttk.PanedWindow 的 add() 不支持 minsize，会导致打包后崩溃（unknown option "-minsize"）
        # 这里使用 tk.PanedWindow（原生）以支持 minsize，并保持拖拽分割能力。
        self.result_paned = tk.PanedWindow(
            frame_result,
            orient=tk.VERTICAL,
            sashrelief=tk.RAISED,
            bg="#1e1e1e",
        )
        self.result_paned.pack(fill=tk.BOTH, expand=True)

        # ---- 上部：搜索摘要文本（只读） ----
        # 【优化】height 从 10 增加到 18，确保默认能显示前 5-8 条结果
        # 按窗口高度 750px 计算，25% 约 187px，Consolas 10号字体每行约 16px，约 11-12 行
        # 考虑到 LabelFrame 的 padding 和标题栏，设置 height=18 较为合理
        self.result_text = scrolledtext.ScrolledText(
            self.result_paned,   # 【修改】父容器改为 PanedWindow
            wrap=tk.WORD,
            state='disabled',
            font=("Consolas", 10),
            bg="#1e1e1e",       # 深色背景
            fg="#d4d4d4",       # 浅色文字
            insertbackground="#d4d4d4",
            selectbackground="#264f78",
            height=10,          # 默认更小，给表格让空间，避免挤出底部按钮
        )
        # 【修改】使用 PanedWindow.add() 添加控件，设置 minsize 确保最小高度
        # minsize=150 表示用户再怎么缩小窗口，列表区域也不会低于 150px（约 9 行）
        # 降低最小高度，避免窗口不够时把底部按钮挤出视区
        self.result_paned.add(self.result_text, minsize=80)

        # ---- 下部：详情表格（用 Treeview 实现三列对齐） ----
        # DetailTableFrame 封装了 ttk.Treeview + 滚动条，
        # 支持三列「字段(固定宽150px)|值(自适应)|含义(自适应)」，
        # 命中行高亮、关联数据展开/折叠等功能。
        self.detail_table = DetailTableFrame(self.result_paned)  # 【修改】父容器改为 PanedWindow
        # 【优化】一开始就加入 PanedWindow，避免“数据太多但表格区域太小”的情况；
        # 通过 sashpos 控制默认比例：上部摘要小、下部表格大。
        self.result_paned.add(self.detail_table, minsize=120)
        self.root.after(0, self._init_result_panes)

        # 说明：原来的底部按钮栏已合并到“二级检索”右侧按钮区，避免被内容区挤没

    def _init_result_panes(self):
        """初始化 PanedWindow 默认比例：摘要区小、详情表格大"""
        try:
            h = max(400, int(self.root.winfo_height() or 750))
            top_h = max(120, int(h * 0.25))
            self.result_paned.sashpos(0, top_h)
        except Exception:
            pass

    def _build_index_frame(self):
        """构建索引管理区域"""
        self.index_frame = ttk.LabelFrame(self.root, text="  📊 索引管理  ", padding=8)
        # 初始不pack，选择目录后才显示
        self.index_frame.pack_forget()

        # 状态显示行
        status_row = ttk.Frame(self.index_frame)
        status_row.pack(fill=tk.X)

        # 索引状态图标
        self.index_icon_var = tk.StringVar(value="⚪")
        self.index_icon_label = ttk.Label(status_row, textvariable=self.index_icon_var, font=("", 12))
        self.index_icon_label.pack(side=tk.LEFT)

        # 索引状态文字
        self.index_status_var = tk.StringVar(value="尚未选择目录")
        self.index_status_label = ttk.Label(status_row, textvariable=self.index_status_var, font=("", 9))
        self.index_status_label.pack(side=tk.LEFT, padx=(5, 0))

        # 索引统计信息
        self.index_stats_var = tk.StringVar(value="")
        self.index_stats_label = ttk.Label(status_row, textvariable=self.index_stats_var, font=("", 8), foreground="gray")
        self.index_stats_label.pack(side=tk.RIGHT)

        # 按钮行
        btn_row = ttk.Frame(self.index_frame)
        btn_row.pack(fill=tk.X, pady=(5, 0))

        self.btn_build_index = ttk.Button(btn_row, text="🔨 建立索引", command=self._build_index, state='disabled')
        self.btn_build_index.pack(side=tk.LEFT)

        self.btn_refresh_index = ttk.Button(btn_row, text="🔄 刷新索引", command=self._refresh_index, state='disabled')
        self.btn_refresh_index.pack(side=tk.LEFT, padx=(5, 0))

        self.btn_delete_index = ttk.Button(btn_row, text="🗑️ 删除索引", command=self._delete_index, state='disabled')
        self.btn_delete_index.pack(side=tk.LEFT, padx=(5, 0))

        # 进度条（初始隐藏）
        self.index_progressbar = ttk.Progressbar(self.index_frame, mode='determinate', maximum=100)
        self.index_progressbar.pack(fill=tk.X, pady=(5, 0))
        self.index_progressbar.pack_forget()

    def _update_index_ui(self, status: IndexStatus, message: str):
        """统一更新索引UI显示"""
        self.index_status_var.set(message)
        self.index_status = status

        # 状态映射: (图标, 颜色, 建立按钮, 刷新按钮, 删除按钮)
        state_map = {
            IndexStatus.NONE: ("⚪", "gray", "normal", "disabled", "disabled"),
            IndexStatus.VALID: ("✅", "green", "disabled", "normal", "normal"),
            IndexStatus.INCREMENTAL: ("⚠️", "orange", "normal", "normal", "normal"),
            IndexStatus.FULL: ("🔴", "red", "normal", "normal", "normal"),
            IndexStatus.CORRUPTED: ("❌", "red", "normal", "disabled", "normal"),
        }

        icon, color, build_state, refresh_state, delete_state = state_map.get(
            status, ("⚪", "gray", "disabled", "disabled", "disabled")
        )

        self.index_icon_var.set(icon)
        self.index_status_label.configure(foreground=color)
        self.btn_build_index.config(state=build_state)
        self.btn_refresh_index.config(state=refresh_state)
        self.btn_delete_index.config(state=delete_state)

    def _update_index_stats(self):
        """更新索引统计信息显示"""
        if self.index_manager and self.index_manager.index_data:
            stats = self.index_manager.get_index_stats()
            if stats:
                text = f"文件: {stats.get('total_files', 0)} | 关键词: {stats.get('total_keywords', 0)} | 条目: {stats.get('total_entries', 0)}"
                self.index_stats_var.set(text)
            else:
                self.index_stats_var.set("")
        else:
            self.index_stats_var.set("")

    # ===================== 核心功能方法 =====================

    def _browse_directory(self):
        """弹出目录选择对话框，加载配表数据"""
        dir_path = filedialog.askdirectory(title="选择游戏项目根目录")
        if not dir_path:
            return

        # 权限校验
        try:
            os.listdir(dir_path)
        except PermissionError:
            self._handle_permission_error(dir_path)
            return
        except OSError as e:
            messagebox.showerror("错误", f"无法访问目录:\n{dir_path}\n\n{str(e)}")
            return

        self.workspace_path = dir_path
        valid, msg = validate_workspace(dir_path)
        if not valid:
            messagebox.showerror("错误", msg)
            return

        # 更新UI显示
        self.path_var.set(dir_path)

        # 索引按钮已移动到“二级检索”右侧，不再显示独立索引管理区（避免布局挤压导致按钮丢失）
        # 这里只更新状态栏提示即可
        self.index_status_var.set("正在校验索引...")
        self.index_icon_var.set("🔄")

        # 在新线程中校验索引并加载数据
        threading.Thread(target=self._check_index_and_load, daemon=True).start()

    def _check_index_and_load(self):
        """后台线程：校验索引状态并加载数据"""
        try:
            self.index_manager = IndexManager(self.index_dir)

            status, message = self.index_manager.check_index_status(self.workspace_path)

            # 回到主线程更新UI
            self.root.after(0, self._on_index_check_done, status, message)
        except PermissionError:
            self.root.after(0, self._handle_permission_error, self.workspace_path)
        except Exception as e:
            self.root.after(0, self._on_index_check_error, str(e))

    def _on_index_check_done(self, status: IndexStatus, message: str):
        """索引校验完成回调"""
        self.index_progressbar.pack_forget()
        self._update_index_ui(status, message)

        if status == IndexStatus.NONE:
            # 无索引，询问是否建立
            self._ask_build_index()

        elif status == IndexStatus.VALID:
            # 索引有效，加载索引并启用搜索
            self._load_tables_with_index()

        elif status == IndexStatus.INCREMENTAL:
            # 部分过期，询问是否刷新
            self._ask_refresh_index(message)

        elif status == IndexStatus.FULL:
            # 变更过多，建议全量重建
            self._ask_rebuild_index(message)

        elif status == IndexStatus.CORRUPTED:
            # 索引损坏
            self._handle_corrupted_index(message)

    def _ask_build_index(self):
        """询问用户是否建立索引"""
        result = messagebox.askyesno(
            "建立索引",
            "未找到索引文件。\n\n"
            "建立索引可以大幅提升搜索速度（首次约需30-60秒）。\n"
            "是否现在建立索引？\n\n"
            "（点击「否」将使用遍历模式搜索）"
        )
        if result:
            self._build_index()
        else:
            # 使用遍历模式
            self._load_tables_fallback()

    def _ask_refresh_index(self, message: str):
        """询问用户是否刷新索引"""
        result = messagebox.askyesno(
            "刷新索引",
            f"索引部分过期：{message}\n\n"
            "是否刷新索引？\n"
            "（点击「否」将使用现有索引搜索）"
        )
        if result:
            self._refresh_index()
        else:
            # 使用现有索引
            self._load_tables_with_index()

    def _ask_rebuild_index(self, message: str):
        """询问用户是否全量重建索引"""
        result = messagebox.askyesno(
            "全量重建索引",
            f"{message}\n\n"
            "建议全量重建索引以保证搜索准确性。\n"
            "是否现在重建？\n\n"
            "（点击「否」将使用遍历模式搜索）"
        )
        if result:
            self._build_index()
        else:
            self._load_tables_fallback()

    def _handle_corrupted_index(self, message: str):
        """处理索引损坏"""
        result = messagebox.askyesno(
            "索引文件损坏",
            f"索引文件已损坏：{message}\n\n"
            "是否删除并重建索引？"
        )
        if result:
            try:
                self.index_manager.delete_index(self.workspace_path)
            except Exception:
                pass
            self._update_index_ui(IndexStatus.NONE, "已删除损坏的索引")
            self._ask_build_index()
        else:
            self._load_tables_fallback()

    def _handle_permission_error(self, path: str):
        """目录权限不足处理"""
        messagebox.showerror(
            "权限错误",
            f"无法访问目录:\n{path}\n\n请检查:\n"
            f"1. 目录是否存在\n"
            f"2. 是否有读取权限\n"
            f"3. 路径是否包含特殊字符"
        )
        self.path_var.set("尚未选择项目目录，请点击右侧按钮选择...")
        self.workspace_path = ""
        self.index_frame.pack_forget()

    def _on_index_check_error(self, error_msg: str):
        """索引校验出错回调"""
        self.index_progressbar.pack_forget()
        self._update_index_ui(IndexStatus.CORRUPTED, f"索引校验出错: {error_msg}")
        self.status_var.set("⚠️ 索引校验失败，将使用遍历模式搜索")
        # 降级为遍历模式
        self._load_tables_fallback()

    def _load_tables_with_index(self):
        """使用索引加载表格数据"""
        self.status_var.set("正在加载配表数据...")
        self.progress.start(10)
        threading.Thread(target=self._load_tables, daemon=True).start()

    def _load_tables_fallback(self):
        """无索引时的降级加载方案"""
        self.status_var.set("正在加载配表数据（遍历模式）...")
        self.progress.start(10)
        threading.Thread(target=self._load_tables, daemon=True).start()

    def _load_tables(self):
        """（后台线程）加载所有配表到内存"""
        try:
            self.loader = TableLoader(self.workspace_path)
            self.loader.scan()
            self.loader.load_all()

            if not self.loader.tables:
                self.root.after(0, self._on_load_complete, False, "未找到任何配表文件")
                return

            # 构造搜索器
            self.searcher = GlobalSearcher(self.loader, self.config)

            # 加载成功，启用搜索
            self.root.after(0, self._on_load_complete, True,
                          f"已加载 {len(self.loader.tables)} 个配表文件，可以开始搜索")
        except Exception as e:
            self.root.after(0, self._on_load_complete, False, f"加载失败: {str(e)}")

    def _on_load_complete(self, success, message):
        """（主线程）加载完成的回调"""
        self.progress.stop()
        if success:
            self.search_entry.config(state='normal')
            self.btn_search.config(state='normal')
            self.detail_entry.config(state='normal')
            self.btn_detail.config(state='normal')
            self.status_var.set(f"✅ {message}")
            self._append_result(f"✅ {message}\n")

            # 根据是否有索引显示不同提示
            if self.index_manager and self.index_manager.index_data:
                self._append_result("📊 索引模式已启用，搜索速度已优化\n")
            else:
                self._append_result("📂 遍历模式：搜索速度较慢，建议建立索引\n")

            self._append_result(f"提示: 输入关键词后点击搜索或按回车键开始检索\n")
        else:
            self.status_var.set(f"❌ {message}")
            messagebox.showerror("加载失败", message)

    # ===================== 索引管理方法 =====================

    def _build_index(self):
        """建立全量索引"""
        if self.index_building:
            return

        if not self.workspace_path:
            messagebox.showwarning("提示", "请先选择项目目录")
            return

        self.index_building = True
        self.index_progress_cancel = False
        self.btn_build_index.config(state='disabled', text="⏳ 建立中...")

        # 显示进度条
        self.index_progressbar.pack(fill=tk.X, pady=(5, 0))
        self.index_progressbar['value'] = 0
        self.index_status_var.set("正在建立索引...")
        self.index_icon_var.set("🔄")
        self.index_status_label.configure(foreground="blue")

        # 后台建立索引
        threading.Thread(target=self._build_index_thread, daemon=True).start()

    def _build_index_thread(self):
        """后台线程：建立索引"""
        try:
            # 先加载表格（索引需要loader）
            self.loader = TableLoader(self.workspace_path)
            self.loader.scan()
            self.loader.load_all()

            if self.index_progress_cancel:
                self.root.after(0, self._on_index_build_cancelled)
                return

            if not self.loader.tables:
                self.root.after(0, self._on_index_build_done, False, "未找到配表文件")
                return

            # 构建搜索器
            self.searcher = GlobalSearcher(self.loader, self.config)

            # 启动进度模拟
            self.root.after(0, self._simulate_progress)

            # 建立索引
            success = self.index_manager.build_full_index(self.workspace_path, self.loader)
            fail_reason = ""
            if not success:
                fail_reason = getattr(self.index_manager, "last_error", "") or "未知错误"

            self.root.after(0, self._on_index_build_done, success,
                           "索引建立完成" if success else f"索引建立失败: {fail_reason}")
        except Exception as e:
            self.root.after(0, self._on_index_build_done, False, f"建立失败: {str(e)}")

    def _simulate_progress(self):
        """模拟进度条更新（索引建立期间的视觉反馈）"""
        if not self.index_building or self.index_progress_cancel:
            return
        current = self.index_progressbar['value']
        if current < 90:
            self.root.after(300, self._simulate_progress)
            self.root.after(0, lambda: self.index_progressbar.step(3))

    def _on_index_build_done(self, success: bool, message: str):
        """索引建立完成回调"""
        self.index_building = False
        self.index_progressbar.pack_forget()
        self.btn_build_index.config(text="🔨 建立索引")

        if success:
            self._update_index_ui(IndexStatus.VALID, f"✅ {message}")
            self._update_index_stats()

            # 启用搜索
            if self.searcher:
                self.search_entry.config(state='normal')
                self.btn_search.config(state='normal')
                self.detail_entry.config(state='normal')
                self.btn_detail.config(state='normal')

            self.status_var.set(f"✅ {message}")
            self._append_result(f"✅ {message}\n")
            self._append_result("📊 索引模式已启用，搜索速度已优化\n")
        else:
            self._update_index_ui(IndexStatus.CORRUPTED, f"❌ {message}")
            log_path = ""
            if self.index_manager:
                log_path = getattr(self.index_manager, "log_file_path", "")
            if log_path:
                self.status_var.set(f"❌ {message}（日志: {log_path}）")
                self._append_result(f"🧾 索引日志: {log_path}\n")
            else:
                self.status_var.set(f"❌ {message}")

    def _on_index_build_cancelled(self):
        """索引建立取消回调"""
        self.index_building = False
        self.index_progressbar.pack_forget()
        self.btn_build_index.config(text="🔨 建立索引")
        self.index_status_var.set("索引建立已取消")
        self.index_icon_var.set("⚪")
        self.index_status_label.configure(foreground="gray")
        self.status_var.set("索引建立已取消")

    def _refresh_index(self):
        """刷新索引（增量/全量）"""
        if self.index_building:
            return

        if not self.index_manager:
            return

        status, message = self.index_manager.check_index_status(self.workspace_path)

        if status == IndexStatus.FULL:
            # 变更过多，全量重建
            result = messagebox.askyesno(
                "全量重建",
                f"变更文件过多，建议全量重建。\n\n是否继续？"
            )
            if result:
                self._build_index()
            return

        # 增量更新
        self.index_building = True
        self.index_progress_cancel = False
        self.btn_refresh_index.config(state='disabled', text="⏳ 更新中...")

        # 显示进度条
        self.index_progressbar.pack(fill=tk.X, pady=(5, 0))
        self.index_progressbar['value'] = 0
        self.index_status_var.set("正在更新索引...")
        self.index_icon_var.set("🔄")
        self.index_status_label.configure(foreground="blue")

        threading.Thread(target=self._refresh_index_thread, daemon=True).start()

    def _refresh_index_thread(self):
        """后台线程：增量更新索引"""
        try:
            # 重新加载变更的表格
            self.loader = TableLoader(self.workspace_path)
            self.loader.scan()
            self.loader.load_all()

            if self.index_progress_cancel:
                self.root.after(0, self._on_index_refresh_cancelled)
                return

            self.searcher = GlobalSearcher(self.loader, self.config)

            # 启动进度模拟
            self.root.after(0, self._simulate_progress)

            success = self.index_manager.update_incremental_index(
                self.workspace_path, self.loader)

            self.root.after(0, self._on_index_refresh_done, success)
        except Exception as e:
            self.root.after(0, self._on_index_refresh_done, False)

    def _on_index_refresh_done(self, success: bool):
        """索引刷新完成回调"""
        self.index_building = False
        self.index_progressbar.pack_forget()
        self.btn_refresh_index.config(text="🔄 刷新索引")

        if success:
            self._update_index_ui(IndexStatus.VALID, "✅ 索引更新完成")
            self._update_index_stats()
            self.status_var.set("✅ 索引更新完成")
        else:
            self._update_index_ui(IndexStatus.CORRUPTED, "❌ 刷新失败")
            self.status_var.set("❌ 索引刷新失败")

    def _on_index_refresh_cancelled(self):
        """索引刷新取消回调"""
        self.index_building = False
        self.index_progressbar.pack_forget()
        self.btn_refresh_index.config(text="🔄 刷新索引")
        self.index_status_var.set("索引更新已取消")
        self.index_icon_var.set("⚪")
        self.index_status_label.configure(foreground="gray")

    def _delete_index(self):
        """删除索引"""
        result = messagebox.askyesno(
            "确认删除",
            "确定要删除索引文件吗？\n下次搜索将使用遍历模式（较慢）。"
        )
        if not result:
            return

        try:
            self.index_manager.delete_index(self.workspace_path)
            self.index_manager.clear()
            self._update_index_ui(IndexStatus.NONE, "索引已删除")
            self.index_stats_var.set("")
            self.status_var.set("已删除索引，将使用遍历模式搜索")
            self._append_result("🗑️ 索引已删除\n")
        except Exception as e:
            messagebox.showerror("错误", f"删除索引失败: {str(e)}")

    # ===================== 搜索功能 =====================

    def _do_search(self):
        """执行搜索（带索引分流）"""
        keyword = self.search_var.get().strip()
        if not keyword:
            messagebox.showwarning("提示", "请输入搜索关键词")
            return

        if self.searcher is None:
            messagebox.showwarning("提示", "请先选择项目目录并等待加载完成")
            return

        # 清空上次结果
        self._clear_result()
        self.detail_var.set("")
        self.last_results = []
        self._append_result(f"🔍 搜索关键词: '{keyword}'\n")

        # 判断是否有索引，选择搜索路径
        if self.index_manager and self.index_manager.index_data:
            self._append_result("📊 使用索引查询（快速模式）\n")
            self._append_result("正在检索...\n\n")
            self.status_var.set("正在索引搜索...")
            threading.Thread(target=self._run_index_search, args=(keyword,), daemon=True).start()
        else:
            self._append_result("📂 使用遍历查询（兼容模式）\n")
            self._append_result("正在检索...\n\n")
            self.status_var.set("正在遍历搜索...")
            threading.Thread(target=self._run_search, args=(keyword,), daemon=True).start()

    def _run_index_search(self, keyword):
        """（后台线程）使用索引执行搜索"""
        try:
            # 精确匹配
            results = self.index_manager.search_index(keyword)

            # 如果没有精确匹配，尝试模糊搜索
            if not results:
                results = self.index_manager.search_index_fuzzy(keyword)

            # 转换为SearchResult格式
            search_results = self._convert_index_matches(results)

            self.root.after(0, self._on_search_done, keyword, search_results)
        except Exception as e:
            self.root.after(0, self._on_search_error, str(e))

    def _convert_index_matches(self, index_matches):
        """将索引匹配结果转换为SearchResult格式"""
        results = []
        seen = set()

        for match in index_matches:
            key = (match.table_name, match.row_index)
            if key in seen:
                continue
            seen.add(key)

            # 从loader中获取完整行数据
            td = self.loader.get_table(match.table_name)
            if td and match.row_index <= td.row_count:
                row_data = {}
                try:
                    row = td.dataframe.iloc[match.row_index - 1]
                    for col in td.columns:
                        val = row[col]
                        import pandas as pd
                        row_data[col] = val if pd.notna(val) else ""
                except Exception:
                    continue

                results.append(SearchResult(
                    table_name=match.table_name,
                    row_index=match.row_index,
                    row_data=row_data,
                    matched_columns=[match.field_name]
                ))
        return results

    def _run_search(self, keyword):
        """（后台线程）执行遍历搜索逻辑"""
        try:
            results = self.searcher.search(keyword)
            self.root.after(0, self._on_search_done, keyword, results)
        except Exception as e:
            self.root.after(0, self._on_search_error, str(e))

    def _on_search_done(self, keyword, results):
        """（主线程）搜索完成的回调"""
        self.status_var.set(f"搜索完成 - 找到 {len(results)} 条匹配记录")

        if not results:
            self._append_result(f"\n❌ 未找到包含 '{keyword}' 的数据\n")
            return

        self._append_result(f"📊 共找到 {len(results)} 条匹配记录\n")
        self._append_result("=" * 60 + "\n\n")

        self.last_results = results

        # 编号列表（二级检索入口）
        self._append_result(" 二级检索编号列表（输入编号后点'查看详情'）\n")
        for i, res in enumerate(results, start=1):
            hit_cols = ",".join(res.matched_columns[:3])
            if len(res.matched_columns) > 3:
                hit_cols += "..."
            # 获取中文名称
            chinese_names = []
            for col in res.matched_columns[:2]:
                cn = self.searcher.get_chinese_name(res.table_name, col)
                if cn:
                    chinese_names.append(cn)
            cn_display = f" ({', '.join(chinese_names)})" if chinese_names else ""
            self._append_result(
                f"  {i:>3}. [{res.table_name}] 行{res.row_index}{cn_display} | 命中字段: {hit_cols}\n"
            )
        self._append_result("\n")

        # 按表分组显示摘要
        by_table = {}
        for r in results:
            by_table.setdefault(r.table_name, []).append(r)

        for tbl_name, tbl_results in by_table.items():
            self._append_result(f"📄 [{tbl_name}] ({len(tbl_results)} 条匹配)\n")
            self._append_result("-" * 40 + "\n")

            # 按匹配列分组
            col_values = {}
            col_rows = {}
            for res in tbl_results:
                for col in res.matched_columns:
                    col_values.setdefault(col, set()).add(str(res.row_data[col]))
                    col_rows.setdefault(col, []).append(res.row_index)

            for col_name, vals in col_values.items():
                meaning = self.searcher.get_meaning(col_name)
                chinese_name = self.searcher.get_chinese_name(tbl_name, col_name)
                display_name = chinese_name or meaning or col_name
                val_list = sorted(vals)[:5]
                val_str = ", ".join(self._truncate(v, 40) for v in val_list)
                if len(vals) > 5:
                    val_str += f"... (共{len(vals)}个)"
                self._append_result(f"  • [{col_name}] {display_name}\n")
                self._append_result(f"    匹配值: {val_str}\n")
                self._append_result(f"    匹配行数: {len(col_rows[col_name])} 行\n")

            self._append_result("\n")

        self._append_result("=" * 60 + "\n")
        self._append_result("💡 提示: 在\"二级检索\"输入编号（如 1）查看完整详情\n")
        self._append_result("   或重新输入更精确的关键词继续筛选\n\n")

    def _on_search_error(self, error_msg):
        """（主线程）搜索出错的回调"""
        self.status_var.set("搜索出错")
        self._append_result(f"\n❌ 搜索出错: {error_msg}\n")

    def _toggle_fk(self):
        """切换是否显示外键关联"""
        self.show_fk = self.fk_var.get()
        mode = "完整模式 (含关联数据)" if self.show_fk else "简单模式 (仅搜索)"
        self.status_var.set(f"切换: {mode}")

    def _toggle_detail_mode(self):
        """切换详情显示模式"""
        self.detail_mode = "compact" if self.compact_var.get() else "full"
        name = "简洁模式" if self.detail_mode == "compact" else "完整模式"
        self.status_var.set(f"切换: 详情显示为{name}")

    def _show_detail_by_index(self):
        """
        根据二级检索编号展示单条详情（优化版）
        
        功能变化：
        - 原来：纯文本 append 到 result_text 框中（无对齐、无颜色）
        - 现在：用 DetailTableFrame（Treeview 表格）展示，
               三列严格对齐，命中行高亮，长文本自动换行，
               关联数据可展开/折叠。
        
        【布局优化】
        - 使用 PanedWindow.add() 添加详情表格，而不是 pack()
        - 详情表格设置 minsize=100 确保最小高度
        - 列表区域保持足够空间显示摘要
        
        保持不变的逻辑：
        - 编号校验、范围检查、数据读取等逻辑不动
        - searcher 的 format_detail 方法保持不动（只作为备用）
        """
        text = self.detail_var.get().strip()
        if not text:
            messagebox.showwarning("提示", "请输入编号（如 1）")
            return
        if not text.isdigit():
            messagebox.showwarning("提示", "编号必须是数字")
            return
        if not self.last_results:
            messagebox.showwarning("提示", "请先执行一级搜索")
            return

        idx = int(text)
        if idx < 1 or idx > len(self.last_results):
            messagebox.showwarning("提示", f"编号超出范围，请输入 1 - {len(self.last_results)}")
            return

        result = self.last_results[idx - 1]

        # ========== 使用表格展示详情（代替原来的纯文本） ==========
        # 1) 在结果文本框中添加一条提示
        self._append_result(f"\n📌 二级详情编号 {idx} —— 详情见下方表格\n")
        
        # 2) 【优化】使用 PanedWindow.add() 添加详情表格
        # 只有当表格还未被添加到 PanedWindow 的窗格中时才添加
        # 使用 PanedWindow.panes() 获取已添加的子控件列表
        # 检查 detail_table 是否已经在窗格列表中
        # 详情表格已经在 PanedWindow 中，无需重复 add
        # 这里仅确保分隔条位置合理，让表格有足够空间展示大量数据
        self.root.after(0, self._init_result_panes)
        
        # 3) 调用 DetailTableFrame 的 show_detail 方法
        #    - 字段名列固定 150px
        #    - 值和含义列自动适配
        #    - 命中行暗红高亮
        #    - 关联数据可双击展开/折叠
        self.detail_table.show_detail(
            result=result,
            searcher=self.searcher,
            show_fk=self.show_fk,
            detail_mode=self.detail_mode,
        )
        
        self.status_var.set(f"已展示编号 {idx} 的详情（表格模式）")

    def _clear_result(self):
        """
        清空结果展示区
        
        同时清空：
        - 上部的文本摘要（ScrolledText）
        - 下部的详情表格（DetailTableFrame）
        
        【布局优化】
        - 使用 PanedWindow.forget() 移除详情表格，而不是 pack_forget()
        - 恢复 result_text 的初始高度为 18（占窗口约 25%）
        """
        # 清空上部文本
        self.result_text.config(state='normal')
        self.result_text.delete('1.0', tk.END)
        self.result_text.config(state='disabled')
        
        # 【优化】恢复文本区域高度为初始值 18
        # 原来设置为 10 会导致列表区域变得很小
        self.result_text.configure(height=18)
        
        # 【修改】使用 PanedWindow.forget() 隐藏详情表格
        # 原来使用 pack_forget()，但现在表格是通过 PanedWindow.add() 添加的
        # 需要使用 PanedWindow 的 forget() 方法来移除
        self.detail_table.clear()
        # 不再移除表格，只清空内容；保留布局，避免按钮/布局跳动

    def _copy_result(self):
        """
        复制结果到剪贴板
        
        注意：只复制 ScrolledText 中的文本摘要内容。
        表格详情因为包含 Treeview 的行数据，暂不纳入复制。
        如需复制表格内容，建议使用「二级检索大图」功能另行导出。
        """
        self.result_text.config(state='normal')
        content = self.result_text.get('1.0', tk.END)
        self.result_text.config(state='disabled')
        if content.strip():
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            self.status_var.set("✅ 已复制结果到剪贴板（仅文本摘要）")
        else:
            self.status_var.set("结果为空，无法复制")

    # ===================== UI辅助方法 =====================

    def _append_result(self, text):
        """向结果框追加文本（线程安全）"""
        def _append():
            self.result_text.config(state='normal')
            self.result_text.insert(tk.END, text)
            self.result_text.see(tk.END)  # 自动滚动到底部
            self.result_text.config(state='disabled')
        self.root.after(0, _append)

    @staticmethod
    def _truncate(text, max_len=500):
        """截断过长的字符串"""
        if text is None:
            return ""
        text = str(text)
        if len(text) <= max_len:
            return text
        return text[:max_len - 3] + "..."

    def _on_enter_search(self, event):
        """处理回车键触发搜索"""
        widget = self.root.focus_get()
        if widget == self.detail_entry and self.detail_entry.cget('state') == 'normal':
            self._show_detail_by_index()
            return
        if widget == self.search_entry and self.search_entry.cget('state') == 'normal':
            self._do_search()


def main():
    """程序入口"""
    # 修复Windows终端编码（虽然GUI不需要，但保留兼容性）
    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass

    # 创建主窗口
    root = tk.Tk()

    # 设置窗口图标（可选，需要.ico文件时取消注释）
    # icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
    # if os.path.exists(icon_path):
    #     root.iconbitmap(icon_path)

    # 设置高DPI支持（Windows）
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    # 尝试设置Windows主题（需要ttkbootstrap或customtkinter时启用）
    # 标准Tkinter使用默认主题

    app = GameConfigSearcherApp(root)

    # 启动主循环
    root.mainloop()


if __name__ == "__main__":
    main()