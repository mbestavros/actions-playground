#!/usr/bin/python3

import itertools
import json
import sys
import github

# We don't want to copy all labels on linked issues; only those in this subset.
LABEL_PROJECTS = {
    "good first issue": "Example project",
    "question": "Another example project"
}

# Get inputs from shell
(token, repository, path) = sys.argv[1:4]

# Authenticate with Github using our token
g = github.Github(token)

# Initialize repo
repo = g.get_repo(repository)

# Open Github event JSON
with open(path) as f:
    event = json.load(f)

# Determine whether the labels were added or removed
action = event["action"]

# Get the name of the label
label_name = event["label"]["name"]

# Determine content type: issue or PR, as well as content ID
if "issue" in event:
    content_type = "Issue"
    content_id = event["issue"]["id"]
else:
    content_type = "PullRequest"
    content_id = event["pull_request"]["id"]

# Fetch the project we want to add to or remove from
project = [p for p in repo.get_projects() if p.name == LABEL_PROJECTS[label_name]][0]

# If the label was added, we want to add to the project. If removed, we want to
# remove from the project.
if(action == "labeled"):
    project_column = project.get_columns()[0]
    try:
        project_column.create_card(content_id=content_id, content_type=content_type)
    except github.GithubException as e:
        print(e)
        print("")
        print(e.data["errors"]["message"])
        if e.data["errors"]["message"] == "Project already has the associated issue":
            print("Card already in project.")
            sys.exit(0)
    
elif(action == "unlabeled"):
    for column in project.get_columns():
        for card in column.get_cards():
            if(card.get_content() is not None and card.get_content().id == content_id):
                card.delete()
