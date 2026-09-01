#!/usr/bin/env bash
set -e

GITHUB_URL="https://github.com/omsaichand35/MCP"

echo "========================================"
echo " Launching GitHub Project Analyzer Agent"
echo " Repo      : $GITHUB_URL"
echo "========================================"

python3 -m interviewos.cli project-analyze --github "$GITHUB_URL"
