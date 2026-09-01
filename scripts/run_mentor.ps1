# InterviewOS - AI Learning Mentor Runner
$ErrorActionPreference = "Stop"

$Resume = "data/input/resumes/sample_resume.pdf"
$JobDesc = "data/input/job_descriptions/sample_jd.pdf"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Launching AI Learning Mentor" -ForegroundColor Green
Write-Host " Resume    : $Resume" -ForegroundColor Yellow
Write-Host " Job Desc  : $JobDesc" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

python -m interviewos.cli mentor --resume $Resume --job $JobDesc
