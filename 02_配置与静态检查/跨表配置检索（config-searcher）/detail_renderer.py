#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
detail_renderer.py - 搜索结果详情展示渲染器
=============================================
基于 tkinter.ttk.Treeview 的表格化展示模块。
负责将单条搜索结果的字段详情以严格对齐的表格形式呈现。

设计目标：
  1. 三列严格左对齐：「字段」「值」「含义」
  2. 字段列固定宽度，值和含义列自适应
  3. 单元格内自动换行，长文本不溢出
  4. 颜色区分：字段名浅蓝、值白色、含义灰色
  5. 命中字段高亮背景色
  6. 保留展开/折叠关联数据的交互

与 searcher 的对接：
  依赖 searcher 模块中的 SearchResult、FKLink 类型，以及
  GlobalSearcher 中的 _explain_field_value、get_chinese_name、
  discover_and_resolve_fk 等方法进行数据解析。
  本模块只负责「显示渲染」，不修改数据解析逻辑。
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Optional, Dict, Any


# ================================================================
#  全局样式常量（统一管理，方便调色）
# ================================================================
STYLE = {
    # 背景色
    "bg_root": "#1e1e1e",          # 深色整体背景
    "bg_heading": "#2d2d2d",       # 表头背景
    "bg_row_even": "#252526",      # 偶数行背景
    "bg_row_odd": "#1e1e1e",       # 奇数行背景
    "bg_hit": "#3a2d2d",           # 命中行背景（暗红/棕）
    
    # 文字颜色
    "fg_field": "#6db3f2",         # 字段名 - 浅蓝
    "fg_value": "#ffffff",         # 值 - 白色
    "fg_meaning": "#a0a0a0",       # 含义 - 灰色
    "fg_heading": "#ffffff",       # 表头文字 - 白色
    
    # 字体
    "font_family": "Microsoft YaHei UI",  # 中文字体
    "font_size": 10,
    "font_heading_size": 10,
    
    # 列宽
    "field_col_width": 150,        # 字段列固定宽度 (px)
    "value_col_width": 300,        # 【优化】值列宽度 (px)，从 200 增加到 300，让长值有更多显示空间
    "row_height": 48,              # 【优化】默认行高，从 28 增加到 48，让多行文本能完整显示
}


def _get_font(size_adj: int = 0, bold: bool = False) -> tuple:
    """获取标准字体元组"""
    weight = "bold" if bold else "normal"
    return (STYLE["font_family"], STYLE["font_size"] + size_adj, weight)


