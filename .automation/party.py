#!/usr/bin/python3
# SPDX-License-Identifier: Apache-2.0

import itertools
import json
import re
import sys
from github import Github

# Returns a pull request extracted from Github's event JSON.
def get_pr(event):
    # --- Extract PR from event JSON ---
    # `push` does not include any direct reference to the PR that merged it in
    # its event JSON. We have to extrapolate it using the head commit ID that
    # *is* there.

    # Get head ID from event JSON
    pr_head_id = event["head_commit"]["id"]

    # Grab the commit from the ID
    commit = repo.get_commit(pr_head_id)

    # Get the commit's associated pull (there should only be one) and return.
    return commit.get_pulls()[0]

# Get inputs from shell
(token, repository, path) = sys.argv[1:4]

# Initialize repo
repo = Github(token).get_repo(repository)

# Open Github event JSON
with open(path) as f:
    event = json.load(f)

print("")
print("")

# Get the PR we're working on.
pr = get_pr(event)


print(pr.number)
