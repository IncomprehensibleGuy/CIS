#!/usr/bin/env bash
REPO=$1   # repo path
source run_or_fail.sh

run_or_fail "Repository folder not found" pushd "$REPO" 1> /dev/null
run_or_fail "Could not clone repo for pusher" git clone "$REPO" repo_clone_pusher
run_or_fail "Could not clone repo for test_runner" git clone "$REPO" repo_clone_test_runner

echo "Repository clones for pusher and test_runner are successfully created"
sleep 3