#!/usr/bin/env bash
#
# Tool to take a dirty working tree and create a 'flat' gerrit topic (per team)
# for all the changes
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
    echo "Usage: bulk_review.sh -t topic -s subject -b message_body"
    echo
    echo "    topic: local branch names will be of the form $team-$topic"
    echo "           and gerrit topic will be set to $topic"
    echo "  subject: This will be the subject in the git commit"
    echo "     body: This will be the message body for the git commit"
    echo
    echo "This script operates on a dirty repo (such as one created by"
    echo "running tools/make_missing_releases.sh. It will then create a"
    echo "local branch per-team of the modified deliverable files and then"
    echo "submit that branch for review"
    echo
    echo "PTLs and liaisons will be CC'd on the review"
}

# NOTE: It might be worth switching getopt but I don't know if that is
# available and the same on MacOS
while getopts "t:s:b:" arg ; do
    case "$arg" in
    t)
        topic=$OPTARG
    ;;
    s)
        subject=$OPTARG
    ;;
    b)
        body=$OPTARG
    ;;
    *)
        usage
        exit 1
    ;;
    esac
done

if [ -z "$topic" -o -z "$subject" -o -z "$body" ] ; then
    usage
    exit 1
fi

echo 'This script will modifiy git branches and and submit reviews.'
echo 'It relies on master being a safe/clean branch.'
echo
echo 'If master contains private changes, abort now'
echo 'If you have any unrelated work, abort now'
echo 'If you have not saved the modified deliverables somewhere, abort now'
echo
echo 'Press return to continue or <ctrl>-C to abort'

read _continue

declare -A files_by_team_release=()

# Find the team associated with each modified deliverable file
declare -a deliverables=($(git ls-files -m deliverables))
for file in "${deliverables[@]}" ; do
    team="$(get-deliverable-owner --file $file)"
    files_by_team_release["$team"]+=" $file"
done

#for x in "${!files_by_team_release[@]}"; do printf "[%q]=%q\n" "$x" "${files_by_team_release[$x]}" ; done

for team in "${!files_by_team_release[@]}" ; do
    branch_name=${team/ /_}-${topic}
    echo "[$team] :: [$branch_name] ${files_by_team_release[$team]}"

    git checkout -b $branch_name -t origin/master

    git add ${files_by_team_release[$team]}
    git commit \
        -m "[$team] $subject" \
        -m "$body"

    git stash
    git checkout master
    git stash pop
done

git checkout master
git stash list
git branch -va | grep -E "$topic"

for team in "${!files_by_team_release[@]}" ; do
    branch_name=${team/ /_}-${topic}
    git checkout $branch_name
    git show --stat
    echo
    echo 'Push? (Ctrl-C to cancel)'
    read
    git review -y -t $topic
done
git checkout master
