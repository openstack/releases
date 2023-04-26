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

"""Tools for working with requirements lists."""

import logging
import os.path

import pkg_resources

from openstack_releases import gitutils
from openstack_releases import processutils
from openstack_releases import pythonutils
from openstack_releases import versionutils

LOG = logging.getLogger(__name__)


def find_bad_lower_bound_increases(workdir, repo,
                                   start_version, new_version, hash,
                                   report):
    if (new_version.split('.')[-1] == '0' or
            versionutils.looks_like_preversion(new_version)):
        # There is no need to look at the requirements so don't do the
        # extra work.
        return
    start_reqs = get_requirements_at_ref(workdir, repo, start_version)
    hash_reqs = get_requirements_at_ref(workdir, repo, hash)
    compare_lower_bounds(start_reqs, hash_reqs, report)


def compare_lower_bounds(start_reqs, hash_reqs, report):
    for (section, name), req in sorted(hash_reqs.items()):
        if section:
            display_name = '[{}]{}'.format(section, name)
        else:
            display_name = name

        if (section, name) not in start_reqs:
            report('New dependency {}'.format(display_name))

        else:
            old_req = start_reqs[(section, name)]
            old_min = get_min_specifier(old_req.specifier)
            new_min = get_min_specifier(req.specifier)

            if old_min is None and new_min is None:
                # No minimums are specified.
                continue

            if old_min is None:
                # There is no minimum on the old dependency but there
                # is now a new minimum.
                report(('Added minimum version for dependency {} of {} '
                        'without at least incrementing minor number').format(
                    display_name, new_min))
                continue

            if new_min is None:
                # There was a minimum but it has been removed.
                continue

            if old_min.version not in req.specifier:
                # The old minimum is not in the new spec.
                report(('Changed supported versions for dependency {} from {} '
                        'to {} without at least incrementing minor number').format(
                    display_name, old_req.specifier, req.specifier))


def get_min_specifier(specifier_set):
    "Find the specifier in the set that controls the lower bound."
    for s in specifier_set:
        if '>' in s.operator:
            return s


def get_requirements_at_ref(workdir, repo, ref):
    """Check out the repo at the ref and load the list of requirements."""
    body = ''

    try:
        dest = gitutils.clone_repo(workdir, repo, ref=ref)
        processutils.check_call(['python3', '-m', 'build', '--sdist', '--wheel'], cwd=dest)
        sdist_name = pythonutils.get_sdist_name(workdir, repo)
        requirements_filename = os.path.join(
            dest, sdist_name + '.egg-info', 'requires.txt',
        )
        if os.path.exists(requirements_filename):
            with open(requirements_filename, 'r') as f:
                body = f.read()
        else:
            # The package has no dependencies.
            pass
    except Exception:
        # We've had a few cases where a previous version had an issue and could
        # no longer be installed. In this case, just move along.
        LOG.warning('Unable to create sdist, unable to get requirements.')
        LOG.warning('!!! Perform manual comparison for requirements changes'
                    '!!!')

    return parse_requirements(body)


def parse_requirements(body):
    """Given the requires.txt file for an sdist, parse it.

    Returns a dictionary mapping (section, pkg name) to the
    requirements specifier.

    Parses files that look like:

    pbr>=1.6
    keyring==7.3
    requests>=2.5.2
    PyYAML>=3.1.0
    yamlordereddictloader
    prompt_toolkit
    tqdm
    packaging>=15.2
    mwclient==0.8.1
    jsonschema>=2.6.0
    Jinja2>=2.6
    parawrap
    reno>=2.0.0
    sphinx>=1.6.2

    [sphinxext]
    sphinx<1.6.1,>=1.5.1
    openstackdocstheme
    sphinxcontrib.datatemplates
    icalendar

    """
    requirements = {}
    section = ''
    for line in body.splitlines():
        # Ignore blank lines and comments
        if (not line.strip()) or line.startswith('#'):
            continue
        if line.startswith('['):
            section = line.lstrip('[').rstrip(']')
            continue

        try:
            parsed_req = pkg_resources.Requirement.parse(line)
        except ValueError:
            LOG.warning('failed to parse %r', line)
        else:
            requirements[(section, parsed_req.name)] = parsed_req

    return requirements
