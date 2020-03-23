#!/usr/bin/python3
# SPDX-License-Identifier: Apache-2.0

import json
import re
import sys
from github import Github

# We don't want to copy all labels on linked issues; only those in this subset.
COPYABLE_LABELS = {
    "enhancement",
    "good first issue",
    }

# Get inputs from shell
(token, repository, path) = sys.argv[1:4]

# Authenticate with Github using our token
g = Github(token)

# Initialize repo
repo = g.get_repo(repository)

# Open Github event JSON
with open(path) as f:
    event = json.load(f)

# --- Extract PR from event JSON ---
# `check_run`/`check_suite` does not include any direct reference to the PR
# that triggered it in its event JSON. We have to extrapolate it using the head
# SHA that *is* there.

# Get head SHA from event JSON
pr_head_sha = event["check_suite"]["head_sha"]

# Get all repo pull requests
repo_pull_requests = repo.get_pulls()

# Find the repo PR that matches the head SHA we found
pr = {pr.head.sha: pr for pr in repo_pull_requests}[pr_head_sha]

# Extract all associated issues from closing keyword in PR
regex_pr_body = re.compile("(close[sd]?|fix|fixe[sd]?|resolve[sd]?)\s*:?\s+#(\d+)", re.I)
closing_numbers_pr_body = {number for keyword, number in regex_pr_body.findall(pr.body)}

regex_commit_messages = re.compile("(close[sd]?|fix|fixe[sd]?|resolve[sd]?|related)\s*:?\s+#(\d+)", re.I)
closing_numbers_commit_messages = {number for commit in pr.get_commits() for keyword, number in regex_commit_messages.findall(commit.commit.message)}

closing_numbers = closing_numbers_pr_body.union(closing_numbers_commit_messages)

if len(closing_numbers) == 0:
    quit()

# Get the superset of every label on every linked issue.
all_associated_issue_labels = {label for label in repo.get_issue(int(number)).labels for number in closing_numbers}

# Filter the superset by our list of acceptable labels to copy.
copyable_associated_issue_labels = all_associated_issue_labels.intersection(COPYABLE_LABELS)

# Convert the list of PR labels into a set.
pr_labels = set(pr.labels)

# Find the set of all labels we want to copy that aren't already set on the PR.
unset_associated_issue_labels = copyable_associated_issue_labels.difference(pr_labels)

# If there are any labels we need to add, add them.
if len(unset_associated_issue_labels) > 0:
    pr.set_labels(*list(unset_associated_issue_labels))
