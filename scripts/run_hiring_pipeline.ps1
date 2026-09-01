# InterviewOS - Full Hiring Pipeline Runner
$ErrorActionPreference = "Stop"

$JobDesc = "data/input/job_descriptions/sample_jd.pdf"
$Resume = "data/input/resumes/sample_resume.pdf"
$CandidateName = "Omsai Ramachandran"
$CandidateEmail = "omsai@example.com"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Launching Full Hiring Pipeline" -ForegroundColor Green
Write-Host " Candidate : $CandidateName ($CandidateEmail)" -ForegroundColor Yellow
Write-Host " Job Desc  : $JobDesc" -ForegroundColor Yellow
Write-Host " Resume    : $Resume" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

python -m interviewos.cli hiring --job $JobDesc --resume $Resume --name $CandidateName --email $CandidateEmail
