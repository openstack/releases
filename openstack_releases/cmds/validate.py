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

"""Try to verify that the latest commit contains valid SHA values.

"""

from __future__ import print_function

import argparse
import atexit
import glob
import os
import os.path
import re
import shutil
import tempfile

import requests
import yaml

# Disable warnings about insecure connections.
from requests.packages import urllib3

from openstack_releases import defaults
from openstack_releases import gitutils
from openstack_releases import governance
from openstack_releases import project_config
from openstack_releases import versionutils

urllib3.disable_warnings()

_VALID_MODELS = set([
    'cycle-with-milestones',
    'cycle-with-intermediary',
    'cycle-trailing',
    'independent',
])
_USES_PREVER = set([
    'cycle-with-milestones',
    'cycle-trailing',
])
_VALID_TYPES = set([
    'horizon-plugin',
    'library',
    'service',
    'other',
])


def is_a_hash(val):
    "Return bool indicating if val looks like a valid hash."
    return re.search('^[a-f0-9]{40}$', val, re.I) is not None


def validate_launchpad(deliverable_info, mk_warning, mk_error):
    "Look for the launchpad project"
    try:
        lp_name = deliverable_info['launchpad']
    except KeyError:
        mk_error('No launchpad project given')
    else:
        lp_resp = requests.get('https://api.launchpad.net/1.0/' + lp_name)
        if (lp_resp.status_code // 100) == 4:
            mk_error('Launchpad project %s does not exist' % lp_name)


def validate_team(deliverable_info, team_data, mk_warning, mk_error):
    "Look for the team name"
    if 'team' not in deliverable_info:
        mk_error('No team name given')
    elif deliverable_info['team'] not in team_data:
        mk_warning('Team %r not in governance data' %
                   deliverable_info['team'])


def validate_metadata(deliverable_info, team_data, mk_warning, mk_error):
    """Look at the general metadata in the deliverable file.
    """

    # Make sure the release notes page exists, if it is specified.
    if 'release-notes' in deliverable_info:
        notes_link = deliverable_info['release-notes']
        if isinstance(notes_link, dict):
            links = list(notes_link.values())
        else:
            links = [notes_link]
        for link in links:
            rn_resp = requests.get(link)
            if (rn_resp.status_code // 100) != 2:
                mk_error('Could not fetch release notes page %s: %s' %
                         (link, rn_resp.status_code))
    else:
        print('no release-notes specified')

    # Determine the deliverable type. Require an explicit value.
    deliverable_type = deliverable_info.get('type')
    if not deliverable_type:
        mk_error(
            'No deliverable type, must be one of %r' %
            sorted(list(_VALID_TYPES))
        )
    elif deliverable_type not in _VALID_TYPES:
        mk_error(
            'Invalid deliverable type %r, must be one of %r' %
            (deliverable_type, sorted(list(_VALID_TYPES)))
        )


def validate_releases(deliverable_info, zuul_layout,
                      series_name,
                      workdir,
                      mk_warning, mk_error):
    """Apply validation rules to the 'releases' list for the deliverable.
    """

    # Determine the release model. Don't require independent
    # projects to redundantly specify that they are independent by
    # including the value in their deliverablefile, but everyone
    # else must provide a valid value.
    is_independent = (series_name == '_independent')
    if is_independent:
        release_model = 'independent'
    else:
        release_model = deliverable_info.get('release-model',
                                             'UNSPECIFIED')
    if release_model not in _VALID_MODELS:
        mk_error(
            'Unknown release model %r, must be one of %r' %
            (release_model, sorted(list(_VALID_MODELS)))
        )

    # Remember which entries are new so we can verify that they
    # appear at the end of the file.
    new_releases = {}

    release_type = deliverable_info.get('release-type', 'std')
    link_mode = deliverable_info.get('artifact-link-mode', 'tarball')

    prev_version = None
    prev_projects = set()
    for release in deliverable_info['releases']:

        for project in release['projects']:

            # Check for release jobs (if we ship a tarball)
            if link_mode != 'none':
                project_config.require_release_jobs_for_repo(
                    deliverable_info, zuul_layout, project['repo'],
                    release_type, mk_warning, mk_error,
                )

            # If the project is release:independent, make sure
            # that's where the deliverable file is.
            if is_independent:
                if series_name != '_independent':
                    mk_warning(
                        '%s uses the independent release model '
                        'and should be in the _independent '
                        'directory' % project['repo'],
                    )

            # Check the SHA specified for the tag.
            print('%s SHA %s ' % (project['repo'], project['hash']))

            if not is_a_hash(project['hash']):
                mk_error(
                    ('%(repo)s version %(version)s release from '
                     '%(hash)r, which is not a hash') % {
                         'repo': project['repo'],
                         'hash': project['hash'],
                         'version': release['version'],
                         }
                )
            else:
                # Report if the SHA exists or not (an error if it
                # does not).
                sha_exists = gitutils.commit_exists(
                    project['repo'], project['hash'],
                )
                if not sha_exists:
                    mk_error('No commit %(hash)r in %(repo)r'
                             % project)
                # Report if the version has already been
                # tagged. We expect it to not exist, but neither
                # case is an error because sometimes we want to
                # import history and sometimes we want to make new
                # releases.
                version_exists = gitutils.tag_exists(
                    project['repo'], release['version'],
                )
                gitutils.clone_repo(workdir, project['repo'])
                if version_exists:
                    actual_sha = gitutils.sha_for_tag(
                        workdir,
                        project['repo'],
                        release['version'],
                    )
                    if actual_sha != project['hash']:
                        mk_error(
                            ('Version %s in %s is on '
                             'commit %s instead of %s') %
                            (release['version'],
                             project['repo'],
                             actual_sha,
                             project['hash']))
                else:
                    print('Found new version {}'.format(release['version']))
                    new_releases[release['version']] = release
                    if project['repo'] not in prev_projects:
                        print('not included in previous release for %s: %s' %
                              (prev_version, ', '.join(sorted(prev_projects))))
                    else:

                        for e in versionutils.validate_version(
                                release['version'],
                                release_type=release_type,
                                pre_ok=(release_model in _USES_PREVER)):
                            msg = ('could not validate version %r: %s' %
                                   (release['version'], e))
                            mk_error(msg)

                        # Check to see if we are re-tagging the same
                        # commit with a new version.
                        old_sha = gitutils.sha_for_tag(
                            workdir,
                            project['repo'],
                            prev_version,
                        )
                        if old_sha == project['hash']:
                            print('Retagging the SHA with a new version')
                        elif not is_independent:
                            # Check to see if the commit for the new
                            # version is in the ancestors of the
                            # previous release, meaning it is actually
                            # merged into the branch.
                            is_ancestor = gitutils.check_ancestry(
                                workdir,
                                project['repo'],
                                prev_version,
                                project['hash'],
                            )
                            if not is_ancestor:
                                if series_name == '_independent':
                                    save = mk_warning
                                else:
                                    save = mk_error
                                save(
                                    '%s %s receiving %s '
                                    'is not a descendant of %s' % (
                                        project['repo'],
                                        project['hash'],
                                        release['version'],
                                        prev_version,
                                    )
                                )
                            mk_warning('skipping descendant test for '
                                       'independent project, verify '
                                       'branch manually')
        prev_version = release['version']
        prev_projects = set(p['repo'] for p in release['projects'])

        # Make sure that new entries have been appended to the file.
        for v, nr in new_releases.items():
            if nr != deliverable_info['releases'][-1]:
                msg = ('new release %s must be listed last, '
                       'with one new release per patch' % nr['version'])
                mk_error(msg)


def validate_new_releases(deliverable_info, filename,
                          team_data,
                          mk_warning, mk_error):
    """Apply validation rules that only apply to the current series.
    """
    final_release = deliverable_info['releases'][-1]
    deliverable_name = os.path.basename(filename)[:-5]  # strip .yaml
    expected_repos = set(
        r.name
        for r in governance.get_repositories(
            team_data,
            deliverable_name=deliverable_name,
        )
    )
    link_mode = deliverable_info.get('artifact-link-mode', 'tarball')
    if link_mode != 'none' and not expected_repos:
        mk_error('unable to find deliverable %s in the governance list' %
                 deliverable_name)
    actual_repos = set(
        p['repo']
        for p in final_release.get('projects', [])
    )
    for extra in actual_repos.difference(expected_repos):
        mk_warning(
            'release %s includes repository %s '
            'that is not in the governance list' %
            (final_release['version'], extra)
        )
    for missing in expected_repos.difference(actual_repos):
        mk_warning(
            'release %s is missing %s from the governance list' %
            (final_release['version'], missing)
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--no-cleanup',
        dest='cleanup',
        default=True,
        action='store_false',
        help='do not remove temporary files',
    )
    parser.add_argument(
        'input',
        nargs='*',
        help=('YAML files to validate, defaults to '
              'files changed in the latest commit'),
    )
    args = parser.parse_args()

    filenames = args.input or gitutils.find_modified_deliverable_files()
    if not filenames:
        print('no modified deliverable files, validating all releases from %s'
              % defaults.RELEASE)
        filenames = glob.glob('deliverables/' + defaults.RELEASE + '/*.yaml')

    zuul_layout = project_config.get_zuul_layout_data()

    team_data = governance.get_team_data()

    errors = []
    warnings = []

    workdir = tempfile.mkdtemp(prefix='releases-')
    print('creating temporary files in %s' % workdir)

    def cleanup_workdir():
        if args.cleanup:
            try:
                shutil.rmtree(workdir)
            except:
                pass
        else:
            print('not cleaning up %s' % workdir)
    atexit.register(cleanup_workdir)

    for filename in filenames:
        print('\nChecking %s' % filename)
        if not os.path.isfile(filename):
            print("File was deleted, skipping.")
            continue
        with open(filename, 'r') as f:
            deliverable_info = yaml.load(f.read())

        series_name = os.path.basename(
            os.path.dirname(filename)
        )

        def mk_warning(msg):
            print('WARNING: {}'.format(msg))
            warnings.append('{}: {}'.format(filename, msg))

        def mk_error(msg):
            print('ERROR: {}'.format(msg))
            errors.append('{}: {}'.format(filename, msg))

        validate_launchpad(deliverable_info, mk_warning, mk_error)
        validate_team(deliverable_info, team_data, mk_warning, mk_error)
        validate_metadata(
            deliverable_info,
            team_data,
            mk_warning,
            mk_error,
        )
        validate_releases(
            deliverable_info,
            zuul_layout,
            series_name,
            workdir,
            mk_warning,
            mk_error,
        )
        # Some rules only apply to the most current release.
        if series_name == defaults.RELEASE:
            validate_new_releases(
                deliverable_info,
                filename,
                team_data,
                mk_warning,
                mk_error,
            )

    if warnings:
        print('\n\n%s warnings found' % len(warnings))
        for w in warnings:
            print(w)

    if errors:
        print('\n\n%s errors found' % len(errors))
        for e in errors:
            print(e)

    return 1 if errors else 0
