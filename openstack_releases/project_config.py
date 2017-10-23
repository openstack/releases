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


ZUUL_PROJECTS_URL = 'http://git.openstack.org/cgit/openstack-infra/project-config/plain/zuul.d/projects.yaml'  # noqa
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


# Which jobs are needed for which release types.
_RELEASE_JOBS_FOR_TYPE = {
    'std': [
        'openstack-server-release-jobs',    # old zuulv2 job name
        'publish-to-pypi',
        'release-openstack-server',
    ],
    'nodejs': [
        'nodejs4-publish-to-npm',
        'nodejs6-publish-to-npm',
    ],
    'puppet': [
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


def require_release_jobs_for_repo(deliverable_info, zuul_projects, repo,
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

    if repo not in zuul_projects:
        mk_error(
            'did not find %s in %s' % (repo, ZUUL_PROJECTS_FILENAME),
        )
    else:
        p = zuul_projects[repo]
        templates = p.get('templates', [])
        # NOTE(dhellmann): We don't mess around looking for individual
        # jobs, because we want projects to use the templates.
        expected_jobs = _RELEASE_JOBS_FOR_TYPE.get(
            release_type,
            _RELEASE_JOBS_FOR_TYPE['std'],
        )
        if expected_jobs:
            found_jobs = [
                j
                for j in templates
                if j in expected_jobs
            ]
            if len(found_jobs) == 0:
                mk_error(
                    '{filename} no release job specified for {repo}, '
                    'one of {expected!r} needs to be included in {existing!r} '
                    'or no release will be '
                    'published'.format(
                        filename=ZUUL_PROJECTS_FILENAME,
                        repo=repo,
                        expected=expected_jobs,
                        existing=templates,
                    ),
                )
            elif len(found_jobs) > 1:
                mk_warning(
                    '{filename} multiple release jobs specified for {repo}, '
                    '{existing!r} should include *one* of '
                    '{expected!r}, found {found!r}'.format(
                        filename=ZUUL_PROJECTS_FILENAME,
                        repo=repo,
                        expected=expected_jobs,
                        existing=templates,
                        found=found_jobs,
                    ),
                )
            # Check to see if we found jobs we did not expect to find.
            for wrong_type, wrong_jobs in _RELEASE_JOBS_FOR_TYPE.items():
                if wrong_type == release_type:
                    continue
                bad_jobs = [
                    j for j in wrong_jobs
                    if j in templates
                ]
                if bad_jobs:
                    mk_error(
                        '{filename} has unexpected release jobs '
                        '{bad_jobs!r} for release-type {wrong_type} '
                        'but {repo} uses release-type {release_type}'.format(
                            filename=ZUUL_PROJECTS_FILENAME,
                            repo=repo,
                            bad_jobs=bad_jobs,
                            wrong_type=wrong_type,
                            release_type=release_type,
                        )
                    )
    return
