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

import os.path
import subprocess

import requests

# Disable warnings about insecure connections.
from requests.packages import urllib3
urllib3.disable_warnings()

CGIT_TEMPLATE = 'http://git.openstack.org/cgit/%s/commit/?id=%s'


def find_modified_deliverable_files():
    "Return a list of files modified by the most recent commit."
    results = subprocess.check_output(
        ['git', 'diff', '--name-only', '--pretty=format:', 'HEAD^']
    )
    filenames = [
        l.strip()
        for l in results.splitlines()
        if l.startswith('deliverables/')
    ]
    return filenames


def commit_exists(repo, ref):
    """Return boolean specifying whether the reference exists in the repository.

    Uses a cgit query instead of looking locally to avoid cloning a
    repository or having Depends-On settings in a commit message allow
    someone to fool the check.

    """
    url = CGIT_TEMPLATE % (repo, ref)
    response = requests.get(url)
    missing_commit = (
        (response.status_code // 100 != 2)
        or 'Bad object id' in response.text
    )
    return not missing_commit


def clone_repo(workdir, repo):
    "Check out the code."
    subprocess.check_call(
        ['zuul-cloner',
         '--workspace', workdir,
         'git://git.openstack.org',
         repo]
    )


def sha_for_tag(workdir, repo, version):
    """Return the SHA for a given tag
    """
    # git log 2.3.11 -n 1 --pretty=format:%H
    try:
        actual_sha = subprocess.check_output(
            ['git', 'log', str(version), '-n', '1', '--pretty=format:%H'],
            cwd=os.path.join(workdir, repo),
            stderr=subprocess.STDOUT,
        )
        actual_sha = actual_sha.strip()
    except subprocess.CalledProcessError as e:
        print('ERROR getting SHA for tag %r: %s [%s]' %
              (version, e, e.output.strip()))
        actual_sha = ''
    return actual_sha


def check_ancestry(workdir, repo, old_version, sha):
    "Check if the SHA is in the ancestry of the previous version."
    try:
        ancestors = subprocess.check_output(
            ['git', 'log', '--oneline', '--ancestry-path',
             '%s..%s' % (old_version, sha)],
            cwd=os.path.join(workdir, repo),
            stderr=subprocess.STDOUT,
        ).strip()
        return bool(ancestors)
    except subprocess.CalledProcessError as e:
        print('ERROR checking ancestry: %s [%s]' % (e, e.output.strip()))
        return False


def get_latest_tag(workdir, repo):
    try:
        return subprocess.check_output(
            ['git', 'describe', '--abbrev=0'],
            cwd=os.path.join(workdir, repo),
            stderr=subprocess.STDOUT,
        ).strip()
    except subprocess.CalledProcessError as e:
        print('WARNING failed to retrieve latest tag: %s [%s]' %
              (e, e.output.strip()))
        return None
