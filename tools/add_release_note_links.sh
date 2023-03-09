#!/bin/bash
#
# Add release notes links to deliverable files when they page exists
# and the link is not already in the file.
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

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 SERIES RELEASE_ID"
    echo "Example: $0 antelope 2023.1"
    exit 1
fi

SERIES="$1"
RELEASE_ID="$2"

# Set up and activate the virtualenv that contains the
# edit-deliverable command.
tox -e venv --notest
source .tox/venv/bin/activate

function url_exists {
    local url="$1"

    code=$(curl --silent -I -w "%{http_code}" -o /dev/null "$url")
    if [[ $code = 200 ]]; then
        return 0
    else
        return 1
    fi
}

for filename in deliverables/$SERIES/*.yaml; do
    deliverable=$(basename $filename .yaml)
    echo -n "$deliverable "
    base="https://docs.openstack.org/releasenotes/${deliverable}"
    main_url="${base}/index.html"
    if ! url_exists $main_url; then
        echo "no notes at all, skipping"
        continue
    fi
    series_url="${base}/${RELEASE_ID}.html"
    if ! url_exists $series_url; then
        echo "no release notes page at $series_url"
    else
        echo "OK"
        edit-deliverable $SERIES $deliverable set-release-notes "$series_url"
    fi
done
