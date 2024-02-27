#!/usr/bin/env bash
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

# This script helps to abandon open patches when a given branch transitions
# to Unmaintained or End of Life and all patches on stable/<series> branch
# needs to be abandoned in order to be able to delete that branch.

set -e

if [[ $# -lt 2 ]]; then
    echo "Usage: $(basename $0) <branch> <repo> [<repo>...]"
    echo "repo should be e.g. glance"
    echo
    echo "Example: $(basename $0) yoga \$(list-deliverables --series yoga --is-eom)"
    echo "     or: $(basename $0) ussuri \$(list-deliverables --series ussuri --is-eol)"
    echo "     or: $(basename $0) 2023.1 \$(list-deliverables --series antelope)"
    echo
    echo " !!! WARNING: please do not run this script without discussing it"
    echo "              first with release managers!"
    exit 1
fi

series="$1"
shift
repos="$@"

function abandon_change {
    gitid=$1
    msg=$2
    commit_message=$(ssh review.opendev.org "gerrit query $gitid --current-patch-set --format json" | head -n1 | jq .subject)
    echo "Abandoning: $change -- $commit_message"
    ssh review.opendev.org gerrit review $gitid --abandon --message \"$msg\"
}



if [[ -z "$TARGET" ]]; then
    echo
    read -p "> Is stable/$series transitioning to Unmaintained or End of Life? [u/e]: " TARGET
fi

if [ "${TARGET,,}" != "u" ] && [ "${TARGET,,}" != "e" ]; then
    echo "Please choose either u or e."
    exit 1
fi

for repo in $repos; do
    echo "Processing repository: $repo..."
    open_changes=$(
        ssh review.opendev.org "gerrit query --current-patch-set --format json \
        status:open branch:stable/${series} project:openstack/${repo}" | \
        jq .currentPatchSet.revision | grep -v null | sed 's/"//g'
    )

    if [ "${TARGET,,}" == "u" ]; then
        abandon_message="stable/$series branch of openstack/$repo is about to be deleted.
To be able to do that, all open patches need to be abandoned.
Please cherry pick the patch to unmaintained/$series if you want to
further work on this patch."
    else
        abandon_message="
stable/$series branch of openstack/$repo transitioned to End of Life
and is about to be deleted.
To be able to do that, all open patches need to be abandoned."
    fi

    for change in $open_changes; do
        abandon_change $change "$abandon_message"
    done
done

