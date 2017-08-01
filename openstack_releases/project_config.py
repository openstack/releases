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

import requests

from openstack_releases import flags
from openstack_releases import yamlutils


ZUUL_LAYOUT_URL = 'http://git.openstack.org/cgit/openstack-infra/project-config/plain/zuul/layout.yaml'  # noqa
ZUUL_LAYOUT_FILENAME = 'openstack-infra/project-config/zuul/layout.yaml'

# We use this key to modify the data structure read from the zuul
# layout file. We don't control what are valid keys there, so make it
# easy to change the key we use, just in case.
_VALIDATE_KEY = 'validate-projects-by-name'


def get_zuul_layout_data(url=ZUUL_LAYOUT_URL):
    """Return the parsed data structure for the zuul/layout.yaml file.

    :param url: Optional URL to the location of the file. Defaults to
      the most current version in the public git repository.

    """
    r = requests.get(url)
    raw = yamlutils.loads(r.text)
    # Add a mapping from repo name to repo settings, since that is how
    # we access this most often.
    raw[_VALIDATE_KEY] = {
        p['name']: p
        for p in raw['projects']
    }
    return raw


# Which jobs are needed for which release types.
_RELEASE_JOBS_FOR_TYPE = {
    'std': [
        'nodejs4-publish-to-npm',
        'nodejs6-publish-to-npm',
        'openstack-server-release-jobs',
        'publish-to-pypi',
        'puppet-tarball-jobs',
        'puppet-release-jobs',
    ],
    'xstatic': [
        'xstatic-publish-jobs',
    ],
    'fuel': [
        # Fuel is manually packaged by the team at Mirantis.
    ],
    'openstack-manuals': [
        # openstack-manuals is not released, only generated content pushed
    ],
}


def require_release_jobs_for_repo(deliverable_info, zuul_layout, repo,
                                  release_type, mk_warning, mk_error):
    """Check the repository for release jobs.

    Returns a list of tuples containing a message and a boolean
    indicating if the message is an error.

    """
    # If the repository is configured as not having an artifact to
    # build, we don't need to check for any jobs.
    if flags.has_flag(deliverable_info, repo, flags.NO_ARTIFACT_BUILD_JOB):
        return

    # If the repository is retired, we don't need to check for any
    # jobs.
    if flags.has_flag(deliverable_info, repo, flags.RETIRED):
        return

    if repo not in zuul_layout[_VALIDATE_KEY]:
        mk_error(
            'did not find %s in %s' % (repo, ZUUL_LAYOUT_FILENAME),
        )
    else:
        p = zuul_layout[_VALIDATE_KEY][repo]
        templates = [
            t['name']
            for t in p.get('template', [])
        ]
        # NOTE(dhellmann): We don't mess around looking for individual
        # jobs, because we want projects to use the templates.
        expected_jobs = _RELEASE_JOBS_FOR_TYPE.get(
            release_type,
            _RELEASE_JOBS_FOR_TYPE['std'],
        )
        if expected_jobs:
            num_release_jobs = sum(
                j in templates
                for j in expected_jobs
            )
            if num_release_jobs == 0:
                mk_error(
                    '%s no release job specified for %s, '
                    'should be one of %r or no release will be '
                    'published' % (ZUUL_LAYOUT_FILENAME, repo, expected_jobs),
                )
            elif num_release_jobs > 1:
                mk_warning(
                    '%s multiple release jobs specified for %s, '
                    'should be *one* of %r'
                    % (ZUUL_LAYOUT_FILENAME, repo, expected_jobs),
                )
    return
