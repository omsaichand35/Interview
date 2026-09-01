# InterviewOS - Project Analyzer Agent Runner
$ErrorActionPreference = "Stop"

$GitHubUrl = "https://github.com/omsaichand35/MCP"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Launching GitHub Project Analyzer Agent" -ForegroundColor Green
Write-Host " Repo      : $GitHubUrl" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

python -m interviewos.cli project-analyze --github $GitHubUrl
