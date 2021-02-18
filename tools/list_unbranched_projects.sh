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
function help {
# Display helping message
cat <<EOF
usage: $0 [<args>]

Retrieve unbranched projects for maintained series.
Can be used to retrieve branch inconsistencies on maintained series.

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


GERRIT_URL="https://review.opendev.org"
TOOLSDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASEDIR=$(dirname $TOOLSDIR)
source $TOOLSDIR/functions
enable_tox_venv

series=($(list-maintained-series))

# Make sure no pager is configured so the output is not blocked
export PAGER=

for current_series in "${series[@]}"; do
    echo -e "\nUnbranched projects for ${current_series}:\n"
    grep -L "stable/${current_series}" ${BASEDIR}/deliverables/${current_series}/*.yaml | \
        sed 's@'"${BASEDIR}"'\/@@g' | \
        grep -v tempest | \
        grep -v patrol
done
