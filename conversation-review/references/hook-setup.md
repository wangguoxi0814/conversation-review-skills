# 可选 Hook — 会话结束自动触发

**范围：** 用户级 `~/.cursor/`，所有项目。  
**限制：** 仅聊天上下文仍可用时有效。

## PowerShell 脚本

`~/.cursor/hooks/conversation-review-followup.ps1`：

```powershell
$payload = @{
  followup_message = "请加载 conversation-review skill，对本次对话做学习回顾：分类统计、盲区分析、源码映射、HTML 报告、Anki 闪卡与行动项。输出语言与用户对话语言保持一致。若对话过短（仅 1-2 轮寒暄），回复「对话过短，跳过回顾」即可。"
} | ConvertTo-Json -Compress
Write-Output $payload
exit 0
```

## hooks.json

```json
{
  "version": 1,
  "hooks": {
    "stop": [
      {
        "command": "powershell -NoProfile -ExecutionPolicy Bypass -File ./hooks/conversation-review-followup.ps1"
      }
    ]
  }
}
```

Bash 版本脚本名改为 `conversation-review-followup.sh`，followup_message 同上。
