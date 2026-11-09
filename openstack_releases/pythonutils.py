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

import configparser
import json
import logging
import os
import os.path
import sys
import time
import xmlrpc.client

from packaging import utils as packaging_utils
import requests

from openstack_releases import processutils

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

LOG = logging.getLogger(__name__)


def get_sdist_name(workdir: str, repo: str) -> str | None:
    """Find the name of the sdist."""
    dest = os.path.join(workdir, repo)

    # prefer pyproject.toml files
    pyproject_path = os.path.join(dest, 'pyproject.toml')
    if os.path.exists(pyproject_path):
        with open(pyproject_path, 'rb') as f:
            metadata = tomllib.load(f)
        name = metadata.get('project', {}).get('name')
        if name:
            return name

    # ...with a setup.cfg fallback. We ignore setup.py since this should never
    # have a name attribute set if using pbr
    setupcfg_path = os.path.join(dest, 'setup.cfg')
    if os.path.exists(setupcfg_path):
        config = configparser.ConfigParser(interpolation=None)
        config.read(setupcfg_path, encoding='utf-8')
        name = config.get('metadata', 'name', fallback=None)
        if name:
            return name

    LOG.debug(
        'did not find a name in pyproject.toml or setup.cfg for %s', repo
    )
    return None


def build_sdist(workdir: str, repo: str) -> None:
    """Build the sdist."""
    dest = os.path.join(workdir, repo)

    build_path = os.path.join(dest, 'dist')
    if os.path.exists(build_path):
        # sdist already built, skip rebuilding it
        return None

    if not any(
        os.path.exists(os.path.join(dest, filename))
        for filename in ('pyproject.toml', 'setup.cfg')
    ):
        LOG.debug(
            'did not find pyproject.toml or setup.cfg; maybe %s is not '
            'a python project?',
            repo
        )
        return None

    # Set some flags to turn off pbr functionality that we don't need.
    flags = {
        'SKIP_GENERATE_RENO': '1',
        'SKIP_GENERATE_AUTHORS': '1',
        'SKIP_WRITE_GIT_CHANGELOG': '1',
    }
    cmd = ['python3', '-m', 'build', '--sdist', '--wheel']
    processutils.check_call(cmd, cwd=dest, env=flags)


def check_readme_format(workdir: str, repo: str) -> None:
    """Verify that the README format looks OK."""
    dest = os.path.join(workdir, repo)
    if not any(
        os.path.exists(os.path.join(dest, filename))
        for filename in ('pyproject.toml', 'setup.cfg', 'setup.py')
    ):
        LOG.debug(
            'did not find pyproject.toml or setup.py, maybe %s is not '
            'a python project',
            repo
        )
        return None

    # Check if the sdist build has been done
    build_path = os.path.join(dest, 'dist')
    if not os.path.exists(build_path):
        build_sdist(workdir, repo)

    # NOTE(dhellmann): This relies on validate being run via tox so
    # that python3 is present and the twine package is installed.
    processutils.check_call(
        ['twine', 'check', os.path.join(build_path, '*')],
        cwd=dest,
    )


def get_pypi_info(dist_name):
    "Return PyPI information for the distribution."
    canonical_name = packaging_utils.canonicalize_name(dist_name)
    LOG.debug('looking at PyPI for {!r}'.format(canonical_name))
    url = 'https://pypi.org/pypi/{}/json'.format(canonical_name)
    try:
        info = requests.get(url).json()
        if info == {'message': 'Not Found'}:
            LOG.debug('{} package not found on PyPI'.format(canonical_name))
            return {}
        return info
    except json.decoder.JSONDecodeError:
        LOG.debug('Error parsing JSON response from PyPI')
        return {}


def _get_pypi_roles(dist_name):
    client = xmlrpc.client.ServerProxy('https://pypi.org/pypi')
    LOG.debug('retrieving roles for {!r}'.format(
        dist_name))
    return client.package_roles(dist_name)


def get_pypi_uploaders(dist_name):
    roles = _get_pypi_roles(dist_name)
    if not roles:
        # Sleep one second before retrying, to avoid PyPI returning
        # TooManyRequests and hiding the real issue
        time.sleep(1)
        canonical_name = packaging_utils.canonicalize_name(dist_name)
        roles = _get_pypi_roles(canonical_name)
    uploaders = set(
        acct
        for role, acct in roles
        if role in ('Owner', 'Maintainer')
    )
    LOG.debug('found: {}'.format(sorted(uploaders)))
    return uploaders
