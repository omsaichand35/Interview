# InterviewOS - Online Assessment (OA) Runner
$ErrorActionPreference = "Stop"

$JobDesc = "data/input/job_descriptions/sample_jd.pdf"
$CandidateName = "Omsai Ramachandran"
$CandidateEmail = "omsai@example.com"
$Questions = 5
$Duration = 20

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Launching Online Assessment (OA)" -ForegroundColor Green
Write-Host " Candidate : $CandidateName" -ForegroundColor Yellow
Write-Host " Questions : $Questions" -ForegroundColor Yellow
Write-Host " Duration  : $Duration mins" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

python -m interviewos.cli oa --job $JobDesc --name $CandidateName --email $CandidateEmail --questions $Questions --duration $Duration
