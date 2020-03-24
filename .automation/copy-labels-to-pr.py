#!/usr/bin/python3
# SPDX-License-Identifier: Apache-2.0

import itertools
import json
import re
import sys
from github import Github

# We don't want to copy all labels on linked issues; only those in this subset.
COPYABLE_LABELS = {
    "enhancement",
    "good first issue",
}

REGEX = re.compile("(close[sd]?|fix|fixe[sd]?|resolve[sd]?)\s*:?\s+#(\d+)", re.I)

# Get inputs from shell
(token, repository, path) = sys.argv[1:4]

# Authenticate with Github using our token
g = Github(token)

# Initialize repo
repo = g.get_repo(repository)

def get_pr(event):
    # --- Extract PR from event JSON ---
    # `check_run`/`check_suite` does not include any direct reference to the PR
    # that triggered it in its event JSON. We have to extrapolate it using the head
    # SHA that *is* there.

    # Get head SHA from event JSON
    pr_head_sha = event["check_suite"]["head_sha"]

    # Find the repo PR that matches the head SHA we found
    return {pr.head.sha: pr for pr in repo.get_pulls()}[pr_head_sha]

def get_related_issues(pr):
    # Extract all associated issues from closing keyword in PR
    numbers_pr_body = {int(num) for verb, num in REGEX.findall(pr.body)}

    # Extract all associated issues from PR commit messages
    results_commit_messages = [REGEX.findall(c.commit.message) for c in pr.get_commits()]
    numbers_commit_messages = {int(num) for verb, num in itertools.chain(*results_commit_messages)}

    # Get the union of both sets of associated issue numbers
    union = numbers_pr_body | numbers_commit_messages 
    print(union)
    return union

# Open Github event JSON
with open(path) as f:
    event = json.load(f)

#Get the PR we're working on.
pr = get_pr(event)
pr_labels = {label.name for label in pr.labels}

# Get every label on every linked issue.
issues = get_related_issues(pr)
issues_labels = [repo.get_issue(n).labels for n in issues]
issues_labels = {l.name for l in itertools.chain(*issues_labels)}
print(issues_labels)

# Find the set of all labels we want to copy that aren't already set on the PR.
unset_labels = COPYABLE_LABELS & issues_labels - pr_labels
print(unset_labels)

# If there are any labels we need to add, add them.
if len(unset_labels) > 0:
    pr.set_labels(*list(unset_labels))
