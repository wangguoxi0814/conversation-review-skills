# 测试结果枚举

| 结果 | 含义 | 谁写入 |
|------|------|--------|
| PENDING | 已分析、尚未跑步骤4 | 步骤3 |
| PASS | HTTP 与行级结果符合期望 | 步骤5 |
| FAIL | 与期望不符 | 步骤5 |
| SKIP | 环境/手工依赖或用户禁止写 | 步骤5（或步骤3预标） |

步骤5把 `PENDING` 更新为 PASS/FAIL/SKIP；脚本 `rowcheck-results.json` 为数据源。
