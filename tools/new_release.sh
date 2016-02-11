#!/bin/bash
#
# Script to add one new release to a deliverable file.
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
    echo "Usage: new_release.sh series deliverable updatetype"
    echo
    echo "Example: new_release.sh mitaka oslo.rootwrap feature"
    echo "Example: new_release.sh independent reno bugfix"
}

if [ $# -lt 3 ]; then
    usage
    exit 2
fi

if [[ -z "$VIRTUAL_ENV" ]]; then
    if [[ ! -d .tox/venv ]]; then
        tox -e venv --notest
    fi
    source ./.tox/venv/bin/activate
fi

new-release $@
