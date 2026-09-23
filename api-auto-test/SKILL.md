---
name: api-auto-test
description: 自动化接口功能测试：产物统一在 http/{controller_name}/（含 .http 与 REPORT）；步骤3经 MySQL MCP 逐条执行造数 SQL 并失败修正；步骤4行级校验；步骤5只改 REPORT。在用户提到接口测试、API 冒烟、写 .http、造测试数据、行级校验，或显式 @api-auto-test 时使用。
disable-model-invocation: true
---

# 自动化接口测试

全程使用**中文**沟通、写用例注释与报告。

## 路径约定（强制）

均相对**当前工作区根目录**。每个 Controller **一个目录**，`.http` 与分析/测试产物**同目录**：

| 产物 | 路径 |
|------|------|
| Controller 目录 | `http/{controller_name}/` |
| `.http` 用例文件 | `http/{controller_name}/{controller_name}.http` |
| **分析/报告一体** | `http/{controller_name}/REPORT.md`（步骤3创建，步骤5只改此文件） |
| 辅助产物 | 同目录：`analysis-cache.json`、`rowcheck-config.json`、`rowcheck-results.json` |

禁止把 `.http` 与 REPORT 拆到不同父目录（例如禁止 `http/Foo.http` + `http/api-auto-test/Foo/REPORT.md`）。

## 流程总览

```
任务进度：
- [ ] 步骤1：确认测试范围
- [ ] 步骤2：确定 .http 产物形态（读模板）
- [ ] 步骤3：分析 → 写 .http + REPORT → MCP 逐条执行造数 SQL（失败则改 SQL）
- [ ] 步骤4：固定运行通用行级校验脚本
- [ ] 步骤5：只修改 REPORT.md，补全实际结果与状态
```

未完成步骤1前，禁止写用例、造数或打写接口。

---

## 步骤1：确认测试范围

向用户确认：

| 维度 | 示例 |
|------|------|
| 目录 / 文件 / 路径 | `http/`、`AuthController`、`POST /api/auth/login` |
| 环境 | Base URL、是否允许写操作、鉴权来源 |
| 造数 | 是否允许 MCP 写库造数（仅测试/预发） |
| 复用 | 默认按 commit 复用；用户可指定「重新分析」 |

输出确认摘要后再继续。

---

## 步骤2：确定 .http 产物形态

**一 Controller 一目录一文件**：`http/{controller_name}/{controller_name}.http`。

生成或改写前**只读取**：[references/http-file-template.md](references/http-file-template.md)。

---

## 步骤3：逐接口深度分析 → `.http` + `REPORT.md` + MCP 造数

### 3.1 Commit 增量复用（先做）

读取 [references/analysis-cache.md](references/analysis-cache.md)：

1. 取当前分支 `HEAD` commit。
2. 若缓存存在且 `cached_commit == HEAD`，且用户**未**指定重新分析 → **复用**已有目录产物；造数 SQL 若标记可复用则先 `SELECT` 校验，不齐再 MCP 执行；然后步骤4。
3. 若用户指定重新分析，或有新提交：
   - `git diff cached_commit..HEAD` 定位变更；
   - **分析变更代码的调用链路**，判定相关联接口；
   - **仅**对关联接口重做 3.2–3.6；其余复用；
   - 更新 `cached_commit`。

### 3.2 逐接口分析

对范围内**每一个**接口：读 Controller → Service → 校验/状态机/权限/落库，理解业务意图，设计高覆盖场景。

### 3.3 写入 `.http`

路径：`http/{controller_name}/{controller_name}.http`  
用例 id：`{Controller类名}_{case_id}`；格式见模板。

### 3.4 写入分析结构到 `REPORT.md`

路径：`http/{controller_name}/REPORT.md`  
模板：[references/report-template.md](references/report-template.md)。

每用例含：接口功能、用例意图、造数记录（逻辑 + SQL）、期望、实际（待测）、状态=`PENDING`。  
「接口一览」须含分类小节；步骤3将全部用例列入 **待测（PENDING）**，成功/失败/跳过写「无」。

### 3.5 用 MySQL MCP **逐条**执行造数 SQL（强制）

对 REPORT 中每条需执行的造数 SQL（按语句拆分，**一条一条**调用 MCP `mysql_query`）：

1. 先执行；成功则在该造数节标记「MCP 已执行：成功」与时间。
2. **若报错**：根据错误（字段类型、FK、唯一键、NOT NULL 等）调整 SQL → **写回 REPORT** → 再 MCP 执行；循环直至成功或确认为环境不可达。
3. MCP 无写权限 / 认证失败：停止，请用户开启写权限后继续；不得跳过静默。
4. 可复用：先 `SELECT` 校验业务键；已满足则跳过 INSERT，仍记录「复用已有行」。

细则：[references/test-data-seed-log.md](references/test-data-seed-log.md)。

### 3.6 更新 `analysis-cache.json`

同目录写入/更新，含 `cached_commit`、用例 id 列表、`.http` / `REPORT` 路径。

---

## 步骤4：固定运行通用行级校验脚本

```bash
python scripts/run_api_rowcheck.py --config http/{controller_name}/rowcheck-config.json
```

说明：[references/run-rowcheck.md](references/run-rowcheck.md)。产出同目录 `rowcheck-results.json`。

判定枚举：[references/result-status.md](references/result-status.md)。

---

## 步骤5：只修改 `REPORT.md`

**不要新建另一份报告。** 根据 `rowcheck-results.json` **原地补全**同目录 `REPORT.md`：

1. 各用例「实际测试结果」与状态（PASS / FAIL / SKIP）
2. 文首汇总计数（与下列分类一致）
3. **「接口一览」按状态分类重写**：`### 成功（PASS）` / `### 失败（FAIL）` / `### 跳过（SKIP）`；清空「待测」；无条目写「无」（模板见 [references/report-template.md](references/report-template.md)）
4. FAIL 时的失败反馈

---

## 工具与安全

- 造数写库：**必须**走 MySQL MCP 逐条执行（步骤3.5）；失败则改 SQL 并更新 REPORT。
- 鉴权与报告脱敏；生产禁止写接口/写库。

## 额外资源

- [references/http-file-template.md](references/http-file-template.md)
- [references/report-template.md](references/report-template.md)
- [references/analysis-cache.md](references/analysis-cache.md)
- [references/run-rowcheck.md](references/run-rowcheck.md)
- [references/result-status.md](references/result-status.md)
- [references/test-data-seed-log.md](references/test-data-seed-log.md)
- [references/mysql-check-template.md](references/mysql-check-template.md)
