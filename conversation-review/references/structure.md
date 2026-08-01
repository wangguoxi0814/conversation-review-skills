# Conversation Review — 目录结构

## 总览

```
conversation-review/
├── SKILL.md                          # 主入口：工作流与触发说明
├── scripts/
│   ├── append-review.py              # 追加问题组到全局 JSON
│   └── generate-report.py            # 渲染 HTML 报告
├── references/
│   └── structure.md                  # 本文件：架构与 Schema
├── assets/
│   └── report-template.html          # HTML 报告模板（含 CSS/JS）
└── data/                             # 运行时在当前工作目录下生成
    └── todos.json                    # 全局问题数据

当前工作目录（运行时生成）：
├── data/
│   ├── todos.json                    # 全局问题数据
│   └── conversation-review.html      # 生成的 HTML 报告
```

## 设计原则

| 原则 | 说明 |
|------|------|
| 范围 | 仅当前对话框；不读 agent-transcripts |
| 自动捕获 | 从对话中提取用户问题 |
| 保留原话 | `original` 字段记录用户原始表述 |
| 适当补充 | `text` 字段补充关键词使意思清晰 |
| 用户专注 | 用户专心对话，无需手动记录 |
| 可视化 | HTML 报告，支持交互勾选 |
| 语言 | 输出与用户对话语言一致 |
| 持久化 | 全局单文件 `todos.json`，HTML 增量追加 |
| 交互性 | 勾选存档、双击编辑、分组折叠 |

## 问题捕获规则

从对话中识别用户问题，同时记录原话和补充后的内容：

| 用户原话 (`original`) | 存储内容 (`text`) | 补充说明 |
|----------------------|------------------|---------|
| "左连接、右连接、全外连接的区别是什么？" | 左连接、右连接、全外连接的区别是什么？ | 原话已清晰 |
| "volatile 为啥不行" | volatile 为什么不能保证原子性？ | 补充"保证原子性" |
| "那个注解怎么用" | @Transactional 注解怎么用？ | 补充具体注解名 |
| "继续" | *(跳过)* | 纯应答，不记录 |

## JSON Schema

### 全局问题文件 `data/todos.json`

```json
{
  "version": 1,
  "groups": [
    {
      "id": "20260730-143022",
      "timestamp": "2026-07-30T14:30:22+08:00",
      "title": "2026-07-30 14:30",
      "todos": [
        {
          "id": "t-001",
          "text": "左连接、右连接、全外连接的区别是什么？",
          "original": "左连接、右连接、全外连接的区别是什么？",
          "done": false
        },
        {
          "id": "t-002",
          "text": "volatile 为什么不能保证原子性？",
          "original": "volatile 为啥不行",
          "done": false
        }
      ]
    }
  ]
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `version` | number | 数据格式版本，当前为 1 |
| `groups` | array | 问题组数组，按时间升序存储 |
| `groups[].id` | string | 唯一标识，格式 `YYYYMMDD-HHmmss` |
| `groups[].timestamp` | string | ISO 8601 生成时间 |
| `groups[].title` | string | 组标题，默认为生成时间，用户可编辑 |
| `groups[].todos` | array | 问题数组 |
| `groups[].todos[].id` | string | 问题唯一标识 |
| `groups[].todos[].text` | string | 补充关键词后的清晰表述（主要展示） |
| `groups[].todos[].original` | string | 用户原话（引用形式展示） |
| `groups[].todos[].done` | boolean | 是否已回顾，HTML 中可交互勾选 |

## 脚本用法

### append-review.py

```bash
# 从 stdin 读取 JSON（在项目根目录执行）
echo '{"title":"...","questions":[...]}' | python conversation-review/scripts/append-review.py --stdin

# 从文件读取
python conversation-review/scripts/append-review.py --file review.json
```

输入 JSON 格式：
```json
{
  "title": "可选标题，默认为当前时间",
  "questions": [
    {
      "original": "用户原话",
      "text": "补充关键词后的清晰表述"
    }
  ]
}
```

也支持简写形式（自动将 text 复制到 original）：
```json
{
  "questions": ["问题文本"]
}
```

### generate-report.py

```bash
# 在项目根目录执行，默认输出到 data/conversation-review.html
python conversation-review/scripts/generate-report.py

# 指定输出路径
python conversation-review/scripts/generate-report.py --output ~/Desktop/conversation-review.html
```

## HTML 报告功能

基于 `assets/report-template.html`：

| 功能 | 说明 |
|------|------|
| 分组展示 | 按触发时间分组，倒序排列 |
| 主次展示 | 主要展示 `text`，`original` 以引用形式出现 |
| 折叠交互 | 每组可展开/收缩，默认最近一组展开 |
| 勾选存档 | 点击勾选框标记已回顾，状态保存在 localStorage |
| 双击编辑 | 双击问题文本可编辑内容 |
| 来源标注 | 底部显示 git 仓库地址和生成时间 |
| 响应式设计 | 适配桌面和移动端 |

## 交互状态存储

HTML 报告使用 `localStorage` 存储：
- 问题完成状态：`cr_done_{groupId}_{todoId}` → `true/false`
- 编辑后的文本：`cr_text_{groupId}_{todoId}` → 新文本
- 折叠状态：`cr_collapsed_{groupId}` → `true/false`
