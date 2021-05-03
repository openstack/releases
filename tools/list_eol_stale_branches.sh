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

# Extended Maintenance was introduced during Queens
# All the following cycle under EM should be added there.

function help {
# Display helping message
cat <<EOF
usage: $0 [<args>]

Provide a list of repositories that contains eol stale branches, and
give option to delete them.

Arguments:
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


gerrit_username=${GERRIT_USER:-}
GERRIT_URL="https://review.opendev.org"
TOOLSDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASEDIR=$(dirname $TOOLSDIR)
source $TOOLSDIR/functions
enable_tox_venv

em_series=($(list-em-series))

# Make sure no pager is configured so the output is not blocked
export PAGER=

setup_temp_space 'list-eol-stale-branches'

branch=$(series_to_branch "$series")

function no_open_patches {
    req="${GERRIT_URL}/changes/?q=status:open+project:${repo}+branch:stable/${em_serie}"
    patches=$(curl -s ${req} | sed 1d | jq --raw-output '.[] | .change_id')
    [ -z "${patches}" ]
    no_opens=$?
    if [[ "$no_opens" -eq 1 ]]; then
        echo "Patches remained open on stale branch (make sure to abandon them):"
        echo "https://review.opendev.org/q/status:open+project:${repo}+branch:stable/${em_serie}"
    fi
    return $no_opens
}

function eol_tag_matches_head {
    head=$(git log --oneline --decorate -1)
    [[ "$head" =~ "${em_serie}-eol" ]] && [[ "$head" =~ "origin/stable/${em_serie}" ]]
    matches=$?
    if [[ "$matches" -eq 1 ]] ; then
        echo "stable/${em_serie} has patches on top of the ${em_serie}-eol tag"
    fi
    return $matches
}

function is_eol {
    clone_repo ${repo} stable/${em_serie}
    cd ${repo} && git checkout -f -q stable/${em_serie} 2>/dev/null
    if [[ $? -eq 0 ]]; then
        echo "${repo} contains eol stale branch (${em_serie})"
        if no_open_patches && eol_tag_matches_head; then
            read -p "> Do you want to delete the branch stable/${em_serie} from ${repo} repository? [y/N]: " YN
            if [ "${YN,,}" == "y" ]; then
                if [ -z "$gerrit_username" ]; then
                    read -p "Gerrit username: " gerrit_username
                fi
                ${TOOLSDIR}/delete_stable_branch.py ${gerrit_username} ${repo} ${em_serie}
            fi
        fi
        cd ..
    fi
}

for em_serie in "${em_series[@]}"; do
    repos=$(list-deliverables -r --series "${em_serie}" --is-eol)

    # Show the eol stale branches for each repository.
    for repo in ${repos}; do
        cd ${MYTMPDIR}
        echo
        is_eol "${repo}" "${em_serie}"
    done
done
