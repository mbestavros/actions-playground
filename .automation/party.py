#!/usr/bin/python3
# SPDX-License-Identifier: Apache-2.0

import itertools
import json
import random
import re
import sys
from github import Github

# We don't want to copy all labels on linked issues; only those in this subset.
ONESHOT_LINKS = {
    "https://giant.gfycat.com/SpeedyAmazingIndianpalmsquirrel.webm",
    "https://cdn.quotesgram.com/img/3/48/841275503-tumblr_mfx1r9sZNM1qa601io6_250.gif",
    "https://i.imgur.com/Cn9zAnI.gif",
    "https://66.media.tumblr.com/d9a3ce2eb39c98d1f81dfc8b5ad266f8/tumblr_mv4uuywedA1rw4rkuo4_r2_400.gif",
    "https://www.picgifs.com/reaction-gifs/reaction-gifs/it-crowd/picgifs-it-crowd-82110.gif",
}

LATE_NIGHT = "https://thumbs.gfycat.com/FlawlessSimplisticGoldenmantledgroundsquirrel-size_restricted.gif"

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

# Get the PR we're working on.
pr = get_pr(event)

# Oneshot
if(pr.review_comments == 0):
    gif = random.sample(ONESHOT_LINKS, 1)
    pr.create_issue_comment("Congratulations on a lightning-fast merge!<br/>![Well done!](" + gif + ")")
