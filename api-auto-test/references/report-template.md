# 分析与报告一体模板（REPORT.md）

**步骤3 创建/更新本文件**（写入分析、用例、造数、期望；实测字段留空或标「待测」）。  
**步骤5 只修改本文件**（补全实际结果、用例状态、汇总统计、**按成功/失败/跳过分类刷新「接口一览」**、失败反馈），禁止另起一份报告。

路径：`http/{controller_name}/REPORT.md`

````markdown
# {controller_name} API 测试报告

- 工作区：相对根目录
- `.http`：`http/{controller_name}/{controller_name}.http`
- cached_commit：`{git_sha}`
- Base URL：`{url}`（步骤5可补）
- 汇总：通过 {n} / 失败 {m} / 跳过 {k} / 待测 {p}（步骤5更新）
- 脚本：`scripts/run_api_rowcheck.py`（步骤5）

## 接口一览

按**用例测试状态**分类（步骤3 全部列入「待测」；步骤5 按 PASS/FAIL/SKIP 重排，无则写「无」）。

### 成功（PASS）

| 用例id | Method | Path | 功能/意图摘要 |
|---|---|---|---|
| AuthController_login_ok | POST | `/api/auth/admin/login` | 管理员登录成功 |

### 失败（FAIL）

| 用例id | Method | Path | 功能/意图摘要 | 失败要点 |
|---|---|---|---|---|
| （无） | | | | |

### 跳过（SKIP）

| 用例id | Method | Path | 跳过原因 |
|---|---|---|---|
| （无） | | | |

### 待测（PENDING）

| 用例id | Method | Path | 功能/意图摘要 |
|---|---|---|---|
| （步骤5 后应为空；步骤3 在此列出全部用例） | | | |

---

## 用例：AuthController_login_ok

| 字段 | 内容 |
|------|------|
| 用例id | `AuthController_login_ok` |
| 接口 | POST `/api/auth/admin/login` |
| 接口功能 | 管理员账号密码校验通过后返回 token |
| 用例意图 | 正确凭证登录成功 |
| 状态 | `PENDING` → 步骤5改为 PASS/FAIL/SKIP |

### 造数记录

- 造数逻辑：无（使用已有测试账号）
- SQL：无
- 回滚：无

### 期望结果

- HTTP：`200`
- 响应：`data.access_token` 存在
- 库表：无强制行级变化（或写明期望 diff）

### 实际测试结果（步骤5补全）

- HTTP：
- 响应摘要：
- before 完整行：
- after 完整行：
- diff：
- 判定说明：

### 失败反馈（仅 FAIL 时步骤5填写）

- 现象：
- 根因推断：
- 建议：
````

## 字段约定

| 字段 | 步骤3 | 步骤5 |
|------|-------|-------|
| 接口功能 / 用例意图 / 造数 / 期望 | 必填 | 一般不改（除非重分析） |
| 状态 | 写 `PENDING` | 改为 PASS/FAIL/SKIP |
| **接口一览分类** | 全部放「待测」 | **必须**按成功/失败/跳过重写；待测清空 |
| 实际测试结果 | 留空或「待测」 | 必填补全 |
| 文首汇总 | 可写待测数 | 与分类表计数一致 |
| 失败反馈 | 可省略 | FAIL 时必填 |

状态枚举见 [result-status.md](result-status.md)。
