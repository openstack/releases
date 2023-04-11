#!/bin/bash
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Produce files for every team that has repositories with the content of
# open and unreleased changes.

if [[ $# -lt 1 ]]; then
    echo "Usage: $(basename $0) <branch>"
    echo "branch should be e.g. ocata"
    exit 1
fi

BRANCH=${1}
RESULT_DIR="$BRANCH-$(date '+%Y%m%d-%H%M')"
mkdir -p $RESULT_DIR

OPENSTACK_TEAMS=$(grep team deliverables/${BRANCH}/*.yaml | cut -f3 -d: | \
                sort -u)

TOOLSDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASEDIR=$(dirname $TOOLSDIR)
source $TOOLSDIR/functions

function get_open_patches {
    REPO=$1

    OPEN_CHANGES=$(ssh -p 29418 review.opendev.org gerrit query status:open \
                project:${REPO} branch:stable/${BRANCH} | \
                awk '/url:|subject:/ {$1=""; print $0}' | \
                awk '(NR%2){buf=$0}!(NR%2){print $0 " --" buf}')

    if [ -n "${OPEN_CHANGES}" ]; then
        title "Changes waiting for review in ${REPO} (stable/${BRANCH})"
        echo "${OPEN_CHANGES}"
    fi
}

for team in ${OPENSTACK_TEAMS}; do
    echo "Checking repositories of team: ${team}"

    REPOS=$(tox -e venv -- list-deliverables --repos \
            --series ${BRANCH} --team ${team} | grep "^openstack/")

    if [ -n "${REPOS}" ]; then
        echo "List of open and unreleased changes of team '${team}' " \
             "(stable/${BRANCH})" >${RESULT_DIR}/${team}.txt
        for repo in ${REPOS}; do
            get_open_patches ${repo} >>${RESULT_DIR}/${team}.txt
            tools/list_unreleased_changes.sh stable/${BRANCH} ${repo} >> \
                ${RESULT_DIR}/${team}.txt
        done
    else
        echo " No repositories found for team '${team}'"
    fi
done
