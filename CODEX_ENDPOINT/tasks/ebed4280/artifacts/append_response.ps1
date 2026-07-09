$ErrorActionPreference='Stop'
$path = 'C:\Users\oscar\AI WORKBENCH\Mekatelyu\CODEX_ENDPOINT\sessions\ebed4280.json'
$dir = Split-Path -Parent $path
$session = Get-Content -Raw -LiteralPath $path | ConvertFrom-Json
if ($session.state -ne 'running_codex' -or $session.last_bridge_run_id -ne 'c077d074' -or $session.conversation[-1].from -ne 'opencode') { throw 'Session gate failed' }
$message = Get-Content -Raw -LiteralPath 'C:\Users\oscar\AI WORKBENCH\Mekatelyu\CODEX_ENDPOINT\tasks\ebed4280\artifacts\reconciled_response.md'
$entry = [ordered]@{
  id = ([guid]::NewGuid().ToString('N').Substring(0,8))
  turn = 1
  from = 'codex'
  type = 'response'
  message = $message
  artifacts = @()
  timestamp = (Get-Date).ToUniversalTime().ToString('o')
  bridge_run_id = 'c077d074'
  metadata = @{}
}
$session.conversation += [pscustomobject]$entry
$session.updated_at = (Get-Date).ToUniversalTime().ToString('o')
$session.turn = 1
$session.revision = 3
$session.state = 'awaiting_opencode'
$session.current_holder = 'opencode'
$session.needs_input = $true
$tmp = Join-Path $dir ('.ebed4280.' + [guid]::NewGuid().ToString('N') + '.tmp')
$json = $session | ConvertTo-Json -Depth 100
Set-Content -LiteralPath $tmp -Value $json -Encoding UTF8
$null = Get-Content -Raw -LiteralPath $tmp | ConvertFrom-Json
Move-Item -LiteralPath $tmp -Destination $path -Force
$null = Get-Content -Raw -LiteralPath $path | ConvertFrom-Json
Get-ChildItem -LiteralPath $dir -Filter '.ebed4280.*.tmp' | Remove-Item -Force
