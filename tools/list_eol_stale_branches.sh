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

eom_series=($(list-eom-series))

# Make sure no pager is configured so the output is not blocked
export PAGER=

setup_temp_space 'list-eol-stale-branches'

function no_stable_open_patches {
    req="${GERRIT_URL}/changes/?q=status:open+project:${repo}+branch:stable/${eom_branch}"
    patches=$(curl -s ${req} | sed 1d | jq --raw-output '.[] | .change_id')
    [ -z "${patches}" ]
    no_opens=$?
    if [[ "$no_opens" -eq 1 ]]; then
        echo "Patches remained open on stale branch (make sure to abandon them):"
        echo "https://review.opendev.org/q/status:open+project:${repo}+branch:stable/${eom_branch}"
    fi
    return $no_opens
}

function no_unmaintained_open_patches {
    req="${GERRIT_URL}/changes/?q=status:open+project:${repo}+branch:unmaintained/${eom_branch}"
    patches=$(curl -s ${req} | sed 1d | jq --raw-output '.[] | .change_id')
    [ -z "${patches}" ]
    no_opens=$?
    if [[ "$no_opens" -eq 1 ]]; then
        echo "Patches remained open on stale branch (make sure to abandon them):"
        echo "https://review.opendev.org/q/status:open+project:${repo}+branch:unmaintained/${eom_branch}"
    fi
    return $no_opens
}

function eol_tag_matches_stable_head {
    head=$(git log --oneline --decorate -1)
    [[ "$head" =~ "${eom_branch}-eol" ]] && [[ "$head" =~ "origin/stable/${eom_branch}" ]]
    matches=$?
    if [[ "$matches" -eq 1 ]] ; then
        tags=$(git tag)
        [[ "$tags" =~ "${eom_branch}-eol" ]]
        eol_tag_exists=$?
        if [[ "$eol_tag_exists" -eq 0 ]]; then
            echo "WARNING !!! stable/${eom_branch} has patches on top of the ${eom_branch}-eol tag."
            echo "Please check the branch and ${eom_branch}-eol tag manually."
            echo "Do not delete the branch if you are not sure!"
            read -p "> If you are sure the branch can be deleted, then press D + Enter: " DELETE
            if [ "${DELETE,,}" == "d" ]; then
                matches=0
            else
                echo "Skipping."
            fi
        else
            echo "No ${eom_branch}-eol tag found! Branch cannot be deleted. Skipping."
        fi
    fi
    return $matches
}

function eol_tag_matches_unmaintained_head {
    head=$(git log --oneline --decorate -1)
    [[ "$head" =~ "${eom_branch}-eol" ]] && [[ "$head" =~ "origin/unmaintained/${eom_branch}" ]]
    matches=$?
    if [[ "$matches" -eq 1 ]] ; then
        tags=$(git tag)
        [[ "$tags" =~ "${eom_branch}-eol" ]]
        eol_tag_exists=$?
        if [[ "$eol_tag_exists" -eq 0 ]]; then
            echo "WARNING !!! unmaintained/${eom_branch} has patches on top of the ${eom_branch}-eol tag."
            echo "Please check the branch and ${eom_branch}-eol tag manually."
            echo "Do not delete the branch if you are not sure!"
            read -p "> If you are sure the branch can be deleted, then press D + Enter: " DELETE
            if [ "${DELETE,,}" == "d" ]; then
                matches=0
            else
                echo "Skipping."
            fi
        else
            echo "No ${eom_branch}-eol tag found! Branch cannot be deleted. Skipping."
        fi
    fi
    return $matches
}

function is_stable_eol {
    ${TOOLSDIR}/delete_stable_branch.py check --quiet ${repo} ${eom_branch}
    if [[ $? -eq 0 ]]; then
        echo
        echo "${repo} contains eol stale branch (${eom_branch})"
        clone_repo ${repo} stable/${eom_branch}
        cd ${repo}
        if no_stable_open_patches && eol_tag_matches_stable_head; then
            read -p "> Do you want to delete the branch stable/${eom_branch} from ${repo} repository? [y/N]: " YN
            if [ "${YN,,}" == "y" ]; then
                if [ -z "$gerrit_username" ]; then
                    read -p "Gerrit username: " gerrit_username
                fi
                ${TOOLSDIR}/delete_stable_branch.py delete ${gerrit_username} ${repo} ${eom_branch}
            fi
        fi
        cd ..
    fi
}

function is_unmaintained_eol {
    ${TOOLSDIR}/delete_unmaintained_branch.py check --quiet ${repo} ${eom_branch}
    if [[ $? -eq 0 ]]; then
        echo
        echo "${repo} contains eol stale branch (${eom_branch})"
        clone_repo ${repo} unmaintained/${eom_branch}
        cd ${repo}
        if no_unmaintained_open_patches && eol_tag_matches_unmaintained_head; then
            read -p "> Do you want to delete the branch unmaintained/${eom_branch} from ${repo} repository? [y/N]: " YN
            if [ "${YN,,}" == "y" ]; then
                if [ -z "$gerrit_username" ]; then
                    read -p "Gerrit username: " gerrit_username
                fi
                ${TOOLSDIR}/delete_unmaintained_branch.py delete ${gerrit_username} ${repo} ${eom_branch}
            fi
        fi
        cd ..
    fi
}

for eom_series in "${eom_series[@]}"; do
    eom_branch=$(python -c "from openstack_releases import gitutils; print(gitutils.get_stable_branch_id(\"$eom_series\"))")
    repos=$(list-deliverables -r --series "$eom_series" --is-eol)

    # Show the eol stale branches for each repository.
    for repo in ${repos}; do
        cd ${MYTMPDIR}
        echo
        echo " --- $repo ($eom_branch) --- "
        is_stable_eol "${repo}" "${eom_branch}"
        is_unmaintained_eol "${repo}" "${eom_branch}"
    done
done
