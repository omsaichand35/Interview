# InterviewOS - Test Suite Runner
$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Running InterviewOS Test Suite" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

pytest tests/ -v
