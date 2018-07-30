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
#
# Provide a list of the unreleased changes in the given repositories

if [[ $# -lt 2 ]]; then
    echo "Usage: $(basename $0) <branch> <repo> [<repo>...]"
    echo "repo should be e.g. openstack/glance"
    exit 1
fi

branch="$1"
shift
repos="$@"

TOOLSDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASEDIR=$(dirname $TOOLSDIR)
source $TOOLSDIR/functions

# Make sure no pager is configured so the output is not blocked
export PAGER=

setup_temp_space 'list-unreleased'

function list_changes {
    title "Unreleased changes in $repo ($branch)"
    clone_repo $repo $branch
    if [[ $? -ne 0 ]]; then
        return 1
    fi
    cd $repo
    prev_tag=$(get_last_tag)
    if [ -z "$prev_tag" ]; then
        echo "$repo has not yet been released"
    else
        echo
        end_sha=$(git log -n 1 --pretty=tformat:%h)
        echo "Changes between $prev_tag and $end_sha"
        echo
        git log --no-color --no-merges --format='%h %ci %s' \
            --graph ${prev_tag}..${end_sha}
        echo
    fi
}

# Show the unreleased changes for each repository.
for repo in $repos; do
    cd $MYTMPDIR
    echo
    list_changes "$repo"
done
