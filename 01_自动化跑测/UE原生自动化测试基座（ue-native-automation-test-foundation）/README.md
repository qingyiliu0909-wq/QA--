# UE 原生自动化测试基座

用于 Unreal Engine 项目的编辑器自动化测试参考包，覆盖两类测试：

| 类型 | 适用场景 | 运行方式 |
| --- | --- | --- |
| 原生单元测试 | 纯逻辑、数据解析、资产约束、工具函数 | `IMPLEMENT_SIMPLE_AUTOMATION_TEST` |
| 功能测试 | 打开地图、生成测试 Actor、验证运行时行为 | `AFunctionalTest` + Automation Framework |
| Lua 用例发现（可选） | 用 Lua 编写大量轻量回归用例 | UnLua + 复杂 Automation Test |

## 目录

| 目录 | 内容 | 是否可直接使用 |
| --- | --- | --- |
| `最小模板_可直接改名使用` | 一个原生单元测试和一个 Functional Test Actor 的 UE 模块骨架 | 是，替换模块名后接入 |
| `参考源码_需项目适配` | Lua 用例自动发现、Unit/Functional 分流和地图执行的成熟参考实现 | 否，需要完成适配清单 |
| `示例用例` | Lua 用例的约定示例 | 仅在接入 Lua 运行时后使用 |
| `迁移清单.md` | 依赖、固定路径与验收步骤 | 必读 |

## 最小接入步骤

1. 将 `最小模板_可直接改名使用/Source/ProjectAutomationTests` 放入目标项目的 `Source/`。
2. 把 `ProjectAutomationTests`、`PROJECTAUTOMATIONTESTS_API` 替换为项目模块名和 API 宏；在 `.uproject` 或 Target 中启用 Editor 模块。
3. 编译 Editor，在 Session Frontend / Test Automation 中搜索 `Project.Smoke`。
4. 先运行 `Project.Smoke.Basic`；再把 `BP_ProjectFunctionalTestActor` 放入测试地图，运行 `Project.Functional.Basic`。
5. 若需要大量脚本用例，再按 `迁移清单.md` 接入 Lua 发现层。

## 运行边界

- 仅应在 Editor、开发包或测试包中启用；Shipping 包不要携带测试入口。
- 功能测试地图、测试数据、账号和 GM 指令属于项目资产，不放在本基座内。
- 测试应可重复执行：自行创建与清理数据，不依赖上一次运行留下的状态。
