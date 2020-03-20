import json
import re
import sys
from github import Github

# Get inputs from shell
token = sys.argv[1]
repository = sys.argv[2]
event_path = sys.argv[3]

# Authenticate with Github using our token
g = Github(token)

# Initialize repo
repo = g.get_repo(repository)

# --- Extract PR from event JSON ---
# `check_run`/`check_suite` does not include any direct reference to the PR
# that triggered it in its event JSON.
# We have to extrapolate it using the head SHA that *is* there.
with open(event_path) as f:
    event = json.load(f)

# Get head SHA from event JSON
pr_head_sha = event["check_suite"]["head_sha"]

# Get all repo pull requests
repo_pull_requests = repo.get_pulls()

# Find the repo PR that matches the head SHA we found
for potential_pr in repo_pull_requests:
    if potential_pr.head.sha == pr_head_sha:
        pr = potential_pr

# Extract associated issue from closing keyword in PR
closing_keyword_regex = re.compile("Resolves #\d+")
closing_keyword_results = closing_keyword_regex.search(pr.body)
if closing_keyword_results is None:
    quit()
closing_keyword = closing_keyword_results.group()
associated_issue_number_regex = re.compile("\d+")
associated_issue_number = int(associated_issue_number_regex.search(closing_keyword).group())
associated_issue = repo.get_issue(associated_issue_number)

# Get labels for both PR and associated issue
issue_labels = associated_issue.labels
pr_labels = pr.labels

# We don't want to mirror all labels the issue has; only those in this subset.
mirrorable_issues = ["enhancement","good first issue"]

unset_issue_labels = []
for label in issue_labels:
    if(label.name in mirrorable_issues and label not in pr_labels):
        unset_issue_labels += [label]

if len(unset_issue_labels) > 0:
    labels_to_set = pr_labels + unset_issue_labels
    pr.set_labels(*labels_to_set)
