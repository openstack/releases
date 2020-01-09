#!/usr/bin/env bash
#
# Wrapper script to locate run pre-defined queries and if needed create new
# releases
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

set -e

function usage {
    echo "Usage: make_missing_releases.sh <series> <stage>"
    echo
    echo "Valid values for stage are:"
    echo "    cwi-m) Used at the m{1,2,3} to run 'interactive release on"
    echo "           cycle-with-intermediary libraries"
    echo
    echo "Wrapper script to locate run pre-defined queries and if "\
         "needed create new releases"
}

# Run a command but echo it first, kind of a light-weight set -x but avoids
# opencoding things and there for glogic errors
function v_run {
    echo "$*"
    "$@"
}

if [ $# -lt 2 ]; then
    usage
    exit 2
fi

TOOLSDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASEDIR=$(dirname $TOOLSDIR)

# FIXME(tonyb): We *almost* have this in 'functions' update enable_tox_venv()
# and use that everywhere
if [[ -z "$VIRTUAL_ENV" ]]; then
    if [[ ! -d .tox/venv ]]; then
        (cd $BASEDIR && tox -e venv --notest)
    fi
    source $BASEDIR/.tox/venv/bin/activate
fi

stable_branch=''
interactive=''
series=$1

case "$2" in
    # Used at the m{1,2,3} to run 'interactive release on
    # cycle-with-intermediary libraries
    cwi-m)
        interactive='--interactive'
        release_type='feature'
        sieve='--model=cycle-with-intermediary --type=library'
    ;;
#    m3)
#        stable_branch=''  # TODO: Should we create stable branches from these releases?
#        release_type='feature'  # TODO: Do we always want this to be a feature?
#        sieve='--type=client-library'
#    ;;
#    rc)
#        stable_branch='--stable-branch'
#        release_type='rc'
#        sieve='--model=cycle-with-rc'
#    ;;
#    final_check)
#        stable_branch='--stable-branch'
#        release_type='feature'
#        sieve='--model=cycle-with-intermediary'
#    ;;
    *)
        usage
        exit 2
    ;;
esac

echo "Collecting deliverables for ${series}: ${sieve}"
declare -a deliverables=($(list-deliverables ${sieve} --unreleased --series ${series}))
processed=1
for deliverable in ${deliverables[@]} ; do
    if [ -n "$interactive" ] ; then
        clear
        echo $(( ${#deliverables[@]} - $processed )) deliverables to go after this one
        processed=$(( $processed + 1 ))
    fi

    v_run new-release $interactive $stable_branch $series $deliverable $release_type
done
