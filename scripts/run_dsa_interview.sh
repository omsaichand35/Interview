#!/usr/bin/env bash
set -e

JOB_DESC="data/input/job_descriptions/sample_jd.pdf"
CANDIDATE_NAME="Omsai Ramachandran"
CANDIDATE_EMAIL="omsai@example.com"

echo "========================================"
echo " Launching DSA Algorithmic Interview"
echo " Candidate : $CANDIDATE_NAME"
echo " Job Desc  : $JOB_DESC"
echo "========================================"

python3 -m interviewos.cli interview --type dsa --job "$JOB_DESC" --name "$CANDIDATE_NAME" --email "$CANDIDATE_EMAIL"
