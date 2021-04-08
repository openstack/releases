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
# Semi-automates the process of creating release team initiated release
# requests.

if [[ $# -lt 2 ]]; then
    echo "Usage: $(basename $0) <series> <repo> [<repo>...]"
    echo "repo should be e.g. glance"
    echo
    echo "Example: $(basename $0) ussuri \$(list-deliverables --unreleased --series ussuri)"
    echo "Example: $(basename $0) train \$(list-deliverables \\"
    echo "         --series train --cycle-based-no-trialing | grep -v tempest)"
    echo "Example: $(basename $0) train \$(list-deliverables --series stein --cyle-based)"
    exit 1
fi

series="$1"
shift
repos="$@"

TOOLSDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASEDIR=$(dirname $TOOLSDIR)
source $TOOLSDIR/functions

# Make sure no pager is configured so the output is not blocked
export PAGER=

if [[ -z "$VIRTUAL_ENV" ]]; then
    if [[ ! -d .tox/venv ]]; then
        tox -e venv --notest
    fi
    source ./.tox/venv/bin/activate
fi

# Set up a clean workspace so we make sure we always have the latest and clean
# files for processing. setup_temp_space defined $MYTMPDIR.
setup_temp_space 'make-auto-releases'
clone_repo "openstack/releases"
cd openstack/releases
git review -s > /dev/null

# Prompt for global parameters to use for all releases
read -p "> Enter review topic to use: " topic
echo
echo "> Enter commit message template"
echo "  The placeholder PROJECT will be replaced with the current project."
echo "  (Press Ctrl-D when done.)"
echo
echo "------------------------------------------------------------------------"
commit=$(</dev/stdin)
echo
# Set the branch name for this series
branch=$(series_to_branch "$series")
read -p "> Branch to use (${branch}): " temp_branch
echo

if [[ ! -z "${temp_branch}" ]]; then
    branch=${temp_branch}
fi

newbranch=""
read -p "> Create stable branch? [y/N]: " YN
if [ "${YN,,}" == "y" ]; then
    newbranch="--stable-branch"
fi
echo
read -p "> Append list of changes to commit message? [y/N]: " YN
if [ "${YN,,}" == "y" ]; then
    append_change_list="yes"
fi

echo
echo "======================================"
echo "Confirm details:"
echo "======================================"
echo "Topic:       $topic"
echo "Series:      $series"
echo "Branch:      $branch"
echo "New Branch:  $newbranch"
echo "Change list: $append_change_list"
echo "Commit Message Template:"
echo
echo "------------------------------------------------------------------------"
echo "${commit//PROJECT/example-project}"
echo "------------------------------------------------------------------------"
echo
echo "======================================"
read -p "Continue with processing? [y/N]: " YN
if [ "${YN,,}" != "y" ]; then
    exit 1
fi

function process_repo {
    repo=$1
    change_list=""
    title "Unreleased changes in $repo ($series)"
    cd "$MYTMPDIR"
    clone_repo "openstack/$repo" $branch
    if [[ $? -ne 0 ]]; then
        return 1
    fi
    cd "openstack/$repo"
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
        if [ -n "$append_change_list" ]; then
            change_list="

$ git log --oneline --no-merges ${prev_tag}..${end_sha}
$(git log --oneline --no-merges ${prev_tag}..${end_sha})
"
        fi
    fi

    read -p "Create new release? [y/N]: " YN
    case $YN in
        [Yy]* ) RELEASE="y";;
        * )
            echo "Skipping $repo release..."
            return
            ;;
    esac

    echo
    echo "Releasing $repo"
    echo "===================="
    cd ../releases
    echo "Select appropriate release type:"
    select type in bugfix feature major milestone rc
    do
        new-release $series $repo $type $newbranch
        break
    done
    git add .
    message="${commit//PROJECT/$repo}${change_list}"
    git commit -s -m "$message"
    git log -1
    git review -t $topic
    git reset --hard HEAD~1 > /dev/null

    cd ../..
    echo
}

# Process each repo passed in to see if a release should be proposed
for repo in $repos; do
    cd $MYTMPDIR
    echo
    process_repo "${repo/openstack\//}"
done
