# InterviewOS - HR & Behavioral Round Runner
$ErrorActionPreference = "Stop"

$JobDesc = "data/input/job_descriptions/sample_jd.pdf"
$CandidateName = "Omsai Ramachandran"
$CandidateEmail = "omsai@example.com"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Launching HR & Behavioral Interview" -ForegroundColor Green
Write-Host " Candidate : $CandidateName" -ForegroundColor Yellow
Write-Host " Job Desc  : $JobDesc" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

python -m interviewos.cli interview --type hr --job $JobDesc --name $CandidateName --email $CandidateEmail
