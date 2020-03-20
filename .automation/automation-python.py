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

# Extract PR number from event JSON
# Technique shown here: https://github.com/actions/checkout/issues/58
with open(event_path) as f:
    event = json.load(f)

# However, since we're using `check_run`/`check_suite`, the PR number isn't there.
# We need to look up which PR in the repo matches the head SHA included there.

# Get head SHA from event JSON
pr_head_sha = event["check_suite"]["head_sha"]
print("PR HEAD SHA EXTRACTED FROM JSON:")
print(pr_head_sha)

# Get all repo pull requests
repo_pull_requests = repo.get_pulls()

# Find the repo PR that matches the head SHA we found
print("POTENTIAL PRS")
for potential_pr in repo_pull_requests:
    print(potential_pr.head.sha)
    if potential_pr.head.sha == pr_head_sha:
        pr = potential_pr

# Extract associated issue from closing keyword in PR
closing_keyword_regex = re.compile("Resolves #\d+")
closing_keyword = closing_keyword_regex.search(pr.body).group()
issue_number_regex = re.compile("\d+")
issue_number = int(issue_number_regex.search(closing_keyword).group())
associated_issue = repo.get_issue(issue_number)

# Get labels for both PR and associated issue
issue_labels = associated_issue.labels
pr_labels = pr.labels

unset_issue_labels = []
for label in issue_labels:
    if label not in pr_labels:
        unset_issue_labels += [label]
    
pr.set_labels(*unset_issue_labels)