class DetailTableFrame(ttk.Frame):
    """
    搜索结果详情表格容器
    
    功能：
    - 三列表格展示：字段名（固定宽）、值（自适应）、含义（自适应）
    - 命中行高亮（暗红背景）
    - 关联数据可展开/折叠（通过双击行触发）
    
    用法：
      frame = DetailTableFrame(parent)
      frame.show_detail(result, searcher)   # 渲染一条结果的详情
      frame.clear()                         # 清空表格
    """

    def __init__(self, parent: tk.Widget, **kwargs):
        """
        初始化表格容器
        
        参数:
            parent: 父容器 widget
        """
        super().__init__(parent, **kwargs)
        
        # ========== 构建表格（先构建，因为标签配置需要 tree 对象） ==========
        self._build_treeview()
        
        # ========== 样式配置 ==========
        self._configure_styles()
        
        # ========== 配置颜色标签 ==========
        self._configure_tags()
        
        # ========== 状态变量 ==========
        self._current_fk_links: List[Any] = []     # 当前展示的外键关联列表
        self._expanded_rows: Dict[str, bool] = {}  # 行id(str) -> 是否展开
        self._fk_child_data: Dict[str, Dict] = {}  # 行id -> 子数据缓存（展开/折叠用）
        
        # ========== 滚动条与Treeview联动 ==========
        self._link_scrollbars()

    # ================================================================
    #  样式配置
    # ================================================================
    
    def _configure_styles(self):
        """配置 ttk 样式主题"""
        style = ttk.Style()
        style.theme_use("default")
        
        # 表头样式
        style.configure(
            "Detail.Treeview.Heading",
            font=_get_font(size_adj=0, bold=True),
            background=STYLE["bg_heading"],
            foreground=STYLE["fg_heading"],
            relief="flat",
            borderwidth=1,
            padding=(8, 4),
        )
        style.map(
            "Detail.Treeview.Heading",
            background=[("active", "#3a3a3a")],
        )
        
        # 表格行样式
        style.configure(
            "Detail.Treeview",
            font=_get_font(),
            background=STYLE["bg_row_odd"],
            foreground=STYLE["fg_value"],
            fieldbackground=STYLE["bg_row_odd"],
            borderwidth=0,
            rowheight=STYLE["row_height"],
            highlightthickness=0,
        )
        style.map(
            "Detail.Treeview",
            background=[("selected", "#2a3d5c")],  # 选中行用深蓝
            foreground=[("selected", "#ffffff")],
        )

    # ================================================================
    #  构建 Treeview 控件
    # ================================================================

    def _build_treeview(self):
        """创建三列 Treeview 表格"""
        # 列定义：字段名（固定宽度）、值（自适应）、含义（自适应）
        columns = ("field", "value", "meaning")
        
        self.tree = ttk.Treeview(
            self,
            columns=columns,
            show="tree headings",  # 显示表头 + 树状折叠标识
            style="Detail.Treeview",
            selectmode="browse",   # 单选
        )
        
        # -------- 配置三列 --------
        # 第0列是 tree 自带的 #0 列（用于折叠图标），隐藏它
        self.tree.column("#0", width=0, minwidth=0, stretch=False)
        
        # 列1: 字段名 → 固定宽度 150px，左对齐
        self.tree.column("field", width=STYLE["field_col_width"],
                         minwidth=120, stretch=False, anchor="w")
        self.tree.heading("field", text="字段", anchor="w")
        
        # 列2: 值 → 自适应宽度，左对齐
        # 【优化】width 从 200 增加到 300，让长值（如逗号分隔的列表）有更多显示空间
        self.tree.column("value", width=STYLE["value_col_width"], minwidth=150,
                         stretch=True, anchor="w")
        self.tree.heading("value", text="值", anchor="w")
        
        # 列3: 含义 → 自适应宽度，左对齐
        self.tree.column("meaning", width=250, minwidth=100,
                         stretch=True, anchor="w")
        self.tree.heading("meaning", text="含义", anchor="w")
        
        # -------- 绑定事件 --------
        # 双击行切换关联数据的展开/折叠
        self.tree.bind("<Double-1>", self._on_double_click)
        
        self.tree.pack(fill=tk.BOTH, expand=True)

    def _link_scrollbars(self):
        """将垂直/水平滚动条与 Treeview 关联"""
        # 垂直滚动条
        v_scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL,
                                    command=self.tree.yview)
        self.tree.configure(yscrollcommand=v_scrollbar.set)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 水平滚动条（让值和含义列不会溢出，仅在列太多时出现）
        h_scrollbar = ttk.Scrollbar(self, orient=tk.HORIZONTAL,
                                    command=self.tree.xview)
        self.tree.configure(xscrollcommand=h_scrollbar.set)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

    # ================================================================
    #  核心渲染接口
    # ================================================================

    def show_detail(self, result, searcher,
                    show_fk: bool = True, detail_mode: str = "compact"):
        """
        渲染单条搜索结果的完整详情到表格中
        
        参数:
            result: SearchResult 对象
            searcher: GlobalSearcher 实例（用于解释字段含义、解析外键）
            show_fk: 是否显示关联数据
            detail_mode: "compact" 简洁模式 / "full" 完整模式
        """
        # 1) 清空旧数据
        self.clear()
        
        # 2) 写入表信息（作为第一行，非选中）
        info_text = f"表: {result.table_name}  |  行号: {result.row_index}  |  模式: {'简洁' if detail_mode == 'compact' else '完整'}"
        self._insert_info_row(info_text)
        
        # 3) 收集命中字段集合
        hit_columns = set(result.matched_columns)
        
        # 4) 按顺序渲染各字段
        if detail_mode == "compact":
            # 简洁模式：只显示命中字段 + 关键显示字段
            keep_cols = set(searcher._pick_display_columns(
                result.table_name, result.row_data))
            keep_cols.update(hit_columns)
        else:
            # 完整模式：显示所有字段
            keep_cols = set(result.row_data.keys())
        
        # 先渲染命中字段（放在最前面，突出显示）
        for col_name in result.matched_columns:
            self._render_field_row(result, col_name, searcher,
                                   is_hit=True, indent=0)
        
        # 再渲染其余字段（排除已显示的命中字段）
        rendered = set(result.matched_columns)
        for col_name in keep_cols:
            if col_name in rendered:
                continue
            self._render_field_row(result, col_name, searcher,
                                   is_hit=False, indent=0)
            rendered.add(col_name)
        
        # 简洁模式下，显示省略提示
        if detail_mode == "compact":
            total = len(result.row_data.keys())
            shown = len(rendered)
            omitted = total - shown
            if omitted > 0:
                self._insert_info_row(
                    f"... 已省略 {omitted} 个非关键字段（切换完整模式可查看全部）",
                    tag="omitted"
                )
        
        # 5) 分隔线
        sep_id = self.tree.insert("", tk.END, values=(
            "─" * 40, "─" * 40, "─" * 40
        ), tags=("separator",))
        
        # 6) 外键关联数据
        if show_fk:
            fk_links = searcher.discover_and_resolve_fk(
                result.table_name, result.row_data)
            self._current_fk_links = fk_links
            
            if fk_links:
                # 关联数据标题行
                self._insert_info_row("关联数据（自动发现）— 双击行展开/折叠详情")
                
                for i, link in enumerate(fk_links):
                    self._render_fk_link_row(link, i, searcher,
                                             compact=(detail_mode == "compact"))
        
        # 7) 调整行高（让长文本显示完整）
        self._auto_adjust_row_height()

    def clear(self):
        """清空表格所有内容"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._current_fk_links = []
        self._expanded_rows.clear()

    # ================================================================
    #  行渲染方法
    # ================================================================

    def _render_field_row(self, result, col_name: str, searcher,
                          is_hit: bool = False, indent: int = 0):
        """
        渲染单个字段行
        
        参数:
            result: SearchResult
            col_name: 字段名
            searcher: GlobalSearcher
            is_hit: 是否为命中字段
            indent: 缩进层级（用于关联数据）
        """
        # 获取字段值 + 业务释义
        col_val = result.row_data.get(col_name, "")
        display_val, explain = searcher._explain_field_value(
            result.table_name, col_name, col_val)
        
        # 处理长值：逗号分隔的多值列表按逗号换行，每行缩进
        formatted_val = self._format_long_text(str(display_val))
        formatted_meaning = self._format_long_text(str(explain) if explain else "-")
        
        # 字段显示名（命中字段加标记）
        chinese_name = searcher.get_chinese_name(result.table_name, col_name)
        if chinese_name:
            field_display = f"{col_name} ({chinese_name})"
        else:
            field_display = col_name
        
        if is_hit:
            field_display = f"★ {field_display}  ← 命中"
        
        # 添加缩进前缀
        if indent > 0:
            prefix = "  " * indent
            field_display = prefix + field_display
        
        # 确定标签
        tags = ("field_row",)
        if is_hit:
            tags = ("hit_row",)  # 命中行特殊高亮
        
        # Treeview 行高无法随换行自动增长；对长文本采用"续行"模式插入多行，确保全部可见。
        _ = self._insert_multiline_row(
            parent="",
            field_text=field_display,
            value_text=formatted_val,
            meaning_text=formatted_meaning,
            tags=tags,
        )

    def _insert_multiline_row(self, parent, field_text: str, value_text: str,
                              meaning_text: str, tags: tuple) -> List[str]:
        """
        插入可能包含多行（\n）的字段行：
        - 第一行显示字段名 + 第1行值/含义
        - 后续行字段列留空，仅展示续行内容（并保持缩进）
        """
        v_lines = str(value_text).splitlines() if value_text is not None else [""]
        m_lines = str(meaning_text).splitlines() if meaning_text is not None else [""]
        max_lines = max(len(v_lines), len(m_lines), 1)
        v_lines += [""] * (max_lines - len(v_lines))
        m_lines += [""] * (max_lines - len(m_lines))

        inserted_ids: List[str] = []

        # 第一行
        first_id = self.tree.insert(
            parent, tk.END,
            values=(field_text, v_lines[0], m_lines[0]),
            tags=tags
        )
        inserted_ids.append(first_id)

        # 续行（字段列置空）
        cont_tags = ("cont_row",)
        for i in range(1, max_lines):
            cid = self.tree.insert(
                parent, tk.END,
                values=("", v_lines[i], m_lines[i]),
                tags=cont_tags
            )
            inserted_ids.append(cid)
        return inserted_ids

    def _render_fk_link_row(self, link, index: int, searcher,
                            compact: bool = True, depth: int = 0):
        """
        渲染外键关联行
        
        每个关联显示为一组行：
         - 第一行：关联概要（可双击展开后续详情）
         - 子行：目标表的关键字段（初始折叠）
        """
        indent = depth + 1
        
        # 关联概要行
        source_chinese = searcher.get_chinese_name(
            link.source_table, link.source_field)
        source_display = source_chinese or link.source_field
        
        summary = (f"→ [{link.target_table}] "
                   f"{source_display}={link.source_value}")
        
        # 获取目标表简要信息
        target_brief = searcher._row_brief(
            link.target_table, link.target_row)
        
        link_id = self.tree.insert(
            "", tk.END,
            values=(summary, target_brief, ""),
            tags=("fk_summary",)
        )
        
        # 子行：目标表关键字段详情（初始化时折叠）
        show_cols = searcher._pick_display_columns(
            link.target_table, link.target_row)
        
        # 把这些子行暂存到字典中，展开时再渲染
        self._expanded_rows[link_id] = False
        self._fk_child_data[link_id] = {
            "table_name": link.target_table,
            "row_data": link.target_row,
            "searcher": searcher,
            "show_cols": show_cols,
            "children_links": link.children,
            "compact": compact,
            "depth": depth + 1,
        }

    def _insert_info_row(self, text: str, tag: str = "info"):
        """插入信息提示行（如标题、省略提示等）"""
        self.tree.insert("", tk.END, values=(text, "", ""), tags=(tag,))

    # ================================================================
    #  文本格式化工具
    # ================================================================

    @staticmethod
    def _format_long_text(text: str, max_line_len: int = 80) -> str:
        """
        处理长文本：按逗号或空格折行，提升可读性
        
        策略：
        1. 如果文本包含逗号（逗号分隔的多值列表），在逗号后换行
        2. 每行的第二行开始加缩进（用空格表示）
        3. 普通长文本超过 max_line_len 时强制折行
        """
        if not text or text == "-":
            return text
        
        text = str(text)
        
        # 情况1：逗号分隔的多值列表 → 每个值一行（不截断）
        if "," in text:
            parts = [p.strip() for p in text.split(",")]
            if len(parts) > 1:
                lines = [parts[0]]
                for part in parts[1:]:
                    lines.append(f"    {part}")
                return "\n".join(lines)
        
        # 情况2：空格分隔的较长文本
        if " " in text and len(text) > max_line_len:
            words = text.split()
            lines = []
            current_line = ""
            for word in words:
                if len(current_line) + len(word) + 1 > max_line_len:
                    lines.append(current_line)
                    current_line = "    " + word  # 第二行开始缩进
                else:
                    if current_line:
                        current_line += " " + word
                    else:
                        current_line = word
            if current_line:
                lines.append(current_line)
            return "\n".join(lines)
        
        # 情况3：无分隔符的超长文本，硬折行
        if len(text) > max_line_len:
            lines = []
            for i in range(0, len(text), max_line_len):
                chunk = text[i:i + max_line_len]
                if i == 0:
                    lines.append(chunk)
                else:
                    lines.append("    " + chunk)  # 缩进
            return "\n".join(lines)
        
        return text

    # ================================================================
    #  交互事件
    # ================================================================

    def _on_double_click(self, event):
        """
        双击行事件处理：
        - 如果是关联概要行，展开/折叠其子详情
        - 展开时动态添加子行，折叠时移除
        """
        item_id = self.tree.focus()
        if not item_id:
            return
        
        # 检查是否为关联摘要行
        if item_id in self._fk_child_data:
            is_expanded = self._expanded_rows.get(item_id, False)
            
            if is_expanded:
                # 折叠：移除子行
                self._collapse_fk_row(item_id)
            else:
                # 展开：动态添加子行
                self._expand_fk_row(item_id)

    def _expand_fk_row(self, parent_id: str):
        """展开关联行的子详情"""
        data = self._fk_child_data.get(parent_id)
        if not data:
            return
        
        searcher = data["searcher"]
        row_data = data["row_data"]
        table_name = data["table_name"]
        show_cols = data["show_cols"]
        children_links = data["children_links"]
        compact = data["compact"]
        depth = data["depth"]
        
        # 添加子行的容器
        child_ids = []
        
        # 渲染关键字段详情
        for col_name in show_cols[:6]:
            col_val = row_data.get(col_name, "")
            display_val, explain = searcher._explain_field_value(
                table_name, col_name, col_val)
            
            chinese = searcher.get_chinese_name(table_name, col_name)
            display_name = chinese or col_name
            
            formatted_val = self._format_long_text(str(display_val))
            formatted_explain = self._format_long_text(
                str(explain) if explain else "-")
            
            prefix = "  " * depth
            # 同样用续行方式插入，避免长文本被固定行高截断
            ids = self._insert_multiline_row(
                parent=parent_id,
                field_text=f"{prefix}{display_name}",
                value_text=formatted_val,
                meaning_text=formatted_explain,
                tags=("fk_detail",),
            )
            child_ids.extend(ids)
        
        # 递归渲染子关联
        if children_links:
            for i, child_link in enumerate(children_links):
                child_prefix = "  " * (depth + 1)
                child_summary_id = self.tree.insert(
                    parent_id, tk.END,
                    values=(
                        f"{child_prefix}[下级关联] "
                        f"{child_link.target_table}",
                        searcher._row_brief(
                            child_link.target_table,
                            child_link.target_row),
                        ""
                    ),
                    tags=("fk_summary",)
                )
                # 递归展开的关联数据暂时不自动展开子行
                child_ids.append(child_summary_id)
        
        # 记录展开状态
        self._expanded_rows[parent_id] = True
        self._fk_child_data[parent_id]["child_ids"] = child_ids
        
        # 展开父节点
        self.tree.item(parent_id, open=True)

    def _collapse_fk_row(self, parent_id: str):
        """折叠关联行的子详情"""
        data = self._fk_child_data.get(parent_id)
        if not data:
            return
        
        # 删除所有子行
        child_ids = data.get("child_ids", [])
        for child_id in child_ids:
            try:
                self.tree.delete(child_id)
            except Exception:
                pass
        
        data["child_ids"] = []
        self._expanded_rows[parent_id] = False
        self.tree.item(parent_id, open=False)

    # ================================================================
    #  行高自适应
    # ================================================================

    def _auto_adjust_row_height(self):
        """
        为多行文本的行增加行高，让长内容完整显示
        
        Treeview 本身不支持按行设置不同的行高，但我们可以：
        1. 统一设一个较大的最小行高
        2. 或者利用 tag_configure 设置统一的字体行距
        
        【优化】增加行高到 STYLE["row_height"] + 10，让每行能显示约 2-3 行中文
        当值列内容包含换行符时，续行模式下每行高度需要更大
        """
        style = ttk.Style()
        style.configure("Detail.Treeview", rowheight=STYLE["row_height"] + 10)

    # ================================================================
    #  标签颜色配置
    # ================================================================

    def _configure_tags(self):
        """
        配置不同行的颜色标签（字体+背景色+前景色）。
        注意：ttk.Treeview.tag_configure 是每个 widget 实例独立的，
        所以每个 DetailTableFrame 都需要调用一次。
        """
        
        # 字段行（默认）：字段名浅蓝、值白色、含义灰色
        self.tree.tag_configure(
            "field_row",
            background=STYLE["bg_row_even"],
            foreground=STYLE["fg_value"],
        )
        
        # 命中行：暗红背景 + 白色文字
        self.tree.tag_configure(
            "hit_row",
            background=STYLE["bg_hit"],
            foreground=STYLE["fg_value"],
            font=_get_font(size_adj=0, bold=False),
        )
        
        # 信息行（标题/省略提示）：居中灰色
        self.tree.tag_configure(
            "info",
            background=STYLE["bg_row_odd"],
            foreground="#888888",
            font=_get_font(size_adj=-1),
        )
        
        # 省略提示行
        self.tree.tag_configure(
            "omitted",
            background=STYLE["bg_row_odd"],
            foreground="#666666",
            font=_get_font(size_adj=-1, bold=False),
        )
        
        # 分隔线
        self.tree.tag_configure(
            "separator",
            background=STYLE["bg_row_odd"],
            foreground="#444444",
        )
        
        # 关联摘要行
        self.tree.tag_configure(
            "fk_summary",
            background="#2a2a3a",  # 深蓝紫底色
            foreground="#8ab4f8",  # 亮蓝色
            font=_get_font(size_adj=0, bold=False),
        )
        
        # 关联详情行
        self.tree.tag_configure(
            "fk_detail",
            background="#232333",
            foreground="#cccccc",
            font=_get_font(size_adj=-1),
        )
        
        # 【新增】续行标签：与字段行同背景色，但文字稍暗
        self.tree.tag_configure(
            "cont_row",
            background=STYLE["bg_row_even"],
            foreground="#b0b0b0",
        )


# ================================================================
#  辅助函数：为不同颜色的列值设置 tag
# （Treeview 不支持单单元格着色，我们用整行加tag替代）
# ================================================================

def colorize_field_value(tree, item_id, col_name, value, meaning):
    """
    对单个 item 的三列设置颜色。
    由于 Treeview 不支持列级前景色，我们用整行的 tag 控制。
    这里是一个扩展点，未来如果 ttk.Treeview 支持列级前景色，
    可以在这里实现。
    """
    # 当前 Treeview 限制：只能设置整行颜色。
    # 我们用"列名缩写+颜色"的约定来提示用户区分
    pass