# 通用行级校验脚本

```bash
python scripts/run_api_rowcheck.py --config http/{controller_name}/rowcheck-config.json
```

配置与产出均在 `http/{controller_name}/`：`rowcheck-config.json`、`rowcheck-results.json`。

期望与造数以同目录 `REPORT.md` 为准；步骤5把结果写回该 REPORT。

环境变量：`API_AUTO_TEST_BASE_URL`、`API_AUTO_TEST_TOKEN`、`API_AUTO_TEST_DB_*`。
