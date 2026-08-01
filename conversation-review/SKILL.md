---
name: conversation-review
description: >-
  回顾当前对话内容，提取待办事项并增量生成 HTML 回顾报告。
  待办项原子化存储于全局 JSON，HTML 支持交互勾选存档。
  当用户要求对话回顾、学习复盘、或调用 /conversation-review 时使用。
---

# Conversation Review

**仅分析当前对话框**，不读取 `agent-transcripts`，不做跨会话分析。

## 输出语言

面向用户的输出**与用户在本对话中使用的主要语言保持一致**。

## 工作流程

```
回顾进度：
- [ ] 1. 提取待办事项
- [ ] 2. 持久化待办项到全局 JSON
- [ ] 3. 生成增量 HTML 报告
```

### 步骤 1 — 提取待办事项

从当前对话中提取**用户待办事项**，遵循以下原则：

| 原则 | 说明 |
|------|------|
| 原子性 | 每个待办项是一个独立可执行的动作 |
| 关键信息 | 保留问题上下文，用户看到待办项就能回忆起背景 |
| 可行动 | 避免空泛表述，具体到可在一个 sitting 内完成 |
| 跳过应答 | 跳过纯应答（`好的`、`继续`、`ok`、`thanks`） |

待办项格式：
```
[动作动词] + [具体对象] + [可选上下文]
```

示例：
- ✅ `阅读 ArrayList.add 源码三步操作，理解扩容机制`
- ✅ `修复 UserService 中 @Transactional 边界问题`
- ❌ `学习 Java`（太宽泛）
- ❌ `看看代码`（缺乏具体对象）

### 步骤 2 — 持久化待办项

将提取的待办项追加到全局 JSON 文件（当前工作目录下 `data/todos.json`）：

```bash
python conversation-review/scripts/append-review.py --stdin
# 或
python conversation-review/scripts/append-review.py --file review.json
```

每组待办项包含：
- `id`: 唯一标识
- `timestamp`: ISO 8601 生成时间
- `title`: 组标题（默认为生成时间，用户可编辑）
- `todos`: 待办项数组，每项包含 `id`、`text`、`done`

### 步骤 3 — 生成 HTML 报告

```bash
python conversation-review/scripts/generate-report.py
# 默认输出到当前工作目录的 data/conversation-review.html
```

HTML 报告特性：
- **全局单文件**：所有历史待办项聚合在一个 HTML 中
- **按时间分组**：每组可展开/收缩，倒序排列
- **交互勾选**：勾选完成的待办项，状态保存在 localStorage
- **可编辑**：双击待办项文本可编辑
- **来源标注**：底部标注 git 仓库地址和生成时间

在聊天中给出 HTML 文件的完整绝对路径，提示用户在浏览器打开。

## 输出顺序

1. Markdown 摘要（聊天内，简要说明本次提取的待办项）
2. HTML 报告路径

## 目录与资源

| 路径 | 用途 |
|------|------|
| [references/structure.md](references/structure.md) | 架构与 JSON Schema |
| [assets/report-template.html](assets/report-template.html) | HTML 报告模板 |
| [scripts/append-review.py](scripts/append-review.py) | 追加待办项到全局 JSON |
| [scripts/generate-report.py](scripts/generate-report.py) | 渲染 HTML 报告 |

数据存储路径：`<当前工作目录>/data/todos.json`
