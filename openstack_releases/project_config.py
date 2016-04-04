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
import yaml


ZUUL_LAYOUT_URL = 'http://git.openstack.org/cgit/openstack-infra/project-config/plain/zuul/layout.yaml'  # noqa

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
    raw = yaml.safe_load(r.text)
    # Add a mapping from repo name to repo settings, since that is how
    # we access this most often.
    raw[_VALIDATE_KEY] = {
        p['name']: p
        for p in raw['projects']
    }
    return raw


def require_release_jobs_for_repo(zuul_layout, repo):
    """Check the repository for release jobs.

    Returns a list of error messages if there are no jobs.

    """
    errors = []

    if repo not in zuul_layout[_VALIDATE_KEY]:
        errors.append(
            'did not find %s in '
            'openstack-infra/project-config/zuul/layout.yaml' % repo
        )
    else:
        p = zuul_layout[_VALIDATE_KEY][repo]
        templates = [
            t['name']
            for t in p.get('template', [])
        ]
        # NOTE(dhellmann): We don't mess around looking for individual
        # jobs, because we want projects to use the templates.
        if not ('openstack-server-release-jobs' in templates or
                'publish-to-pypi' in templates):
            errors.append(
                'openstack-infra/project-config/zuul/layout.yaml has '
                'neither openstack-server-release-jobs '
                'nor publish-to-pypi defined for %s so no release '
                'will be published' % (repo,)
            )
        if ('openstack-server-release-jobs' in templates and
                'publish-to-pypi' in templates):
            errors.append(
                'openstack-infra/project-config/zuul/layout.yaml has '
                'both openstack-server-release-jobs '
                'and publish-to-pypi defined for %s' % (repo,)
            )
    return errors
