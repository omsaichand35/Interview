#!/usr/bin/env bash
set -e

RESUME="data/input/resumes/sample_resume.pdf"
JOB_DESC="data/input/job_descriptions/sample_jd.pdf"

echo "========================================"
echo " Launching AI Learning Mentor"
echo " Resume    : $RESUME"
echo " Job Desc  : $JOB_DESC"
echo "========================================"

python3 -m interviewos.cli mentor --resume "$RESUME" --job "$JOB_DESC"
