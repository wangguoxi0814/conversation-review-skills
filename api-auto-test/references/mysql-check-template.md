# mysql-check.md 模板（完整行 + 差异）

步骤5 可选附录。路径：`http/{controller_name}/mysql-check.md`。人读结论以同目录 `REPORT.md` 为准。

每个用例必须保留 **before 完整行**、**after 完整行**、**字段差异**。

````markdown
# {module} MySQL 行级核对

## CommunityEventController_update_approved_ok

- rowcheck_sql：`SELECT * FROM t_community_event WHERE id = 99901`

### before（完整行）

```json
{ "id": 99901, "title": "api-auto-test-seed-event", "status": 1, "...": "..." }
```

### after（完整行）

```json
{ "id": 99901, "title": "api-auto-test-updated", "status": 1, "...": "..." }
```

### diff

| op | field | before | after |
|---|---|---|---|
| changed | title | api-auto-test-seed-event | api-auto-test-updated |

- 结论：与用例意图一致 / 不一致
````
