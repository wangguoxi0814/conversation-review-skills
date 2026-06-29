---
name: conversation-review
description: >-
  回顾当前对话框对话，提取用户问题，进行大领域-子领域二级分类与打标签，识别多轮追问盲区，
  映射触达源码文件，输出统计、学习路径、Anki 闪卡、HTML 报告与行动项。
  当用户要求对话回顾、学习复盘、知识盲区分析、问题归纳统计，或调用 /conversation-review 时使用。
---

# Conversation Review

**仅分析当前对话框**，不读取 `agent-transcripts`，不做跨会话分析。

## 输出语言

面向用户的输出（Markdown 报告、HTML 文案、Anki 闪卡、行动项、学习路径）**与用户在本对话中使用的主要语言保持一致**。

- 中文对话 → 全中文
- 英文对话 → 全英文
- 中英混用 → 以最近几轮使用更多的语言为准

## 工作流程

```
回顾进度：
- [ ] 1. 提取用户问题
- [ ] 2. 识别多轮盲区线程
- [ ] 3. 二级分类 + 打标签
- [ ] 4. 映射触达源码文件
- [ ] 5. 统计归纳
- [ ] 6. 分析提问演变
- [ ] 7. 撰写 Markdown 报告
- [ ] 8. 生成 HTML 可视化报告
- [ ] 9. 生成 Anki 闪卡
- [ ] 10. 持久化并列出行动项
```

### 步骤 1 — 提取用户问题

- 仅包含**用户**消息；跳过纯应答（`好的`、`继续`、`ok`、`thanks`）
- 连续追问同一意图合并为一个**问题单元**
- 引用时保留用户原话

### 步骤 2 — 多轮盲区识别

满足任一条件标记为**重大盲区**：

| 信号 | 规则 |
|------|------|
| 长线程 | 同一主题 ≥ 3 轮仍未收敛 |
| 换说法重复 | 不同表述反复问同一概念 |
| 深度升级 | 「怎么用」→「为什么报错」→「底层原理」 |
| 未解决追问 | Agent 已回答，用户仍不理解或再次追问 |

### 步骤 3 — 分类与打标签

AI 实时判别，详见 [references/taxonomy-guide.md](references/taxonomy-guide.md)。

格式：`大领域 > 子领域 | 标签1, 标签2`

### 步骤 4 — 映射触达源码文件

收集对话中**阅读、编辑、搜索或讨论**的文件；盲区关联应 revisit 的源码；未触达则推断并标注 `(推断)`。

### 步骤 5 — 统计归纳

产出问题单元总数、大领域/子领域/标签次数、Top 3 主题、多轮盲区数。

### 步骤 6 — 提问演变

每个主要主题一句话：是否从模糊走向精准，或仍在重复。

### 步骤 7 — Markdown 报告

模板见 [references/examples.md](references/examples.md)。语言与用户对话一致。

### 步骤 8 — HTML 可视化报告

**不使用 Canvas**。按以下流程生成 HTML：

1. 将本次分析结果整理为 JSON（schema 见 [references/structure.md](references/structure.md)）
2. 持久化：`python scripts/append-review.py --stdin` 或 `--file review.json`
3. 生成报告：`python scripts/generate-report.py --output <path>/conversation-review.html`
4. 在聊天中给出 HTML 文件的完整绝对路径，提示用户在浏览器打开

HTML 基于 [assets/report-template.html](assets/report-template.html)，支持**全部 / 本周 / 本月**时间范围切换（详见模板内 Filter 逻辑）。

每条 review 记录必须包含 ISO 8601 时间戳 `timestamp`，供时间筛选使用。

### 步骤 9 — Anki 闪卡

针对重大盲区生成 3–8 张。格式见 [references/anki-format.md](references/anki-format.md)。

### 步骤 10 — 行动项

具体、可在一个 sitting 内完成；避免空泛表述。

## 输出顺序

1. Markdown 报告（聊天内）
2. HTML 报告路径
3. Anki CSV 代码块
4. 行动项清单

## 目录与资源

| 路径 | 用途 |
|------|------|
| [references/structure.md](references/structure.md) | Skill 架构与 JSON Schema |
| [references/taxonomy-guide.md](references/taxonomy-guide.md) | 分类与标签规则 |
| [references/anki-format.md](references/anki-format.md) | Anki 导出格式 |
| [references/examples.md](references/examples.md) | 输入/输出示例 |
| [references/hook-setup.md](references/hook-setup.md) | 可选 Hook 自动触发 |
| [assets/report-template.html](assets/report-template.html) | HTML 报告模板 |
| [scripts/append-review.py](scripts/append-review.py) | 追加 review 到本地 datastore |
| [scripts/generate-report.py](scripts/generate-report.py) | 渲染 HTML 报告 |

数据存储默认路径：`~/.cursor/skills/conversation-review/data/reviews.json`
