#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用 API 行级校验脚本（api-auto-test Skill）。

用法:
  python scripts/run_api_rowcheck.py --config path/to/rowcheck-config.json

配置 JSON 最小结构:
{
  "baseUrl": "http://127.0.0.1:8990/app",
  "output": "http/AuthController/rowcheck-results.json",
  "login": { "path": "/api/auth/admin/login", "body": { "email": "...", "password": "..." } },
  "cases": [
    {
      "id": "AuthController_login_ok",
      "method": "POST",
      "path": "/api/auth/admin/login",
      "headers": {},
      "body": {},
      "auth": false,
      "seed_sqls": ["..."],
      "rowcheck_sql": "SELECT * FROM t_users WHERE id = %s",
      "rowcheck_args": [1],
      "expect_http_status": [200]
    }
  ]
}

环境变量可覆盖 DB 与 Base URL:
  API_AUTO_TEST_BASE_URL, API_AUTO_TEST_DB_HOST, API_AUTO_TEST_DB_PORT,
  API_AUTO_TEST_DB_USER, API_AUTO_TEST_DB_PASSWORD, API_AUTO_TEST_DB_DATABASE
"""
from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any


def _env(name: str, default: str | None = None) -> str | None:
    v = os.environ.get(name)
    return v if v not in (None, "") else default


def freeze(value: Any) -> Any:
    if value is None:
        return None
    if hasattr(value, "isoformat"):
        try:
            return value.isoformat(sep=" ", timespec="seconds")
        except TypeError:
            return value.isoformat()
    if isinstance(value, dict):
        return {str(k): freeze(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [freeze(v) for v in value]
    if isinstance(value, (bytes, bytearray)):
        return value.decode("utf-8", errors="replace")
    return value


def row_diff(before: dict | None, after: dict | None) -> list[dict[str, Any]]:
    diffs: list[dict[str, Any]] = []
    if before is None and after is None:
        return diffs
    if before is None and after is not None:
        return [{"op": "added_row", "after": after}]
    if before is not None and after is None:
        return [{"op": "removed_row", "before": before}]
    assert before is not None and after is not None
    keys = sorted(set(before) | set(after))
    for k in keys:
        bv, av = before.get(k), after.get(k)
        if k not in before:
            diffs.append({"op": "added", "field": k, "before": None, "after": av})
        elif k not in after:
            diffs.append({"op": "removed", "field": k, "before": bv, "after": None})
        elif bv != av:
            diffs.append({"op": "changed", "field": k, "before": bv, "after": av})
    return diffs


def http_json(
    base_url: str,
    method: str,
    path: str,
    token: str | None = None,
    headers: dict | None = None,
    body: Any = None,
    timeout: float = 45.0,
) -> tuple[int, Any, str, float]:
    url = base_url.rstrip("/") + path
    hdrs = {
        "Accept": "application/json",
        "User-Agent": "api-auto-test-rowcheck/1.0",
    }
    if headers:
        hdrs.update({k: str(v) for k, v in headers.items()})
    data = None
    if body is not None:
        if "Content-Type" not in hdrs and "content-type" not in {k.lower() for k in hdrs}:
            hdrs["Content-Type"] = "application/json"
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    if token:
        hdrs["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=data, headers=hdrs, method=method.upper())
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            ms = (time.perf_counter() - t0) * 1000
            try:
                return resp.status, json.loads(raw) if raw else None, raw, ms
            except json.JSONDecodeError:
                return resp.status, None, raw, ms
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        ms = (time.perf_counter() - t0) * 1000
        try:
            return e.code, json.loads(raw) if raw else None, raw, ms
        except json.JSONDecodeError:
            return e.code, None, raw, ms
    except Exception as e:  # noqa: BLE001
        return 0, None, str(e), (time.perf_counter() - t0) * 1000


def connect_db(cfg: dict[str, Any]):
    try:
        import pymysql
    except ImportError as e:
        raise SystemExit("需要安装 pymysql: pip install pymysql") from e
    db = cfg.get("db") or {}
    return pymysql.connect(
        host=_env("API_AUTO_TEST_DB_HOST", db.get("host", "127.0.0.1")),
        port=int(_env("API_AUTO_TEST_DB_PORT", str(db.get("port", 3306)))),
        user=_env("API_AUTO_TEST_DB_USER", db.get("user", "root")),
        password=_env("API_AUTO_TEST_DB_PASSWORD", db.get("password", "")),
        database=_env("API_AUTO_TEST_DB_DATABASE", db.get("database", "")),
        charset=db.get("charset", "utf8mb4"),
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )


def exec_sqls(conn, sqls: list[str] | None) -> None:
    if not sqls:
        return
    with conn.cursor() as cur:
        for sql in sqls:
            s = (sql or "").strip()
            if not s:
                continue
            cur.execute(s)


def fetch_rows(conn, sql: str | None, args: list | None) -> list[dict]:
    if not sql:
        return []
    with conn.cursor() as cur:
        cur.execute(sql, args or ())
        rows = cur.fetchall() or []
        return [freeze(dict(r)) for r in rows]


def unwrap_token(parsed: Any) -> str | None:
    if not isinstance(parsed, dict):
        return None
    # nested data or flat body
    data = parsed.get("data") if isinstance(parsed.get("data"), dict) else parsed
    if not isinstance(data, dict):
        return None
    tok = data.get("access_token") or data.get("accessToken") or parsed.get("access_token") or parsed.get("accessToken")
    return str(tok) if tok else None


def run_case(conn, base_url: str, token: str | None, case: dict[str, Any]) -> dict[str, Any]:
    case_id = case.get("id") or "unknown"
    if case.get("skip"):
        return {"id": case_id, "result": "SKIP", "reason": case.get("skip_reason") or "skipped"}

    exec_sqls(conn, case.get("seed_sqls"))
    before = fetch_rows(conn, case.get("rowcheck_sql"), case.get("rowcheck_args"))

    use_auth = case.get("auth", True)
    st, parsed, raw, ms = http_json(
        base_url,
        case.get("method", "GET"),
        case["path"],
        token=token if use_auth else None,
        headers=case.get("headers"),
        body=case.get("body"),
    )
    after = fetch_rows(conn, case.get("rowcheck_sql"), case.get("rowcheck_args"))

    # 单行优先；多行则按 index 对齐做 diff 列表
    diffs: list[Any] = []
    if len(before) <= 1 and len(after) <= 1:
        diffs = row_diff(before[0] if before else None, after[0] if after else None)
    else:
        n = max(len(before), len(after))
        for i in range(n):
            b = before[i] if i < len(before) else None
            a = after[i] if i < len(after) else None
            d = row_diff(b, a)
            if d:
                diffs.append({"index": i, "diff": d})

    expect_status = case.get("expect_http_status") or [200]
    biz_code = None
    if isinstance(parsed, dict) and "code" in parsed:
        try:
            biz_code = int(parsed.get("code"))
        except (TypeError, ValueError):
            biz_code = parsed.get("code")

    # 本项目常见：HTTP 始终 200，业务码在 body.code（401/403/422/400）
    ok_http = st in expect_status
    ok_biz = biz_code in expect_status if biz_code is not None else False
    ok = ok_http or (st == 200 and ok_biz)
    result = "PASS" if ok else "FAIL"
    reason = None
    if not ok:
        reason = f"HTTP {st} biz={biz_code} not in {expect_status}"
    return {
        "id": case_id,
        "method": case.get("method", "GET"),
        "path": case.get("path"),
        "http_status": st,
        "biz_code": biz_code,
        "elapsed_ms": round(ms, 1),
        "response_preview": (raw or "")[:800],
        "before_rows": before,
        "after_rows": after,
        "diff": diffs,
        "result": result,
        "reason": reason,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="api-auto-test generic row-level checker")
    ap.add_argument("--config", required=True, help="rowcheck-config.json path")
    args = ap.parse_args()
    cfg_path = Path(args.config)
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))

    base_url = _env("API_AUTO_TEST_BASE_URL", cfg.get("baseUrl") or cfg.get("base_url"))
    if not base_url:
        raise SystemExit("缺少 baseUrl / API_AUTO_TEST_BASE_URL")

    conn = connect_db(cfg)
    token = cfg.get("token") or _env("API_AUTO_TEST_TOKEN")
    login = cfg.get("login")
    if not token and login:
        st, parsed, raw, _ = http_json(
            base_url,
            login.get("method", "POST"),
            login["path"],
            body=login.get("body"),
            headers=login.get("headers"),
        )
        token = unwrap_token(parsed)
        if not token:
            raise SystemExit(f"login failed {st}: {raw[:300]}")

    results = []
    for case in cfg.get("cases") or []:
        results.append(run_case(conn, base_url, token, case))

    conn.close()

    out = {
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "baseUrl": base_url,
        "config": str(cfg_path),
        "summary": {
            "total": len(results),
            "pass": sum(1 for r in results if r["result"] == "PASS"),
            "fail": sum(1 for r in results if r["result"] == "FAIL"),
            "skip": sum(1 for r in results if r["result"] == "SKIP"),
        },
        "results": results,
    }
    out_path = Path(cfg.get("output") or (cfg_path.parent / "rowcheck-results.json"))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(out["summary"], ensure_ascii=False))
    print(f"wrote {out_path}")
    return 0 if out["summary"]["fail"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
