from github import Github
import re
import json
import sys

# Get inputs from shell
token = sys.argv[1]
repository = sys.argv[2]
event_path = sys.argv[3]

# Extract PR number from event JSON
with open(event_path) as f:
    event = json.load(f)

pr_number = 10#event["number"]

# Authenticate with Github using our token
g = Github(token)

# Initialize repo and grab the pull request we're working on
repo = g.get_repo(repository)
pr = repo.get_pull(pr_number)

# Extract issue number from closing keyword in PR
closing_keyword_regex = re.compile("Resolves #\d+")
closing_keyword = closing_keyword_regex.search(pr.body).group()
issue_number_regex = re.compile("\d+")
issue_number = int(issue_number_regex.search(closing_keyword).group())

# Get associated issue's labels
associated_issue = repo.get_issue(issue_number)
issue_labels = associated_issue.labels

# Get associated issue's projects
repo_projects = repo.get_projects()
issue_projects = []
for project in repo_projects:
    for column in project.get_columns():
        for card in column.get_cards():
            card_content = card.get_content()
            if(card_content is not None and card_content.number == issue_number):
                issue_projects += [project]

# Assign labels and projects to the pull request
for project in issue_projects:
    column_to_add = project.get_columns()[0]
    print(pr.id)
    column_to_add.create_card(content_id=pr.id, content_type="PullRequest")
pr.set_labels(*issue_labels)
