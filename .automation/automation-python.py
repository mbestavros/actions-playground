import json
import re
import sys
from github import Github

# Get inputs from shell
token = sys.argv[1]
repository = sys.argv[2]
event_path = sys.argv[3]

# Extract PR number from event JSON
# Technique shown here: https://github.com/actions/checkout/issues/58
with open(event_path) as f:
    event = json.load(f)




pr_number = 19#event["number"]

# Authenticate with Github using our token
g = Github(token)

# Initialize repo and grab the pull request we're working on
repo = g.get_repo(repository)

pull_requests = repo.get_pulls()

for potential_pr in pull_requests:
    print("potential_pr number:")
    print(potential_pr.number)
    print("head sha:")
    print(potential_pr.head.sha)
    print("head ref:")
    print(potential_pr.head.sha)




pr = repo.get_pull(pr_number)

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
