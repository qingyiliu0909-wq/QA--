把黑盒跑测需要的资源放这里。

建议结构：

- `runner/assets/win/`：Windows 侧图像模板（按钮/界面锚点）
- `runner/assets/android/`：Android 侧（如要做图像锚点匹配）模板图

用例里 `anchor.asset` 的相对路径是相对 `--assets` 指定目录（默认就是 `runner/assets`）。

