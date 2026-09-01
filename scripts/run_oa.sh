#!/usr/bin/env bash
set -e

JOB_DESC="data/input/job_descriptions/sample_jd.pdf"
CANDIDATE_NAME="Omsai Ramachandran"
CANDIDATE_EMAIL="omsai@example.com"
QUESTIONS=5
DURATION=20

echo "========================================"
echo " Launching Online Assessment (OA)"
echo " Candidate : $CANDIDATE_NAME"
echo " Questions : $QUESTIONS"
echo " Duration  : $DURATION mins"
echo "========================================"

python3 -m interviewos.cli oa --job "$JOB_DESC" --name "$CANDIDATE_NAME" --email "$CANDIDATE_EMAIL" --questions "$QUESTIONS" --duration "$DURATION"
