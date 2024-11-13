#!/bin/bash
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

# This script helps to find and delete stable/<series> branches tagged with
# <series>-eom tag, when the given series transitions to Unmaintained.

function help {
# Display helping message
cat <<EOF
usage: $0 <series> [<args>]

Provide a list of repositories that contains eom stale branches on a
series, and give option to delete them.

Arguments:
    <series>            The <series> that is to move to Unmaintained (e.g. antelope)
    -d, --debug         Turn on the debug mode
    -h, --help          show this help message and exit
examples:
    $(basename $0)
EOF
}

for i in "$@"; do
    case $i in
        # Turn on the debug mode
        -d|--debug)
        set -x
        shift 1
        ;;
        # Display the helping message
        -h|--help)
        help
        exit 0
        ;;
    esac
done

if [[ "$1" == "" ]]; then
    help
    exit 1
fi
SERIES=$1


gerrit_username=${GERRIT_USER:-}
GERRIT_URL="https://review.opendev.org"
TOOLSDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASEDIR=$(dirname $TOOLSDIR)
source $TOOLSDIR/functions
enable_tox_venv

# Make sure no pager is configured so the output is not blocked
export PAGER=

setup_temp_space 'list-eom-stale-branches'

# Get branch name from series name (stable/2023.1 for antelope)
branch=$(series_to_branch "$SERIES")
# Get branch id from full branch name (stable/2023.1 -> 2023.1)
branch_id=${branch#*/}

function no_open_patches {
    req="${GERRIT_URL}/changes/?q=status:open+project:${repo}+branch:${branch}"
    patches=$(curl -s ${req} | sed 1d | jq --raw-output '.[] | .change_id')
    [ -z "${patches}" ]
    no_opens=$?
    if [[ "$no_opens" -eq 1 ]]; then
        echo "Patches remained open on stale branch (make sure to abandon them):"
        echo "https://review.opendev.org/q/status:open+project:${repo}+branch:${branch}"
    fi
    return $no_opens
}

function eom_tag_matches_head {
    head=$(git log --oneline --decorate -1)
    [[ "$head" =~ "${branch_id}-eom" ]] && [[ "$head" =~ "origin/${branch}" ]]
    matches=$?
    if [[ "$matches" -eq 1 ]] ; then
        tags=$(git tag)
        [[ "$tags" =~ "${branch_id}-eom" ]]
        eom_tag_exists=$?
        if [[ "$eom_tag_exists" -eq 0 ]]; then
            echo "WARNING !!! ${branch} has patches on top of the ${branch_id}-eom tag."
            echo "Please check the branch and ${branch_id}-eom tag manually."
            echo "Do not delete the branch if you are not sure!"
            read -p "> If you are sure the branch can be deleted, then press D + Enter: " DELETE
            if [ "${DELETE,,}" == "d" ]; then
                matches=0
            else
                echo "Skipping."
            fi
        else
            echo "No ${branch_id}-eom tag found! Branch cannot be deleted. Skipping."
        fi
    fi
    return $matches
}

function is_eom {
    ${TOOLSDIR}/delete_stable_branch.py check --quiet ${repo} ${branch}
    if [[ $? -eq 0 ]]; then
        echo
        echo "${repo} contains eom stale branch (${branch})"
        clone_repo ${repo} ${branch}
        cd ${repo}
        if no_open_patches && eom_tag_matches_head; then
            read -p "> Do you want to delete the branch ${branch} from ${repo} repository? [y/N]: " YN
            if [ "${YN,,}" == "y" ]; then
                if [ -z "$gerrit_username" ]; then
                    read -p "Gerrit username: " gerrit_username
                fi
                ${TOOLSDIR}/delete_stable_branch.py delete ${gerrit_username} ${repo} ${branch}
            fi
        fi
        cd ..
    fi
}

repos=$(list-deliverables -r --series "${SERIES}" --is-eom)

# Show the eom stale branches for each repository.
for repo in ${repos}; do
    cd ${MYTMPDIR}
    echo
    echo " --- $repo (${branch}) --- "
    is_eom "${repo}" "${branch}"
done

