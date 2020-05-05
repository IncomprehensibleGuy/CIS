#!/usr/bin/env bash
REPO=$1   # repo path
COMMIT=$2 # commit id

source run_or_fail.sh

run_or_fail "Repository folder not found" pushd "$REPO" 1> /dev/null
run_or_fail "Could not clean repository" git clean -d -f -x
run_or_fail "Could not call git pull" git pull
run_or_fail "Could not update to given commit hash" git reset --hard "$COMMIT"