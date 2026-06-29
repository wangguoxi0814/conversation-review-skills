# Conversation Review — 目录结构

## 总览

```
conversation-review/
├── SKILL.md                          # 主入口：工作流与触发说明
├── scripts/
│   ├── append-review.py              # 追加单次回顾 JSON 到 datastore
│   └── generate-report.py            # 渲染 HTML 报告
├── references/
│   ├── structure.md                  # 本文件：架构与 Schema
│   ├── taxonomy-guide.md             # 二级分类与标签规则
│   ├── anki-format.md                # Anki CSV 格式
│   ├── examples.md                   # 输入/输出示例
│   └── hook-setup.md                 # 可选 stop Hook 配置
├── assets/
│   └── report-template.html          # HTML 报告模板（含 CSS/JS）
└── data/
    └── reviews.json                  # 运行时生成，历史回顾数据
```

## 设计原则

| 原则 | 说明 |
|------|------|
| 范围 | 仅当前对话框；不读 agent-transcripts |
| 可视化 | HTML 报告，不用 Canvas |
| 语言 | 输出与用户对话语言一致；SKILL 中专有名词可用英文 |
| 时间筛选 | HTML 支持**全部 / 本周 / 本月**聚合统计 |
| 持久化 | 每次回顾写入 `data/reviews.json`，供跨次对话累积统计 |

## JSON Schema（单次 Review）

Agent 完成分析后，生成如下 JSON 并交给 `append-review.py`：

```json
{
  "id": "20260629-143022",
  "timestamp": "2026-06-29T14:30:22+08:00",
  "language": "zh",
  "summary": {
    "questionUnits": 12,
    "blindSpots": 3,
    "sourceFiles": 5,
    "domains": 4
  },
  "classifications": [
    {
      "domain": "Java",
      "subdomain": "并发",
      "tags": ["原理知识", "调试排错"],
      "count": 4
    }
  ],
  "blindSpots": [
    {
      "title": "Java > 并发 — Happens-Before",
      "turns": 4,
      "path": "volatile 用法 → 仍不对 → happens-before 是什么",
      "rootCause": "对内存可见性模型理解不完整",
      "sourceFiles": ["src/.../ConcurrentExample.java"]
    }
  ],
  "sourceMap": [
    {
      "file": "ai-x-core/.../ChatRecordServiceImpl.java",
      "question": "Spring 事务边界",
      "isBlindSpot": true,
      "inferred": true
    }
  ],
  "evolution": [
    {
      "theme": "Java 并发",
      "note": "从 API 用法逐步深入到 JMM 原理，方向正确但仍未收敛"
    }
  ],
  "learningPath": [
    "阅读《Java 并发编程实战》第 3 章内存可见性",
    "对照项目中的 ChatRecordServiceImpl 理解 @Transactional 边界"
  ],
  "actionItems": [
    "阅读 ArrayList.add 源码三步操作",
    "导入 Anki CSV 并完成一次复习"
  ],
  "anki": {
    "csv": "Front,Back,Tags\n...",
    "cards": [
      {
        "front": "volatile 能保证原子性吗？",
        "back": "不能。volatile 只保证可见性...",
        "tags": ["Java::并发", "盲区"]
      }
    ]
  }
}
```

## Datastore 格式

`data/reviews.json`：

```json
{
  "version": 1,
  "reviews": [ /* Review 对象数组，按 timestamp 升序 */ ]
}
```

## 脚本用法

### append-review.py

```bash
# 从 stdin 读取 JSON
echo '{...}' | python scripts/append-review.py --stdin

# 从文件读取
python scripts/append-review.py --file /path/to/review.json
```

### generate-report.py

```bash
# 默认输出到 data/report.html
python scripts/generate-report.py

# 指定输出路径
python scripts/generate-report.py --output ~/Desktop/conversation-review.html
```

## HTML 报告功能

基于 `assets/report-template.html`：

| 功能 | 说明 |
|------|------|
| 时间筛选 | 顶部 Filter：**全部** / **本周** / **本月** |
| 概览卡片 | 问题单元、盲区、领域、文件数（随筛选变化） |
| 领域柱状图 | 按大领域聚合 count |
| 分类表格 | 大领域 × 子领域 × 标签 |
| 盲区列表 | 多轮线程详情 |
| 源码地图 | 触达与推断文件 |
| 提问演变 | 各主题演变摘要 |

筛选逻辑（客户端 JS）：

- **全部**：所有 review 记录
- **本周**：`timestamp` 落在当前 ISO 周（周一至周日）
- **本月**：`timestamp` 年月与当前日期相同

## Hook 集成

可选用户级 `stop` Hook，follow-up 加载 `conversation-review` skill。详见 [hook-setup.md](hook-setup.md)。

## 触发方式

- 手动：`/conversation-review` 或自然语言「帮我回顾这次对话」
- 自动：配置 Hook 后会话结束时 follow-up 触发
