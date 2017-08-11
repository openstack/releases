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
import pkgutil
import re
import shutil
import tempfile

import jsonschema
import requests
import six

# Disable warnings about insecure connections.
from requests.packages import urllib3

from openstack_releases import defaults
from openstack_releases import gitutils
from openstack_releases import governance
from openstack_releases import npmutils
from openstack_releases import project_config
from openstack_releases import puppetutils
from openstack_releases import pythonutils
from openstack_releases import versionutils
from openstack_releases import yamlutils

urllib3.disable_warnings()

_CLOSED_SERIES = set([
    'austin',
    'bexar',
    'cactus',
    'diablo',
    'essex',
    'folsom',
    'grizzly',
    'havana',
    'icehouse',
    'juno',
    'kilo',
    'liberty',
])
_VALID_MODELS = set([
    'cycle-with-milestones',
    'cycle-with-intermediary',
    'cycle-trailing',
    'independent',
    'untagged',
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
_VALID_BRANCH_PREFIXES = set([
    'stable',
    'feature',
    'driverfixes',
])
_NO_STABLE_BRANCH_CHECK = set([
    'gnocchi',
    'rally',
    'puppet-pacemaker',  # tracks upstream version
])
_PLEASE = ('It is too expensive to determine this value during '
           'the site build, please set it explicitly.')
_SCHEMA = yamlutils.loads(
    pkgutil.get_data('openstack_releases', 'schema.yaml').decode('utf-8')
)


def is_a_hash(val):
    "Return bool indicating if val looks like a valid hash."
    return re.search('^[a-f0-9]{40}$', val, re.I) is not None


def validate_schema(deliverable_info, mk_warning, mk_error):
    validator = jsonschema.Draft4Validator(_SCHEMA)
    for error in validator.iter_errors(deliverable_info):
        mk_error(str(error))


def validate_series_open(deliverable_info,
                         series_name, filename,
                         mk_warning, mk_error):
    "No releases in the new series until the previous one has a branch."
    if not deliverable_info.get('releases'):
        return
    if series_name == '_independent':
        # These rules don't apply to independent projects.
        return
    deliverables_dir = os.path.dirname(
        os.path.dirname(filename)
    )
    deliverable_base = os.path.basename(filename)
    pattern = os.path.join(
        deliverables_dir,
        '*',
        deliverable_base,
    )
    # NOTE(dhellmann): When projects switch from _independent to
    # cycle-based models, we don't want to require a
    # stable/_independent branch, so ignore those files.
    all_deliverable_files = [
        name
        for name in sorted(glob.glob(pattern))
        if '/_independent/' not in name
    ]
    idx = all_deliverable_files.index(filename)
    if idx == 0:
        # This is the first cycle-based deliverable file.
        return
    previous_deliverable_file = all_deliverable_files[idx - 1]
    previous_series = os.path.basename(
        os.path.dirname(previous_deliverable_file)
    )
    expected_branch = 'stable/' + previous_series
    with open(previous_deliverable_file, 'r', encoding='utf-8') as f:
        previous_deliverable = yamlutils.loads(f.read())
        if not previous_deliverable:
            # An empty file results in None, so convert to dict to
            # make using the value easier.
            previous_deliverable = {}
    for branch in previous_deliverable.get('branches', []):
        if branch['name'] == expected_branch:
            # Everything is OK
            return
    mk_warning(
        'There is no {} branch defined in {}. Is the {} series open?'.format(
            expected_branch, previous_deliverable_file, series_name))


def validate_series_first(deliverable_info, series_name,
                          mk_warning, mk_error):
    "The first release in a series needs to end with '.0'."
    # When the releases entry is present but empty, it's value may not
    # be a list, so we default to a list using 'or'.
    releases = deliverable_info.get('releases') or []
    if len(releases) != 1:
        # We only have to check this when the first release is being
        # applied in the file.
        return
    if series_name == '_independent':
        # These rules don't apply to independent projects.
        return
    versionstr = releases[0]['version']
    patchlevel = versionstr.rpartition('.')[-1]
    if not (patchlevel == '0' or patchlevel.startswith('0b')):
        mk_error(
            'Initial releases in a series must increment at '
            'least the minor version or be beta versions. %r' % (versionstr,)
        )


def validate_bugtracker(deliverable_info, mk_warning, mk_error):
    "Look for the bugtracker info"
    if 'launchpad' in deliverable_info:
        lp_name = deliverable_info['launchpad']
        try:
            lp_resp = requests.get('https://api.launchpad.net/1.0/' + lp_name)
        except requests.exceptions.ConnectionError as e:
            # The flakey Launchpad API failed. Don't punish the user for that.
            mk_warning('Could not verify launchpad project %s (%s)' %
                       (lp_name, e))
        else:
            if (lp_resp.status_code // 100) == 4:
                mk_error('Launchpad project %s does not exist' % lp_name)
    elif 'storyboard' in deliverable_info:
        try:
            sb_id = int(deliverable_info['storyboard'])
        except (TypeError, ValueError):
            mk_error('Invalid storyboard ID, must be a number: %s' %
                     deliverable_info['storyboard'])
            return
        try:
            projects_resp = requests.get(
                'https://storyboard.openstack.org/api/v1/projects'
            )
        except requests.exceptions.ConnectionError as e:
            # The flakey Launchpad API failed. Don't punish the user for that.
            mk_warning('Could not verify storyboard project %s (%s)' %
                       (sb_id, e))
        else:
            if (projects_resp.status_code // 100) == 4:
                mk_warning(
                    'Could not verify storyboard project, API call failed.'
                )
            for project in projects_resp.json():
                if sb_id == project.get('id'):
                    break
            else:
                mk_error(
                    'Did not find a storyboard project with ID %s' % sb_id
                )
    else:
        mk_error('No launchpad or storyboard project given')


def validate_team(deliverable_info, team_data, mk_warning, mk_error):
    "Look for the team name"
    if 'team' not in deliverable_info:
        mk_error('No team name given')
    elif deliverable_info['team'] not in team_data:
        mk_warning('Team %r not in governance data' %
                   deliverable_info['team'])


def validate_release_notes(deliverable_info, mk_warning, mk_error):
    "Make sure the release notes page exists, if it is specified."
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


def validate_type(deliverable_info, mk_warning, mk_error):
    "Determine the deliverable type. Require an explicit value."
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


def get_model(deliverable_info, series_name):
    "Return the release model from the deliverable info."
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
    return release_model


def validate_model(deliverable_info, series_name, mk_warning, mk_error):
    "Require a valid release model"
    release_model = get_model(deliverable_info, series_name)
    if release_model not in _VALID_MODELS:
        mk_error(
            'Unknown release model %r, must be one of %r' %
            (release_model, sorted(list(_VALID_MODELS)))
        )

    # If the project is release:independent, make sure
    # that's where the deliverable file is.
    if release_model == 'independent' and series_name != '_independent':
        mk_error(
            'uses the independent release model '
            'and should be in the _independent '
            'directory'
        )

    # If the project is declaring some other release model, make sure
    # it is not in h the _independent directory.
    if series_name == '_independent':
        model_value = deliverable_info.get('release-model',
                                           'independent')
        if model_value != 'independent':
            mk_error(
                'deliverables in the _independent directory '
                'should all use the independent release model'
            )


def validate_releases(deliverable_info, zuul_layout,
                      series_name,
                      workdir,
                      mk_warning, mk_error):
    """Apply validation rules to the 'releases' list for the deliverable.
    """
    release_model = get_model(deliverable_info, series_name)
    is_independent = (release_model == 'independent')

    # Remember which entries are new so we can verify that they
    # appear at the end of the file.
    new_releases = {}

    release_type = deliverable_info.get('release-type', 'std')
    link_mode = deliverable_info.get('artifact-link-mode', 'tarball')

    if release_model == 'untagged' and 'releases' in deliverable_info:
        mk_error('untagged deliverables should not have a "releases" section')
        return

    prev_version = None
    prev_projects = set()
    for release in deliverable_info.get('releases', []):

        print('checking %s' % release['version'])

        for project in release['projects']:

            # Check for release jobs (if we ship a tarball)
            if link_mode != 'none':
                project_config.require_release_jobs_for_repo(
                    deliverable_info, zuul_layout, project['repo'],
                    release_type, mk_warning, mk_error,
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

                # Ensure we have a local copy of the repository so we
                # can scan for values that are more difficult to get
                # remotely.
                try:
                    gitutils.clone_repo(workdir, project['repo'], project['hash'])
                except Exception as err:
                    mk_error('Could not clone repository %s at %s: %s' % (
                        project['repo'], project['hash'], err))
                    # No point in running extra checks if we can't
                    # clone the repository.
                    continue

                # Report if the SHA exists or not (an error if it
                # does not).
                sha_exists = gitutils.commit_exists(
                    workdir, project['repo'], project['hash'],
                )
                if not sha_exists:
                    mk_error('No commit %(hash)r in %(repo)r'
                             % project)
                    # No point in running extra checks if the SHA just
                    # doesn't exist.
                    continue

                version_exists = gitutils.tag_exists(
                    project['repo'], release['version'],
                )

                # Check that the sdist name and tarball-base name match.
                if link_mode == 'tarball':
                    try:
                        sdist = pythonutils.get_sdist_name(workdir,
                                                           project['repo'])
                    except Exception as err:
                        msg = 'Could not get the name of {} for version {}: {}'.format(
                            project['repo'], release['version'], err)
                        if version_exists:
                            # If there was a problem with an existing
                            # release, treat it as a warning so we
                            # don't prevent new releases.
                            mk_warning(msg)
                        else:
                            mk_error(msg)
                    else:
                        if sdist is not None:
                            expected = project.get(
                                'tarball-base',
                                os.path.basename(project['repo']),
                            )
                            if sdist != expected:
                                if 'tarball-base' in project:
                                    action = 'is set to'
                                else:
                                    action = 'defaults to'
                                mk_error(
                                    ('tarball-base for %s %s %s %r '
                                     'but the sdist name is actually %r. ' +
                                     _PLEASE)
                                    % (project['repo'], release['version'],
                                       action, expected, sdist))

                # Report if the version has already been
                # tagged. We expect it to not exist, but neither
                # case is an error because sometimes we want to
                # import history and sometimes we want to make new
                # releases.
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
                    if prev_projects and project['repo'] not in prev_projects:
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

                        # If this is a puppet module, ensure
                        # that the tag and metadata file
                        # match.
                        if puppetutils.looks_like_a_module(workdir,
                                                           project['repo']):
                            puppet_ver = puppetutils.get_version(
                                workdir, project['repo'])
                            if puppet_ver != release['version']:
                                mk_error(
                                    '%s metadata contains "%s" '
                                    'but is being tagged "%s"' % (
                                        project['repo'],
                                        puppet_ver,
                                        release['version'],
                                    )
                                )

                        # If this is a npm module, ensure
                        # that the tag and metadata file
                        # match.
                        if npmutils.looks_like_a_module(workdir,
                                                        project['repo']):
                            npm_ver = npmutils.get_version(
                                workdir, project['repo'])
                            if npm_ver != release['version']:
                                mk_error(
                                    '%s package.json contains "%s" '
                                    'but is being tagged "%s"' % (
                                        project['repo'],
                                        npm_ver,
                                        release['version'],
                                    )
                                )

                        if is_independent:
                            mk_warning('skipping descendant test for '
                                       'independent project, verify '
                                       'branch manually')

                        else:
                            # If this is the first version in the series,
                            # check that the commit is actually on the
                            # targeted branch.
                            if not gitutils.check_branch_sha(workdir,
                                                             project['repo'],
                                                             series_name,
                                                             defaults.RELEASE,
                                                             project['hash']):
                                msg = '%s %s not present in %s branch' % (
                                    project['repo'],
                                    project['hash'],
                                    series_name,
                                    )
                                mk_error(msg)

                            if prev_version:
                                # Check to see if we are re-tagging the same
                                # commit with a new version.
                                old_sha = gitutils.sha_for_tag(
                                    workdir,
                                    project['repo'],
                                    prev_version,
                                )
                                if old_sha == project['hash']:
                                    # FIXME(dhellmann): This needs a test.
                                    print('Retagging the SHA with '
                                          'a new version')
                                else:
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
                                        mk_error(
                                            '%s %s receiving %s '
                                            'is not a descendant of %s' % (
                                                project['repo'],
                                                project['hash'],
                                                release['version'],
                                                prev_version,
                                            )
                                        )

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
    if not deliverable_info.get('releases'):
        return
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


def validate_branch_prefixes(deliverable_info, mk_waring, mk_error):
    "Ensure all branches have good prefixes."
    branches = deliverable_info.get('branches', [])
    for branch in branches:
        prefix = branch['name'].split('/')[0]
        if prefix not in _VALID_BRANCH_PREFIXES:
            mk_error('branch name %s does not use a valid prefix: %s' % (
                branch['name'], _VALID_BRANCH_PREFIXES))


def validate_stable_branches(deliverable_info, workdir,
                             series_name,
                             mk_warning, mk_error):
    "Apply the rules for stable branches."
    if ('launchpad' in deliverable_info and
       deliverable_info['launchpad'] in _NO_STABLE_BRANCH_CHECK):
        return

    branch_mode = deliverable_info.get('stable-branch-type', 'std')

    branches = deliverable_info.get('branches', [])
    known_releases = list(
        r['version']
        for r in deliverable_info.get('releases', [])
    )
    known_series = sorted(list(
        d for d in os.listdir('deliverables')
        if not d.startswith('_')
    ))
    for branch in branches:
        try:
            prefix, series = branch['name'].split('/')
        except ValueError:
            mk_error(
                ('stable branch name expected to be stable/name '
                 'but got %s') % (branch['name'],))
            continue
        if prefix != 'stable':
            continue
        location = branch.get('location')
        if branch_mode == 'std':
            if not isinstance(location, six.string_types):
                mk_error(
                    ('branch location for %s is '
                     'expected to be a string but got a %s' % (
                         branch['name'], type(location)))
                )
            if location not in known_releases:
                mk_error(
                    ('stable branches must be created from existing '
                     'tagged releases, and %s for %s is not found in the '
                     'list of releases for this deliverable' % (
                         location, branch['name']))
                )
        elif branch_mode == 'tagless':
            if not isinstance(location, dict):
                mk_error(
                    ('branch location for %s is '
                     'expected to be a mapping but got a %s' % (
                         branch['name'], type(location)))
                )
                # The other rules aren't going to be testable, so skip them.
                continue
            for repo, loc in sorted(location.items()):
                if not is_a_hash(loc):
                    mk_error(
                        ('tagless stable branches should be created '
                         'from commits by SHA but location %s for '
                         'branch %s of %s does not look '
                         'like a SHA' % (
                             (loc, repo, branch['name'])))
                    )
                    # We can't clone the location if it isn't a SHA.
                    continue
                # Ensure we have a local copy of the repository so we
                # can scan for values that are more difficult to get
                # remotely.
                try:
                    gitutils.clone_repo(workdir, repo, loc)
                except Exception as err:
                    mk_error('Could not clone repository %s at %s: %s' % (
                        repo, loc, err))
                    # No point in running extra checks if we can't
                    # clone the repository.
                    continue
                if not gitutils.commit_exists(workdir, repo, loc):
                    mk_error(
                        ('stable branches should be created from merged '
                         'commits but location %s for branch %s of %s '
                         'does not exist' % (
                             (loc, repo, branch['name'])))
                    )
        else:
            mk_error(
                ('unrecognized stable-branch-type %r' % (branch_mode,))
            )
        if series_name == '_independent':
            if series not in known_series:
                mk_error(
                    ('stable branches must be named for known series '
                     'but %s was not found in %s' % (
                         branch['name'], known_series))
                )
        else:
            if series != series_name:
                mk_error(
                    ('cycle-based projects must match series names '
                     'for stable branches. %s should be stable/%s' % (
                         branch['name'], series_name))
                )


def validate_feature_branches(deliverable_info, workdir, mk_warning, mk_error):
    "Apply the rules for feature branches."
    branches = deliverable_info.get('branches', [])
    for branch in branches:
        try:
            prefix, series = branch['name'].split('/')
        except ValueError:
            mk_error(
                ('feature branch name expected to be feature/name '
                 'but got %s') % (branch['name'],))
            continue
        if prefix != 'feature':
            continue
        location = branch['location']
        if not isinstance(location, dict):
            mk_error(
                ('branch location for %s is '
                 'expected to be a mapping but got a %s' % (
                     branch['name'], type(location)))
            )
            # The other rules aren't going to be testable, so skip them.
            continue
        for repo, loc in sorted(location.items()):
            if not is_a_hash(loc):
                mk_error(
                    ('feature branches should be created from commits by SHA '
                     'but location %s for branch %s of %s does not look '
                     'like a SHA' % (
                         (loc, repo, branch['name'])))
                )
            if not gitutils.commit_exists(workdir, repo, loc):
                mk_error(
                    ('feature branches should be created from merged commits '
                     'but location %s for branch %s of %s does not exist' % (
                         (loc, repo, branch['name'])))
                )


def validate_driverfixes_branches(deliverable_info, workdir, mk_warning, mk_error):
    "Apply the rules for driverfixes branches."
    known_series = sorted(list(
        d for d in os.listdir('deliverables')
        if not d.startswith('_')
    ))
    branches = deliverable_info.get('branches', [])
    for branch in branches:
        try:
            prefix, series = branch['name'].split('/')
        except ValueError:
            mk_error(
                ('driverfixes branch name expected to be driverfixes/name '
                 'but got %s') % (branch['name'],))
            continue
        if prefix != 'driverfixes':
            continue
        location = branch['location']
        if series not in known_series:
            mk_error(
                ('driverfixes branches must be named for known series '
                 'but %s was not found in %s' % (
                     branch['name'], known_series))
            )
        if not isinstance(location, dict):
            mk_error(
                ('branch location for %s is '
                 'expected to be a mapping but got a %s' % (
                     branch['name'], type(location)))
            )
            # The other rules aren't going to be testable, so skip them.
            continue
        for repo, loc in sorted(location.items()):
            if not is_a_hash(loc):
                mk_error(
                    ('driverfixes branches should be created from commits by SHA '
                     'but location %s for branch %s of %s does not look '
                     'like a SHA' % (
                         (loc, repo, branch['name'])))
                )
            if not gitutils.commit_exists(workdir, repo, loc):
                mk_error(
                    ('driverfixes branches should be created from merged commits '
                     'but location %s for branch %s of %s does not exist' % (
                         (loc, repo, branch['name'])))
                )


# if the branch already exists, the name is by definition valid
# if the branch exists, the data in the map must match reality
#
# FIXME(dhellmann): these two rules become more challenging to
# implement when we think about EOLed branches. I'm going to punt on
# that for now, and if it turns into an issue we can think about how
# to handle validation while still allowing branches to be deleted.


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
        print('no modified deliverable files and no arguments, '
              'skipping validation')
        return 0

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
        with open(filename, 'r', encoding='utf-8') as f:
            deliverable_info = yamlutils.loads(f.read())

        series_name = os.path.basename(
            os.path.dirname(filename)
        )

        if series_name in _CLOSED_SERIES:
            continue

        def mk_warning(msg):
            print('WARNING: {}'.format(msg))
            warnings.append('{}: {}'.format(filename, msg))

        def mk_error(msg):
            print('ERROR: {}'.format(msg))
            errors.append('{}: {}'.format(filename, msg))

        validate_schema(deliverable_info, mk_warning, mk_error)
        validate_bugtracker(deliverable_info, mk_warning, mk_error)
        validate_team(deliverable_info, team_data, mk_warning, mk_error)
        validate_release_notes(deliverable_info, mk_warning, mk_error)
        validate_type(deliverable_info, mk_warning, mk_error)
        validate_model(deliverable_info, series_name, mk_warning, mk_error)
        # NOTE(dhellmann): A side-effect of validate_releases() is
        # that all of the repos mentioned in the deliverable file are
        # cloned. No validation that needs the repo to be checked out
        # locally should happen before validate_releases() is called.
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
            validate_series_open(
                deliverable_info,
                series_name,
                filename,
                mk_warning,
                mk_error,
            )
        validate_series_first(
            deliverable_info,
            series_name,
            mk_warning,
            mk_error,
        )
        validate_branch_prefixes(
            deliverable_info,
            mk_warning,
            mk_error,
        )
        validate_stable_branches(
            deliverable_info,
            workdir,
            series_name,
            mk_warning,
            mk_error,
        )
        validate_feature_branches(
            deliverable_info,
            workdir,
            mk_warning,
            mk_error,
        )
        validate_driverfixes_branches(
            deliverable_info,
            workdir,
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
