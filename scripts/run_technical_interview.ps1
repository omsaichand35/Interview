# InterviewOS - Technical Round Runner
$ErrorActionPreference = "Stop"

$JobDesc = "data/input/job_descriptions/sample_jd.pdf"
$CandidateName = "Omsai Ramachandran"
$CandidateEmail = "omsai@example.com"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Launching Technical Interview Round" -ForegroundColor Green
Write-Host " Candidate : $CandidateName" -ForegroundColor Yellow
Write-Host " Job Desc  : $JobDesc" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

python -m interviewos.cli interview --type technical --job $JobDesc --name $CandidateName --email $CandidateEmail
