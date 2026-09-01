#!/usr/bin/env bash
set -e

JOB_DESC="data/input/job_descriptions/sample_jd.pdf"
CANDIDATE_NAME="Omsai Ramachandran"
CANDIDATE_EMAIL="omsai@example.com"
GITHUB_URL="https://github.com/omsaichand35/MCP"

echo "========================================"
echo " Launching Project Deep Dive Interview"
echo " Candidate : $CANDIDATE_NAME"
echo " Repo      : $GITHUB_URL"
echo "========================================"

python3 -m interviewos.cli interview --type project --job "$JOB_DESC" --name "$CANDIDATE_NAME" --email "$CANDIDATE_EMAIL" --github "$GITHUB_URL"
