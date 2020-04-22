#!/usr/bin/python3
# SPDX-License-Identifier: Apache-2.0

import itertools
import json
import random
import re
import sys
from github import Github

FIRST_ISSUE = {
    "https://gifimage.net/wp-content/uploads/2017/08/it-crowd-gif-12.gif",
    "https://media1.tenor.com/images/81f6c0d34b867a7ca405125aa0e7f328/tenor.gif?itemid=6233135",
    "https://i.giphy.com/media/FspLvJQlQACXu/giphy.webp",
}

# Returns a pull request extracted from Github's event JSON.
def get_issue(event):
    # --- Extract issue from event JSON ---
    # `issues` directly refers the the issue number in the event JSON. Extract
    # that number and use it to grab the issue.

    # Get issue number
    issue_number = event["issue"]["number"]

    # Grab the issue from the number and return
    return repo.get_issue(issue_number)

# Get inputs from shell
(token, repository, path) = sys.argv[1:4]

# Initialize repo
repo = Github(token).get_repo(repository)

# Open Github event JSON
with open(path) as f:
    event = json.load(f)

# Get the PR we're working on.
issue = get_issue(event)

# --- Newcomer ---
# Check whether the person opening the issue has opened an issue in the
# repository before. If it's their first, let's give them a warm welcome.
author = issue.user
if(len([i for i in repo.get_issues(state="all") if i.user == author]) == 0):
    gif = random.sample(FIRST_ISSUE, 1)[0]
    issue.create_comment("Congratulations on filing your first issue! Welcome to the project!<br/><br/>![We're happy to have you!](" + gif + ")")
