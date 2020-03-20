
# SPDX-License-Identifier: Apache-2.0

import json
import re
import sys
from github import Github

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
regex = re.compile("(close[sd]?|fix|fixe[sd]?|resolve[sd]?)\s*:?\s+#(\d+)", re.I)
closing_numbers = [number for keyword, number in regex.findall(pr.body)]
if len(closing_numbers) == 0:
    quit()

# We don't want to copy all labels the issue has; only those in the subset
# found in .automation/copyable-labels.json
with open(path) as f:
    copyable_labels = json.load("./copyable-labels.json")

# Get the superset of every label on every linked issue, filtered by our 
# acceptable labels list.
labels_to_add = []
for number in closing_numbers:
    for label in repo.get_issue(number).labels:
        if label not in labels_to_add and label.name in copyable_labels:
            labels_to_add += [label]

# Figure out all labels not yet set on the PR.
pr_labels = pr.labels
unset_issue_labels = []
for label in labels_to_add:
    if(label.name in copyable_labels and label not in pr_labels):
        unset_issue_labels += [label]

# If there are any labels we need to add, add them.
if len(unset_issue_labels) > 0:
    labels_to_set = pr_labels + unset_issue_labels
    pr.set_labels(*labels_to_set)
