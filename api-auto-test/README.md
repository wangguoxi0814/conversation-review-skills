# api-auto-test

面向后端 HTTP API 的 **Cursor Agent Skill**：从确认范围、深度分析接口、生成 IDEA 友好的 `.http`、数据源 MCP 造数、行级校验到一体报告，形成可复用的自动化测试闭环。

> 个人级 Skill 路径：`~/.cursor/skills/api-auto-test/`  
> 使用方式：在对话中显式附加 / `@api-auto-test`（`disable-model-invocation: true`）。

---

## 能做什么

| 能力 | 说明 |
|------|------|
| 范围确认 | 按目录 / Controller / 具体 path 确认测什么、环境、是否允许写库造数 |
| 深度分析 | 读 Controller → Service → 校验/权限/落库，设计高覆盖用例 |
| 生成 `.http` | 一 Controller 一文件，可在 IntelliJ / VS Code REST Client 中直接跑 |
| 造数溯源 | 造数逻辑 + SQL 写入报告；经 **数据源 MCP 逐条执行**，失败自动改 SQL 再试 |
| Commit 增量 | 记录 `cached_commit`；无新提交可复用；有变更则沿**调用链路**只重分析关联接口 |
| 行级校验 | 固定跑通用脚本：请求前后完整行快照 + 字段级 diff |
| 一体报告 | 分析与实测同一份 `REPORT.md`；接口一览按 **成功 / 失败 / 跳过** 分类 |

---

## 快速开始

1. **准备数据源 MCP**（造数与校验依赖）  
   - 配置并启用 **MySQL / 数据库 MCP**（如 `user-mysql`），连接到**测试/预发**库。  
   - MCP 需具备执行 `SELECT` 以及造数所需的 `INSERT` / `UPDATE` / `DELETE` 权限；若当前为只读，Agent 会停下来请你开启写权限。  
2. 在对话中/api-auto-test调用skill
5. 等待 Agent 产出 `http/{Controller}/` 下的用例与报告，并按步骤执行校验。

---

## 目录结构

```text
api-auto-test/
├── README.md                 ← 本说明
├── SKILL.md                  ← Agent 主流程（必读入口）
├── references/               ← 模板与细则（渐进披露）
│   ├── http-file-template.md
│   ├── report-template.md
│   ├── analysis-cache.md
│   ├── test-data-seed-log.md
│   ├── run-rowcheck.md
│   ├── result-status.md
│   └── mysql-check-template.md
└── scripts/
    └── run_api_rowcheck.py   ← 通用行级校验脚本
```

