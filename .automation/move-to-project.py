#!/usr/bin/python3

import itertools
import json
import re
import sys
from github import Github

# We don't want to copy all labels on linked issues; only those in this subset.
COPYABLE_LABELS = {
    "enhancement",
    "good first issue",
}

# Get inputs from shell
(token, repository, path) = sys.argv[1:4]

# Authenticate with Github using our token
g = Github(token)

# Initialize repo
repo = g.get_repo(repository)

# Open Github event JSON
with open(path) as f:
    event = json.load(f)

# Determine whether the labels were added or removed
action = event["action"]

print(action)
