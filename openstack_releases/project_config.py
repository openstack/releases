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

"""Work with the project-config repository.
"""

import glob
import logging
import os
import os.path

import requests

from openstack_releases import yamlutils


LOG = logging.getLogger()

ZUUL_PROJECTS_URL = 'https://opendev.org/openstack-infra/project-config/raw/branch/master/zuul.d/projects.yaml'  # noqa
ZUUL_PROJECTS_FILENAME = 'openstack-infra/project-config/zuul.d/projects.yaml'

# We use this key to modify the data structure read from the zuul
# layout file. We don't control what are valid keys there, so make it
# easy to change the key we use, just in case.
_VALIDATE_KEY = 'validate-projects-by-name'


def get_zuul_project_data(url=ZUUL_PROJECTS_URL):
    """Return the data from the zuul.d/projects.yaml file.

    :param url: Optional URL to the location of the file. Defaults to
      the most current version in the public git repository.

    """
    r = requests.get(url)
    raw = yamlutils.loads(r.text)
    # Convert the raw list to a mapping from repo name to repo
    # settings, since that is how we access this most often.
    #
    # The inputs are like:
    #
    # - project:
    #     name: openstack/oslo.config
    #     templates:
    #       - system-required
    #       - openstack-python-jobs
    #       - openstack-python35-jobs
    #       - publish-openstack-sphinx-docs
    #       - check-requirements
    #       - lib-forward-testing
    #       - release-notes-jobs
    #       - periodic-newton
    #       - periodic-ocata
    #       - periodic-pike
    #       - publish-to-pypi
    #
    # And the output is:
    #
    #  openstack/oslo.config:
    #     templates:
    #       - system-required
    #       - openstack-python-jobs
    #       - openstack-python35-jobs
    #       - publish-openstack-sphinx-docs
    #       - check-requirements
    #       - lib-forward-testing
    #       - release-notes-jobs
    #       - periodic-newton
    #       - periodic-ocata
    #       - periodic-pike
    #       - publish-to-pypi
    #
    return {
        p['project']['name']: p['project']
        for p in raw
    }


def read_templates_from_repo(workdir, repo_name):
    """Read the zuul settings from a repo and return them.

    Read all of the zuul settings from the YAML files, parse them,
    and return the project templates.

    :param workdir: Working directory
    :type workdir: str
    :param repo_name: Repository name
    :type repo_name: str

    """
    root = os.path.join(workdir, repo_name)
    candidates = [
        '.zuul.yaml',
        'zuul.yaml',
        '.zuul.d/*.yaml',
        'zuul.d/*.yaml',
    ]
    results = []
    for pattern in candidates:
        LOG.debug('trying {}'.format(pattern))
        if '*' in pattern:
            filenames = glob.glob(os.path.join(root, pattern))
            if not filenames:
                LOG.debug('did not find {}'.format(pattern))
                continue
        else:
            filenames = [os.path.join(root, pattern)]
        for filename in filenames:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    body = f.read()
                results.extend(yamlutils.loads(body))
                LOG.debug('read {}'.format(pattern))
            except Exception as e:
                LOG.debug('failed to read {}: {}'.format(pattern, e))
    # Find the project settings
    project_info = [
        s['project']
        for s in results
        if 'project' in s
    ]
    templates = []
    for p in project_info:
        templates.extend(p.get('templates', []))
    return templates


