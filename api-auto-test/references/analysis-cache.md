# 分析缓存与 commit 增量复用

路径：`http/{controller_name}/analysis-cache.json`。

```json
{
  "branch": "feature/xxx",
  "cached_commit": "abc1234...",
  "updated_at": "2026-09-23T03:00:00+08:00",
  "scope": "AuthController",
  "http_files": ["http/AuthController/AuthController.http"],
  "report_file": "http/AuthController/REPORT.md",
  "case_ids": ["AuthController_login_ok"]
}
```

## 复用规则

| 条件 | 行为 |
|------|------|
| `cached_commit == HEAD` 且未要求重新分析 | 复用同目录 `.http` + `REPORT.md`；造数先 SELECT 校验，缺则 MCP 逐条补 |
| 用户「重新分析」 | 重写分析段 + 按需重跑 MCP 造数 |
| 有新提交 | diff → **调用链路**判定关联接口 → 仅重做这些接口 |

关联接口：向上追 Controller，向下看语义影响。
