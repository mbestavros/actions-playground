#!/usr/bin/python3
# SPDX-License-Identifier: Apache-2.0

import json
import re
import sys
from github import Github

# Regex to pick out closing keywords.
LINKED_ISSUES = re.compile("(close[sd]?|fix|fixe[sd]?|resolve[sd]?)\s*:?\s+#(\d+)", re.I)

# Returns a pull request extracted from Github's event JSON.
def get_pr(event):
    # --- Extract issue from event JSON ---
    # `pull_request` directly refers the the PR number in the event JSON.
    # Extract that number and use it to grab the PR.

    # Get PR number
    pr_number = event["number"]

    # Grab the PR from the number and return
    return repo.get_pull(pr_number)

# Extract all associated issues from PR commit messages
def get_linked_issues_commits(pr):
    for c in pr.get_commits():
        for verb, num in LINKED_ISSUES.findall(c.commit.message):
            yield int(num)

# Extract all associated issues linked in PR description
def get_linked_issues_body(pr):
    # Extract all associated issues from closing keyword in PR
    for verb, num in LINKED_ISSUES.findall(pr.body):
        yield int(num)

# Get inputs from shell
(token, repository, path) = sys.argv[1:4]

# Initialize repo
repo = Github(token).get_repo(repository)

# Open Github event JSON
with open(path) as f:
    event = json.load(f)

# Get the PR we're working on.
pr = get_pr(event)

commits_issues = set(get_linked_issues_commits(pr))
description_issues = set(get_linked_issues_body(pr))
print(commits_issues)
print(description_issues)

unlinked_issues = description_issues - commits_issues
print(unlinked_issues)

if len(unlinked_issues) > 0:
    print("Your PR contains one or more commit messages that refer to closing\
        issues, but those issues are not linked in your pull request\
            description.")
    print("Please include the following in your PR description:\n")
    for n in unlinked_issues:
        print("Resolves #" + n)
    print("\nYou may use any of Github's supported closing keywords in place of 'Resolves':")
    print("\nhttps://help.github.com/en/github/managing-your-work-on-github/linking-a-pull-request-to-an-issue#linking-a-pull-request-to-an-issue-using-a-keyword")
    exit(1)
