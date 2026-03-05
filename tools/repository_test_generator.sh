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

# This script generates DNM patches to check the gate state of deliverables.

function help {
    # Display helping message
    cat <<EOF
usage: $0 [<args>] <repo> [<repo>...]

This script generates DNM patches to check the gate health of
deliverables in the current cycle.

Arguments:
    -d, --debug         Turn on the debug mode
    -h, --help          show this help message and exit
examples:
    $(basename $0) oslo.db
    $(basename $0) nova neutron
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


TOOLSDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASEDIR=$(dirname $TOOLSDIR)
source $TOOLSDIR/functions
enable_tox_venv

deliverables="$@"

# Make sure no pager is configured so the output is not blocked
export PAGER=

setup_temp_space 'repository-test-generator'
cd ${MYTMPDIR}


function generate_dnm_patch_for_repo {
    echo
    echo "Processing repo ${repo}..."
    clone_repo "openstack/${repo}"
    pushd openstack/${repo}
    if [[ $? -eq 0 ]]; then
        file_to_edit=$(find -mindepth 2 -maxdepth 2 -type f -size +0 -name "*.py" | head -1)
        if [[ -z "${file_to_edit}" ]]; then
            file_to_edit=tox.ini
        fi
        echo "# do-not-merge change" >>${file_to_edit}
        git add ${file_to_edit}
        git commit -s -m "DNM: gate health test" \
            --trailer="Generated-By:openstack/releases:tools/repository_test_generator.sh"
        git show --stat
        git review -t "release-health-check"
        popd
    else
        echo "Something went wrong with ${repo}..."
    fi
}


for repo in ${deliverables}; do
    generate_dnm_patch_for_repo "${repo}"
done
