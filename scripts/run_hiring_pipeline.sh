#!/usr/bin/env bash
set -e

JOB_DESC="data/input/job_descriptions/sample_jd.pdf"
RESUME="data/input/resumes/sample_resume.pdf"
CANDIDATE_NAME="Omsai Ramachandran"
CANDIDATE_EMAIL="omsai@example.com"

echo "========================================"
echo " Launching Full Hiring Pipeline"
echo " Candidate : $CANDIDATE_NAME ($CANDIDATE_EMAIL)"
echo " Job Desc  : $JOB_DESC"
echo " Resume    : $RESUME"
echo "========================================"

python3 -m interviewos.cli hiring --job "$JOB_DESC" --resume "$RESUME" --name "$CANDIDATE_NAME" --email "$CANDIDATE_EMAIL"
