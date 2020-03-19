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

pr_number = 11#event["number"]

# Authenticate with Github using our token
g = Github(token)

# Initialize repo and grab the pull request we're working on
repo = g.get_repo(repository)
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

# Get projects for both PR and associated issue
repo_projects = repo.get_projects()
issue_projects = []
pr_projects = []
for project in repo_projects:
    for column in project.get_columns():
        for card in column.get_cards():
            card_content = card.get_content()
            if card_content is not None:
                if(card_content.number == issue_number):
                    issue_projects += [project]
                if(card_content.number == pr_number):
                    pr_projects += [project]

# Assign labels and projects to the pull request, if it doesn't have them already
for project in issue_projects:
    if project not in pr_projects:
        column_to_add = project.get_columns()[0]
        column_to_add.create_card(content_id=pr.id, content_type="PullRequest")

unset_issue_labels = []
for label in issue_labels:
    if label not in pr_labels:
        unset_issue_labels += [label]
    
pr.set_labels(*unset_issue_labels)
