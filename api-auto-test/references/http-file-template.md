# .http 文件模板

步骤2/3 生成或改写时读取。

路径：**当前工作区** `http/{controller_name}/{controller_name}.http`  
（与 `REPORT.md`、rowcheck 产物同目录；`controller_name` = Controller 类名）

用例 id = `{Controller类名}_{case_id}`；`# @name` 与注释中的 id 一致。

```http
### 来源：AuthController | analyzed_commit: {git_sha}
@baseUrl = {{baseUrl}}
@accessToken = {{accessToken}}

### AuthController_login_ok
# @name AuthController_login_ok
# 用例id: AuthController_login_ok
# 意图: 管理员正确账号密码登录，返回 access_token
# 造数: 无
POST {{baseUrl}}/api/auth/admin/login
Content-Type: application/json

{
  "email": "{{adminEmail}}",
  "password": "{{adminPasswordMd5}}"
}
```

注意：禁止把真实长期密钥写进 Skill；multipart / 破坏性 DELETE 规则同前。
