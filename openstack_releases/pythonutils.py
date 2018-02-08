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

import json
import logging
import os
import os.path

import requests

from openstack_releases import processutils

LOG = logging.getLogger(__name__)


def get_sdist_name(workdir, repo):
    "Check out the code."
    dest = os.path.join(workdir, repo)
    if not os.path.exists(os.path.join(dest, 'setup.py')):
        # Not a python project
        return None
    use_tox = repo.endswith('/pbr')
    if use_tox and not os.path.exists(os.path.join(dest, '.tox', 'venv')):
        # Use tox to set up a virtualenv so we can install the
        # dependencies for the package. This only seems to be
        # necessary for pbr, but...
        processutils.check_output(
            ['tox', '-e', 'venv', '--notest'],
            cwd=dest,
        )
    if use_tox:
        python = '.tox/venv/bin/python'
    else:
        python = 'python'
    # Run it once and discard the result to ensure any setup_requires
    # dependencies are installed.
    cmd = [python, 'setup.py', '--name']
    processutils.check_output(cmd, cwd=dest)
    # Run it again to get a clean version of the name.
    print('Running: %s in %s' % (' '.join(cmd), dest))
    out = processutils.check_output(cmd, cwd=dest).decode('utf-8')
    print('Results: %s' % (out,))
    name = out.splitlines()[-1].strip()
    return name


def guess_sdist_name(project):
    "Guess the name without checking out the repo."
    repo_base = project['repo'].rsplit('/')[-1]
    base = project.get('tarball-base', repo_base)
    return base


def get_pypi_info(dist_name):
    "Return PyPI information for the distribution."
    LOG.debug('looking at PyPI for {}'.format(dist_name))
    url = 'https://pypi.python.org/pypi/{}/json'.format(dist_name)
    LOG.debug(url)
    try:
        return requests.get(url).json()
    except json.decoder.JSONDecodeError:
        return {}
