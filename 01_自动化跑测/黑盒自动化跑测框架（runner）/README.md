# Dungeon auto-runner (blackbox)

目标：在**不改包体**的前提下，通过外部黑盒方式在 **Windows 本地** 与 **Android 真机**自动跑“进入副本 → 完整流程 → 结算/退出”，并产出可归档结果（截图、日志、报告）。

## 目录结构

- `runner/`
  - `main.py`：CLI 入口
  - `cases/`：用例 YAML
  - `assets/`：图像模板等资源
  - `core/`：编排、报告、工具函数
  - `platform/`：Windows/Android driver
- `results/`：运行输出（默认在仓库根目录下创建）

## 环境准备

### Python

建议 Python 3.10+，并使用虚拟环境：

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r runner\requirements.txt
```

### Android（可选）

- 安装 Android SDK platform-tools（确保 `adb` 在 PATH）
- 手机开启 USB 调试

## 快速开始

### 1) 查看用例

示例用例：`runner/cases/dungeon_smoke.yaml`

### 2) Windows 跑一条（示例）

```bash
python -m runner.main --platform win --case runner\cases\dungeon_smoke.yaml --exe "D:\Path\To\Game.exe" --title "EM"
```

### 3) Android 跑一条（示例）

```bash
python -m runner.main --platform android --case runner\cases\dungeon_smoke.yaml --device <adb_serial> --package com.your.game
```

## 输出

每次运行会创建：`results/<run_id>/`

- `report.json`：结构化结果
- `junit.xml`：可选（`--junit`）
- `steps/`：每步截图、logcat 切片等

## 说明

- Windows 侧默认基于**图像模板**定位按钮/界面（OpenCV），并使用输入注入执行点击/按键。
- Android 侧优先使用 **uiautomator2（控件树锚点）**，也可退化为截图模板匹配（需要额外资源）。

