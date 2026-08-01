# Conversation Review — 目录结构

## 总览

```
conversation-review/
├── SKILL.md                          # 主入口：工作流与触发说明
├── scripts/
│   ├── append-review.py              # 追加待办项组到全局 JSON
│   └── generate-report.py            # 渲染 HTML 报告
├── references/
│   └── structure.md                  # 本文件：架构与 Schema
├── assets/
│   └── report-template.html          # HTML 报告模板（含 CSS/JS）
└── data/                             # 运行时在当前工作目录下生成
    └── todos.json                    # 全局待办项数据

当前工作目录（运行时生成）：
├── data/
│   ├── todos.json                    # 全局待办项数据
│   └── conversation-review.html      # 生成的 HTML 报告
```

## 设计原则

| 原则 | 说明 |
|------|------|
| 范围 | 仅当前对话框；不读 agent-transcripts |
| 可视化 | HTML 报告，支持交互勾选 |
| 语言 | 输出与用户对话语言一致 |
| 持久化 | 全局单文件 `todos.json`，HTML 增量追加 |
| 交互性 | 勾选存档、双击编辑、分组折叠 |

## JSON Schema

### 全局待办项文件 `data/todos.json`

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
          "text": "阅读 ArrayList.add 源码三步操作，理解扩容机制",
          "done": false
        },
        {
          "id": "t-002",
          "text": "修复 UserService 中 @Transactional 边界问题",
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
| `groups` | array | 待办项组数组，按时间升序存储 |
| `groups[].id` | string | 唯一标识，格式 `YYYYMMDD-HHmmss` |
| `groups[].timestamp` | string | ISO 8601 生成时间 |
| `groups[].title` | string | 组标题，默认为生成时间，用户可编辑 |
| `groups[].todos` | array | 待办项数组 |
| `groups[].todos[].id` | string | 待办项唯一标识 |
| `groups[].todos[].text` | string | 待办项内容，保留问题关键信息 |
| `groups[].todos[].done` | boolean | 是否完成，HTML 中可交互勾选 |

## 脚本用法

### append-review.py

```bash
# 从 stdin 读取 JSON（在项目根目录执行）
echo '{"title":"...","todos":[...]}' | python conversation-review/scripts/append-review.py --stdin

# 从文件读取
python conversation-review/scripts/append-review.py --file review.json
```

输入 JSON 格式：
```json
{
  "title": "可选标题，默认为当前时间",
  "todos": [
    "待办项1的文本",
    "待办项2的文本"
  ]
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
| 折叠交互 | 每组可展开/收缩，默认最近一组展开 |
| 勾选存档 | 点击勾选框标记完成，状态保存在 localStorage |
| 双击编辑 | 双击待办项文本可编辑内容 |
| 来源标注 | 底部显示 git 仓库地址和生成时间 |
| 响应式设计 | 适配桌面和移动端 |

## 交互状态存储

HTML 报告使用 `localStorage` 存储：
- 待办项完成状态：`cr_done_{groupId}_{todoId}` → `true/false`
- 编辑后的文本：`cr_text_{groupId}_{todoId}` → 新文本
- 折叠状态：`cr_collapsed_{groupId}` → `true/false`
