#!/usr/bin/env bash
set -e

echo "========================================"
echo " Running InterviewOS Test Suite"
echo "========================================"

pytest tests/ -v
