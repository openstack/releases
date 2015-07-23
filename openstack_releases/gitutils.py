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

import subprocess

import requests

# Disable warnings about insecure connections.
from requests.packages import urllib3
urllib3.disable_warnings()

CGIT_TEMPLATE = 'http://git.openstack.org/cgit/%s/commit/?id=%s'


def find_modified_deliverable_files():
    "Return a list of files modified by the most recent commit."
    results = subprocess.check_output(
        ['git', 'show', '--name-only', '--pretty=format:']
    )
    filenames = [
        l.strip()
        for l in results.splitlines()
        if l.startswith('deliverables/')
    ]
    return filenames


def commit_exists(repo, hash):
    """Return boolean specifying whether the hash exists in the repository.

    Uses a cgit query instead of looking locally to avoid cloning a
    repository or having Depends-On settings in a commit message allow
    someone to fool the check.

    """
    url = CGIT_TEMPLATE % (repo, hash)
    response = requests.get(url)
    missing_commit = (
        (response.status_code // 100 != 2)
        or 'Bad object id' in response.text
    )
    return not missing_commit
