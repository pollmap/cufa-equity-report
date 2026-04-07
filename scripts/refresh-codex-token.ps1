# Luxon AI — Codex OAuth Token Auto-Refresh
# Runs daily via Windows Task Scheduler
# Refreshes ChatGPT Pro OAuth tokens in ~/.codex/auth.json

$ErrorActionPreference = "SilentlyContinue"
$logFile = "$env:USERPROFILE\.claude\scripts\token-refresh.log"
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

# Check if auth.json exists
$authFile = "$env:USERPROFILE\.codex\auth.json"
if (-not (Test-Path $authFile)) {
    "$timestamp | ERROR: auth.json not found" | Out-File -Append $logFile
    exit 1
}

# Read current token and check expiry
$auth = Get-Content $authFile | ConvertFrom-Json
$lastRefresh = $auth.last_refresh

# Use codex CLI to refresh
$result = & codex auth refresh 2>&1
if ($LASTEXITCODE -eq 0) {
    "$timestamp | SUCCESS: Token refreshed (was: $lastRefresh)" | Out-File -Append $logFile
} else {
    # Fallback: try login if refresh fails
    "$timestamp | WARN: Refresh failed, token may still be valid. Error: $result" | Out-File -Append $logFile
}
