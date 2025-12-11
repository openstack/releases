#!/bin/bash
#
# Script to add PTL and release liaison(s) as reviewers for any release
# patches under a given topic.
#
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

function usage {
    echo "Usage: $0 $gerrit_topic"
    echo
    echo "# Add reviewers to all open reviews"
    echo "Example: $0"
    echo "# Add reviewers for a specific topic"
    echo "Example: $0 ussuri-c-w-i # Adds reviewers for a specific topic"
}

function get_series_from_path {
    local path=$1
    if [[ $path =~ ^deliverables/([^/]+)/.*yaml$ ]]; then
        series="${BASH_REMATCH[1]}"
    else
        series=""
    fi
}

# Validate topic was provided
if [ $# -gt 1 ]; then
    usage
    exit 2
fi

topic=""
if [ $# -eq 1 ]; then
    topic="+topic:$1"
fi

# We make assumptions that local commands will be available
if [[ -z "$VIRTUAL_ENV" ]]; then
    if [[ ! -d .tox/venv ]]; then
        tox -e venv --notest
    fi
    source ./.tox/venv/bin/activate
fi

UNMAINTAINED=$(list-eom-series)

# Make sure we have a gerrit user for authenticated commands
GERRIT_ID=${GERRIT_USER}
if [[ -z "$GERRIT_ID" ]]; then
    GERRIT_ID=$(git config --list | grep gitreview.username | cut -d '=' -f 2)
fi

if [[ -z "$GERRIT_ID" ]]; then
    echo "Need GERRIT_USER environment variable set or be in a repo with"
    echo "gitreview.username set in your git config."
    exit 2
fi

GERRIT="review.opendev.org"
GERRIT_URL="https://$GERRIT"
GERRIT_PROJECT="openstack/releases"

# Get all open reviews for the given topic
reviews=$(curl -s \
    "$GERRIT_URL/changes/?q=status:open+project:$GERRIT_PROJECT${topic}" | \
    sed 1d | \
    jq --raw-output '.[] | .change_id')

# Loop through each review and find deliverable files
for review in $reviews; do
    last_team=""
    deliverable_files=$(curl -s \
        "$GERRIT_URL/changes/?q=$review&o=CURRENT_REVISION&o=CURRENT_FILES" | \
        sed 1d | \
        jq -r '.[] | .revisions | map(.files) | .[] | keys | .[]' | \
        grep deliverables)

    # Extract the owning teams for each deliverable in this patch
    for file in $deliverable_files; do
        get_series_from_path $file
        if [[ $UNMAINTAINED =~ $series ]]; then
            continue
        fi
        team=$(grep team $file | sed 's/team: //g')
        if [[ "$team" == "$last_team" ]]; then
            continue
        fi
        last_team="$team"
        echo "Adding $team reviewers for $review"
        declare -a emails=$(
            get-contacts --all "$team" | awk -F': ' '/Email/ {print $2}')
        for email in $emails; do
            # Skip over some common dummy entries
            if [[ "$email" == "None" ]] || [[ "$email" =~ "example" ]]; then
                continue
            fi

            echo "  Adding Email: $email"
            ssh -p 29418 "$GERRIT_ID@review.opendev.org" gerrit set-reviewers \
                -a "$email" "$review" || true
        done
    done
done