# Which jobs are needed for which release types.
_RELEASE_JOBS_FOR_TYPE = {
    'python-service': [
        'publish-to-pypi',
        'publish-to-pypi-stable-only',
    ],
    'python-pypi': [
        'publish-to-pypi',
        'publish-to-pypi-stable-only',
    ],
    'neutron': [
        'publish-to-pypi',
        'publish-to-pypi-stable-only',
    ],
    'horizon': [
        'publish-to-pypi',
        'publish-to-pypi-stable-only',
    ],
    'nodejs': [
        'nodejs4-publish-to-npm',
        'nodejs6-publish-to-npm',
        'nodejs8-publish-to-npm',
    ],
    'puppet': [
        'puppet-tarball-jobs',
        'puppet-release-jobs',
    ],
    'xstatic': [
        'publish-to-pypi',
        'publish-to-pypi-stable-only',
    ],
    'fuel': [
        # Fuel is manually packaged by the team at Mirantis.
    ],
    'openstack-manuals': [
        # openstack-manuals is not released, only generated content pushed
    ],
    'manila-image-elements': [
        'manila-image-elements-publish-artifacts',
    ],
    'openstack-virtual-baremetal': [
        'docs-on-readthedocs',
    ],
}


def require_release_jobs_for_repo(deliv, repo, release_type, context):

    """Check the repository for release jobs.

    Returns a list of tuples containing a message and a boolean
    indicating if the message is an error.

    """
    # If the repository is configured as not having an artifact to
    # build, we don't need to check for any jobs.
    if repo.no_artifact_build_job:
        LOG.debug('{} has no-artifact-build-job set, skipping'.format(
            repo.name))
        return

    # If the repository is retired, we don't need to check for any
    # jobs.
    if repo.is_retired:
        LOG.debug('{} is retired, skipping'.format(repo.name))
        return

    # NOTE(dhellmann): We don't mess around looking for individual
    # jobs, because we want projects to use the templates.
    expected_jobs = _RELEASE_JOBS_FOR_TYPE.get(
        release_type,
        _RELEASE_JOBS_FOR_TYPE['python-service'],
    )
    if not expected_jobs:
        LOG.debug('no expected jobs for release type {}, skipping'.format(
            release_type))
        return

    found_jobs = []

    # Start by looking at the global project-config settings.
    if repo.name in context.zuul_projects:
        LOG.debug('found {} in project-config settings'.format(
            repo.name))
        p = context.zuul_projects[repo.name]
        templates = p.get('templates', [])
        found_jobs.extend(
            j
            for j in templates
            if j in expected_jobs
        )

    # Look for settings within the repo.
    #
    # NOTE(dhellmann): We only need this until zuul grows the API to
    # feed us this information via its API.
    if not found_jobs:
        LOG.debug('looking in {} for zuul settings'.format(
            repo.name))
        templates = read_templates_from_repo(context.workdir, repo.name)
        found_jobs.extend(
            j
            for j in templates
            if j in expected_jobs
        )

    if len(found_jobs) == 0:
        context.error(
            '{filename} no release job specified for {repo}, '
            'one of {expected!r} needs to be included in {existing!r} '
            'or no release will be '
            'published'.format(
                filename=ZUUL_PROJECTS_FILENAME,
                repo=repo.name,
                expected=expected_jobs,
                existing=templates,
            ),
        )
    elif len(found_jobs) > 1:
        context.warning(
            '{filename} multiple release jobs specified for {repo}, '
            '{existing!r} should include *one* of '
            '{expected!r}, found {found!r}'.format(
                filename=ZUUL_PROJECTS_FILENAME,
                repo=repo.name,
                expected=expected_jobs,
                existing=templates,
                found=found_jobs,
            ),
        )
    # Check to see if we found jobs we did not expect to find.
    for wrong_type, wrong_jobs in _RELEASE_JOBS_FOR_TYPE.items():
        if wrong_type == release_type:
            continue
        # "bad" jobs are any that are attached to the repo but
        # are not supported by the release-type of the repo
        bad_jobs = [
            j for j in wrong_jobs
            if j in templates and j not in expected_jobs
        ]
        if bad_jobs:
            context.error(
                '{filename} has unexpected release jobs '
                '{bad_jobs!r} for release-type {wrong_type} '
                'but {repo} uses release-type {release_type}'.format(
                    filename=ZUUL_PROJECTS_FILENAME,
                    repo=repo.name,
                    bad_jobs=bad_jobs,
                    wrong_type=wrong_type,
                    release_type=release_type,
                )
            )
    return
