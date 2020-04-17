#!/usr/bin/python3
# SPDX-License-Identifier: Apache-2.0

import itertools
import json
import re
import sys
from github import Github

# Returns a pull request extracted from Github's event JSON.
def get_pr(event):
    # --- Extract PR from event JSON ---
    # `check_run`/`check_suite` does not include any direct reference to the PR
    # that triggered it in its event JSON. We have to extrapolate it using the head
    # SHA that *is* there.

    # Get head SHA from event JSON
    pr_head_sha = event["head_commit"]["id"]
    print("pr head sha")
    print(pr_head_sha)

    # Find the repo PR that matches the head SHA we found
    return {pr.head.sha: pr for pr in repo.get_pulls(state="closed")}#[pr_head_sha]

# Get inputs from shell
(token, repository, path) = sys.argv[1:4]

# Initialize repo
repo = Github(token).get_repo(repository)

# Open Github event JSON
with open(path) as f:
    event = json.load(f)

# Get the PR we're working on.
pr = get_pr(event)

print("")
print("")
print(pr)
