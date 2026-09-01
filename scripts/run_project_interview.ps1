# InterviewOS - Project Deep Dive Runner
$ErrorActionPreference = "Stop"

$JobDesc = "data/input/job_descriptions/sample_jd.pdf"
$CandidateName = "Omsai Ramachandran"
$CandidateEmail = "omsai@example.com"
$GitHubUrl = "https://github.com/omsaichand35/MCP"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Launching Project Deep Dive Interview" -ForegroundColor Green
Write-Host " Candidate : $CandidateName" -ForegroundColor Yellow
Write-Host " Repo      : $GitHubUrl" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

python -m interviewos.cli interview --type project --job $JobDesc --name $CandidateName --email $CandidateEmail --github $GitHubUrl
