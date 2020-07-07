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
    echo
    echo "Example: $(basename $0) victoria oslo.rootwrap"
    echo "Example: $(basename $0) independent reno bugfix"
    echo
    echo "For further details about how to use the command:"
    echo "tox -e venv -- list-unreleased-changes --help"
    exit 1
fi

if [[ -z "$VIRTUAL_ENV" ]]; then
    if [[ ! -d .tox/venv ]]; then
        tox -e venv --notest
    fi
    source ./.tox/venv/bin/activate
fi

list-unreleased-changes $@
