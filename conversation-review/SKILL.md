---
name: conversation-review
description: >-
  自动捕获对话中用户提出的问题，保留原话并适当补充关键词，增量生成 HTML 回顾报告。
  用户可专注于对话，无需手动记录问题，事后统一回顾。
  当用户要求对话回顾、学习复盘、或调用 /conversation-review 时使用。
---

# Conversation Review

**自动捕获问题，保留原话，补充关键词**。用户在对话中专心提问，skill 自动记录问题，事后统一回顾。

## 输出语言

面向用户的输出**与用户在本对话中使用的主要语言保持一致**。

## 工作流程

```
回顾进度：
- [ ] 1. 捕获用户问题
- [ ] 2. 持久化到全局 JSON
- [ ] 3. 生成 HTML 报告
```

### 步骤 1 — 捕获用户问题

从当前对话中提取**用户提出的问题**，同时记录：
- `original`: 用户原话（引用形式展示）
- `text`: 补充关键词后的清晰表述（主要内容）

| 原则 | 说明 |
|------|------|
| 保留原话 | `original` 字段记录用户原始表述 |
| 适当补充 | `text` 字段在原话基础上补充关键词，使回顾时能快速理解 |
| 跳过应答 | 跳过纯应答（`好的`、`继续`、`ok`、`thanks`） |
| 合并追问 | 同一主题的连续追问合并为一条 |

**示例：**

| 用户原话 (`original`) | 存储内容 (`text`) | 补充说明 |
|----------------------|------------------|---------|
| "左连接、右连接、全外连接的区别是什么？" | 左连接、右连接、全外连接的区别是什么？ | 原话已清晰，无需补充 |
| "volatile 为啥不行" | volatile 为什么不能保证原子性？ | 补充"保证原子性"明确问题 |
| "那个注解怎么用" | @Transactional 注解怎么用？ | 补充具体注解名 |
| "继续" | *(跳过)* | 纯应答，不记录 |

### 步骤 2 — 持久化到全局 JSON

将问题追加到当前工作目录下的 `data/todos.json`：

```bash
echo '{"title":"对话回顾","questions":[{"original":"volatile 为啥不行","text":"volatile 为什么不能保证原子性？"}]}' | \
  python conversation-review/scripts/append-review.py --stdin
```

### 步骤 3 — 生成 HTML 报告

```bash
python conversation-review/scripts/generate-report.py
# 输出到 data/conversation-review.html
```

HTML 报告特性：
- **全局单文件**：所有历史问题聚合在一个 HTML 中
- **按时间分组**：每组可展开/收缩，倒序排列
- **主次展示**：主要展示补充后的清晰表述，原话以引用形式出现
- **交互勾选**：勾选已回顾的问题，状态保存在 localStorage
- **可编辑**：双击问题文本可编辑
- **来源标注**：底部标注 git 仓库地址和生成时间

在聊天中给出 HTML 文件的完整绝对路径，提示用户在浏览器打开。

## 输出顺序

1. Markdown 摘要（聊天内，列出捕获的问题）
2. HTML 报告路径

## 使用场景

**用户专心对话，skill 自动记录：**

```
用户: 左连接、右连接、全外连接的区别是什么？
AI:   [详细解答...]
用户: 那 INNER JOIN 呢？
AI:   [详细解答...]

[触发 /conversation-review]

Skill: 捕获到以下问题：
       - 左连接、右连接、全外连接的区别是什么？
       - INNER JOIN 与它们的区别？
       - HTML 报告: d:\project\data\conversation-review.html
```

## 目录与资源

| 路径 | 用途 |
|------|------|
| [references/structure.md](references/structure.md) | 架构与 JSON Schema |
| [assets/report-template.html](assets/report-template.html) | HTML 报告模板 |
| [scripts/append-review.py](scripts/append-review.py) | 追加问题到全局 JSON |
| [scripts/generate-report.py](scripts/generate-report.py) | 渲染 HTML 报告 |

数据存储路径：`<当前工作目录>/data/todos.json`
