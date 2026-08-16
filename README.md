# Conversation Review

> **和AI聊了一整天，活干了不少，想复盘，但无从下手？那就用这个SKILL！**

## 使用最佳姿势

### 1. 对话分类，窗口独立

零散问题（查概念、问语法、临时 debug）和系统性任务对话（功能开发、架构设计、问题排查）应使用**各自独立的对话窗口**。
- 窗口独立能保持上下文纯净，提升大模型在对话中的理解和总结质量
- 最终生成的报告文件独立，便于快速对所有零散问题回顾和系统性任务回顾，避免一个文件夹在着对零散问题和系统性任务的回顾。

### 2. 复盘即终点，不再追加

触发 `/conversation-review` 后，当前窗口应视为**已结束**，不再追加新问题。

- 该 Skill 会**全量总结**当前对话的全部内容
- 若总结后再追加问题并二次总结，前部分内容会被重复处理，浪费 token
- 这也违背了复盘的本质——复盘是对"已完成"的回顾，既已完成，不应再有后续

### 3. 触发时机

该 Skill 的设计意图是**阶段性收尾**，适合在以下时机使用：

- ✅ 一天工作结束时
- ✅ 某个任务/功能完成时
- ✅ 一次完整的问题排查结束时
- ❌ 对话中途（尚未形成完整上下文）
- ❌ 刚开始一个问题时

---

## 快速使用

### 1. 安装 Skill

#### Cursor

```bash
# macOS / Linux
cp -r conversation-review ~/.cursor/skills/conversation-review

# Windows (PowerShell)
Copy-Item -Recurse -Force conversation-review "$env:USERPROFILE\.cursor\skills\conversation-review"
```

#### Claude Code

```bash
# macOS / Linux
cp -r conversation-review ~/.claude/skills/conversation-review

# Windows (PowerShell)
Copy-Item -Recurse -Force conversation-review "$env:USERPROFILE\.claude\skills\conversation-review"
```

#### Codex

```bash
# macOS / Linux
cp -r conversation-review ~/.codex/skills/conversation-review

# Windows (PowerShell)
Copy-Item -Recurse -Force conversation-review "$env:USERPROFILE\.codex\skills\conversation-review"
```

### 2. 在对话中触发

- `/conversation-review`
- 「帮我做对话回顾」
- 「分析一下这次对话」

### 3. 查看报告

报告生成在当前工作目录下：

```
conversation-reviews/
└── review-YYYYMMDD-HHmmss.md
```

## 效果示例

对话回顾报告示例（[查看完整示例](conversation-review/examples/review-20260801-153000.md)）：

```markdown
# 对话回顾 · 2026-08-01 15:30

> **Source**: [conversation-review-skills](https://github.com/wangguoxi0814/conversation-review-skills)

---

## 问题列表

1. **SQLAlchemy 中 flush 和 commit 的区别，以及事务何时提交**
   > 原问题：「这里为什么要flush」「那这里的插入什么时候执行commit」

   关键点：
   - `flush`：将 SQL 发送到数据库执行，但**不提交事务**
   - `commit`：先 flush 再提交事务，数据对其他事务可见
   - 事务由 `create_session` 依赖统一管理：路由正常结束自动 commit

2. **FastAPI yield 依赖注入的实现原理**

   > 原问题：「这个原理是怎么实现的，为什么是先返回数据，然后再yield处恢复」

   > 引用：`app/dependencies.py:15-28`

   关键点：
   - `yield` 让函数变成生成器，执行到 yield 暂停并保存现场
   - FastAPI 通过 `next(gen)` 获取 yield 的值，路由结束后再次 `next(gen)` 恢复执行

3. **lifespan 生命周期函数与 @asynccontextmanager**
   > 原问题：「lifespan是干嘛的，@asynccontextmanager又是干嘛的」「一个服务只能有一个lifespan函数是吗」

   关键点：
   - `lifespan`：FastAPI 的启动/关闭钩子
   - 一个应用只能注册一个 lifespan，组合多个用 `AsyncExitStack`
```

## 核心功能

| 功能 | 说明 |
|------|------|
| **自动捕获** | 从对话中提取用户问题，无需手动记录 |
| **意图分析** | 结合问答内容，理解用户真正想了解什么 |
| **合并追问** | 同一主题的连续追问合并为一条，避免碎片化 |
| **关键点记录** | 从 AI 回答中提炼核心要点，回顾时不遗忘 |
| **原话保留** | 用户原话以「原问题」引用形式保留，还原上下文 |
| **代码引用** | 记录选中代码的文件路径和行号，回顾时快速定位 |

## 目录结构

```
conversation-review/
├── SKILL.md                      # 工作流与规则
├── references/
│   └── structure.md              # 报告内容结构
└── examples/
    └── review-20260801-153000.md # 示例报告
```

---

更多细节见 [`conversation-review/SKILL.md`](conversation-review/SKILL.md)。
