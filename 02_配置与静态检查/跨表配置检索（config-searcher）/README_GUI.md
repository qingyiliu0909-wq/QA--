# 游戏配表检索工具 v2.0

## 概述

这是一个完全通用的跨表格配表检索工具，支持自动关联发现，无需手动配置外键关系。

## 新功能 (v2.0)

### 1. 自动关联发现
- **基于命名约定自动发现外键关联**
  - 规则1: `XXId` 字段 → 自动查找 `XX` 表的主键
    - 例: `RegionId` → `Region表.RegionId`
  - 规则2: 字段名包含表名关键词 → 模糊匹配
    - 例: `UnlockCondition` → `Condition表.ConditionId`
- **无需手动配置 foreign_keys**，新增表自动生效

### 2. Excel表头元数据解析
- 自动解析Excel第1行中文名称作为字段备注
- 自动识别每张表的主键字段
- 搜索结果中显示中文名称，方便理解

### 3. 递归关联查询
- 自动追踪完整的关联链路
- 例如：搜索DynQuestId → 显示关联的Condition → 显示关联的Reward → 显示关联的Resource...

### 4. 更友好的显示
- 摘要视图显示中文字段名
- 详情视图显示关联数据树
- 支持简洁/完整两种模式切换

## 使用方法

### GUI模式
```bash
python gui_app.py
```
或双击 `GameConfigSearcher.exe`

### 命令行模式
```bash
# 交互式模式
python main.py <工作区目录>

# 直接搜索
python main.py <工作区目录> <关键词>

# 列出所有表格
python main.py <工作区目录> --list
```

## 目录结构

```
tool/
├── config.json      # 配置文件（字段含义、枚举映射等）
── loader.py        # 表格加载器（解析Excel元数据）
├── searcher.py      # 搜索引擎（自动关联发现）
├── gui_app.py       # GUI界面
├── main.py          # 命令行入口
└── utils.py         # 工具函数
```

## 配置说明

### config.json 主要配置项

| 配置项 | 说明 |
|--------|------|
| `auto_discover.enabled` | 是否启用自动关联发现（默认true） |
| `auto_discover.max_fk_depth` | 关联查询最大深度（默认5） |
| `field_meanings` | 手动补充的字段含义（可选） |
| `enum_mappings` | 枚举值映射 |
| `table_display_fields` | 各表优先显示的字段 |

## Excel格式要求

工具支持标准配表格式：
```
第0行：Sheet名称行（可选） "--- Sheet: 表名 ---"
第1行：中文名称           "事件ID" | "事件名称" | ...
第2行：数据类型           Int     | String     | ...
第3行：英文字段名         DynQuestId | DynName | ...
第4行：可见性标记         server/client | ...
第5行+：实际数据          100101  | ...       | ...
```

## 打包成exe

```bash
pyinstaller --onefile --windowed --name GameConfigSearcher gui_app.py
```

## 常见问题

### Q: 为什么有些Excel文件加载失败？
A: 部分Excel文件结构可能不符合标准格式，工具会跳过这些文件继续加载其他文件。

### Q: 如何添加新的关联规则？
A: v2.0支持自动关联发现，通常无需手动配置。如需特殊处理，可在 `config.json` 的 `field_meanings` 中补充说明。

### Q: 关联查询太慢怎么办？
A: 可在 `config.json` 中调整 `auto_discover.max_fk_depth` 减小关联深度，或减小 `max_results_per_table` 限制结果数量。