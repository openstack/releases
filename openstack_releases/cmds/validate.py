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
import logging
import os
import os.path
import pkgutil
import re
import shutil
import sys
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
from openstack_releases import requirements
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
    'client-library',
    'service',
    'tempest-plugin',
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


def header(title):
    print('\n%s' % title)
    print('-' * len(title))


def is_a_hash(val):
    "Return bool indicating if val looks like a valid hash."
    return re.search('^[a-f0-9]{40}$', val, re.I) is not None


def validate_schema(deliverable_info, mk_warning, mk_error):
    header('Validate Schema')
    validator = jsonschema.Draft4Validator(_SCHEMA)
    for error in validator.iter_errors(deliverable_info):
        mk_error(str(error))


def validate_series_open(deliverable_info,
                         series_name, filename,
                         mk_warning, mk_error):
    "No releases in the new series until the previous one has a branch."
    header('Validate Series Open')
    if not deliverable_info.get('releases'):
        print('no releases, skipping')
        return
    if series_name == '_independent':
        # These rules don't apply to independent projects.
        print('rule does not apply to independent projects')
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


def deprecate_release_highlights(deliverable_info,
                                 mk_warning, mk_error):
    "No releases in the new series until the previous one has a branch."
    header('Deprecate Release Highlights')
    if not deliverable_info.get('releases'):
        return
    last_release = deliverable_info['releases'][-1]
    if 'highlights' in last_release:
        mk_error(
            'The per-release "highlights" feature is deprecated. '
            'Please use "cycle-highlights" for marketing notes '
            'and reno for release notes.'
        )


def validate_series_first(deliverable_info, series_name,
                          mk_warning, mk_error):
    "The first release in a series needs to end with '.0'."
    header('Validate Series First')
    # When the releases entry is present but empty, it's value may not
    # be a list, so we default to a list using 'or'.
    releases = deliverable_info.get('releases') or []
    if len(releases) != 1:
        # We only have to check this when the first release is being
        # applied in the file.
        print('not the first release')
        return
    if series_name == '_independent':
        # These rules don't apply to independent projects.
        print('rule does not apply to independent projects')
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
    header('Validate Bug Tracker')
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
    header('Validate Team')
    if 'team' not in deliverable_info:
        mk_error('No team name given')
    elif deliverable_info['team'] not in team_data:
        mk_warning('Team %r not in governance data' %
                   deliverable_info['team'])


def validate_release_notes(deliverable_info, mk_warning, mk_error):
    "Make sure the release notes page exists, if it is specified."
    header('Validate Release Notes')
    if 'release-notes' not in deliverable_info:
        print('no release-notes given')
        return
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
    header('Validate Type')
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
    header('Validate Model')
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


def clone_deliverable(deliverable_info, workdir, mk_warning, mk_error):
    """Clone all of the repositories for the deliverable into the workdir.

    Returns boolean indicating whether all of the clones could be
    performed as expected.

    """
    cloned = set()
    ok = True
    print('\nchecking out source code')
    for release in deliverable_info.get('releases', []):
        for project in release['projects']:
            if project['repo'] in cloned:
                continue
            cloned.add(project['repo'])
            if not gitutils.safe_clone_repo(workdir, project['repo'],
                                            project['hash'], mk_error):
                ok = False
    return ok


def _require_gitreview(workdir, repo, mk_error):
    print('\nlooking for .gitreview in %s' % repo)
    filename = os.path.join(
        workdir, repo, '.gitreview',
    )
    if not os.path.exists(filename):
        mk_error('%s has no .gitreview file' % (repo,))


def validate_gitreview(deliverable_info, workdir, mk_warning, mk_error):
    "Verify that all repos include a .gitreview file."
    header('Validate .gitreview')
    checked = set()
    for release in deliverable_info.get('releases', []):
        for project in release['projects']:
            if project['repo'] in checked:
                continue
            checked.add(project['repo'])
            version_exists = gitutils.commit_exists(
                workdir, project['repo'], release['version'],
            )
            if not version_exists:
                _require_gitreview(workdir, project['repo'], mk_error)


_TYPE_TO_RELEASE_TYPE = {
    'library': 'python-pypi',
    'service': 'python-service',
    'horizon-plugin': 'horizon',
}

_PYTHON_RELEASE_TYPES = ['python-service', 'python-pypi', 'neutron', 'horizon']


def get_release_type(deliverable_info, repo, workdir):
    """Return tuple with release type and boolean indicating whether it
    was explicitly set.

    """
    if 'release-type' in deliverable_info:
        return (deliverable_info['release-type'], True)

    from_type = _TYPE_TO_RELEASE_TYPE.get(deliverable_info.get('type'))
    if from_type is not None:
        return (from_type, False)

    if deliverable_info.get('include-pypi-link', False):
        return ('python-pypi', False)

    if puppetutils.looks_like_a_module(workdir, repo):
        return ('puppet', False)

    if npmutils.looks_like_a_module(workdir, repo):
        return ('nodejs', False)

    return ('python-service', False)


def validate_release_type(deliverable_info,
                          zuul_projects,
                          series_name,
                          workdir,
                          mk_warning,
                          mk_error):
    """Apply validation rules for the deliverable based on 'release-type'
    to the most recent release of a deliverable.

    """
    header('Validate release-type')

    link_mode = deliverable_info.get('artifact-link-mode', 'tarball')
    if link_mode == 'none':
        print('link-mode is "none", skipping release-type checks')
        return

    if not deliverable_info.get('releases'):
        print('no releases listed, skipping release-type checks')
        return

    release = deliverable_info['releases'][-1]
    for project in release['projects']:

        print('checking release-type for {}'.format(project['repo']))

        release_type, was_explicit = get_release_type(
            deliverable_info, project['repo'], workdir,
        )
        if was_explicit:
            print('found explicit release-type {!r}'.format(
                release_type))
        else:
            print('release-type not given, '
                  'guessing {!r}'.format(release_type))

        version_exists = gitutils.commit_exists(
            workdir, project['repo'], release['version'],
        )

        if not version_exists:
            project_config.require_release_jobs_for_repo(
                deliverable_info, zuul_projects,
                project['repo'],
                release_type, mk_warning, mk_error,
            )


def validate_tarball_base(deliverable_info,
                          workdir,
                          mk_warning, mk_error):

    link_mode = deliverable_info.get('artifact-link-mode', 'tarball')

    if link_mode != 'tarball':
        print('rule does not apply for link-mode {}, skipping'.format(
            link_mode))
        return
    if not deliverable_info.get('releases'):
        print('no releases, skipping')
        return

    release = deliverable_info['releases'][-1]
    for project in release['projects']:
        version_exists = gitutils.commit_exists(
            workdir, project['repo'], release['version'],
        )
        # Check that the sdist name and tarball-base name match.
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


def validate_pypi_permissions(deliverable_info, zuul_projects, workdir,
                              mk_warning, mk_error):

    header('Validate PyPI Permissions')

    for repo in deliverable_info['repository-settings'].keys():

        job_templates = zuul_projects.get(repo, {}).get('templates', [])

        # Look for jobs that appear to be talking about publishing to
        # PyPI. There are variations.
        pypi_jobs = [
            j
            for j in job_templates
            if 'pypi' in j
        ]

        if not pypi_jobs:
            print('rule does not apply to repos not publishing to PyPI')
            continue

        print('{} publishes to PyPI via {}'.format(repo, pypi_jobs))

        try:
            sdist = pythonutils.get_sdist_name(workdir, repo)
        except Exception as err:
            mk_warning(
                'Could not determine the sdist name '
                'for {} to check PyPI permissions: {}'.format(
                    repo, err)
            )
            continue

        # Names like "openstack_requirements" are translated to
        # "openstack-requirements" in the PyPI API.
        sdist = sdist.replace('_', '-')
        print('sdist name {!r}'.format(sdist))

        uploaders = pythonutils.get_pypi_uploaders(sdist)
        if not uploaders:
            mk_error(
                'could not find users with permission to upload packages '
                'for {}. Is the sdist name correct?'.format(sdist)
            )
        elif 'openstackci' not in uploaders:
            mk_error(
                'openstackci does not have permission to upload packages '
                'for {}. Current owners include: {}'.format(
                    sdist, ', '.join(sorted(uploaders)))
            )


def validate_releases(deliverable_info, zuul_projects,
                      series_name,
                      workdir,
                      mk_warning, mk_error):
    """Apply validation rules to the 'releases' list for the deliverable.
    """
    header('Validate Releases')

    release_model = get_model(deliverable_info, series_name)
    is_independent = (release_model == 'independent')

    # Remember which entries are new so we can verify that they
    # appear at the end of the file.
    new_releases = {}

    if release_model == 'untagged' and 'releases' in deliverable_info:
        mk_error('untagged deliverables should not have a "releases" section')
        return

    prev_version = None
    prev_projects = set()
    for release in deliverable_info.get('releases', []):

        print('\nchecking %s' % release['version'])

        for project in release['projects']:

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

                if not gitutils.safe_clone_repo(workdir, project['repo'],
                                                project['hash'], mk_error):
                    continue

                # Report if the version has already been
                # tagged. We expect it to not exist, but neither
                # case is an error because sometimes we want to
                # import history and sometimes we want to make new
                # releases.
                version_exists = gitutils.commit_exists(
                    workdir, project['repo'], release['version'],
                )
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
                    print('tag exists, skipping further validation')
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

                print('Found new version {} for {}'.format(
                    release['version'], project['repo']))
                new_releases[release['version']] = release
                if prev_projects and project['repo'] not in prev_projects:
                    print('not included in previous release for %s: %s' %
                          (prev_version, ', '.join(sorted(prev_projects))))
                else:

                    release_type, was_explicit = get_release_type(
                        deliverable_info, project['repo'], workdir,
                    )
                    if was_explicit:
                        print('found explicit release-type {!r}'.format(
                            release_type))
                    else:
                        print('release-type not given, '
                              'guessing {!r}'.format(release_type))

                    # If this is a puppet module, ensure
                    # that the tag and metadata file
                    # match.
                    if release_type == 'puppet':
                        print('applying puppet version rules')
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
                    if release_type == 'nodejs':
                        print('applying nodejs version rules')
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

                    # If we know the previous version and the
                    # project is a python deliverable make sure
                    # the requirements haven't changed in a way
                    # not reflecting the version.
                    if prev_version and release_type in _PYTHON_RELEASE_TYPES:
                        # For the master branch, enforce the
                        # rules. For other branches just warn if
                        # the rules are broken because there are
                        # cases where we do need to support point
                        # releases with requirements updates.
                        if series_name == defaults.RELEASE:
                            report = mk_error
                        else:
                            report = mk_warning
                        requirements.find_bad_lower_bound_increases(
                            workdir, project['repo'],
                            prev_version, release['version'], project['hash'],
                            report,
                        )

                    for e in versionutils.validate_version(
                            release['version'],
                            release_type=release_type,
                            pre_ok=(release_model in _USES_PREVER)):
                        msg = ('could not validate version %r: %s' %
                               (release['version'], e))
                        mk_error(msg)

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


def validate_new_releases(deliverable_info, deliverable_name,
                          team_data,
                          mk_warning, mk_error):

    """Apply validation rules that only apply to the current series.
    """
    header('Validate New Releases')
    if not deliverable_info.get('releases'):
        print('no releases, skipping')
        return

    final_release = deliverable_info['releases'][-1]
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
            'release %s is missing %s, '
            'which appears in the governance list: %s' %
            (final_release['version'], missing, expected_repos)
        )
    repository_settings = deliverable_info.get('repository-settings', {})
    for repo in actual_repos:
        if repo not in repository_settings:
            mk_error(
                'release %s includes repository %s '
                'that is not in the repository-settings section' %
                (final_release['version'], repo)
            )
    for missing in repository_settings.keys():
        if missing not in actual_repos:
            mk_warning(
                'release %s is missing %s, '
                'which appears in the repository-settings list' %
                (final_release['version'], missing)
            )


def validate_branch_prefixes(deliverable_info, mk_waring, mk_error):
    "Ensure all branches have good prefixes."
    header('Validate Branch Prefixes')
    branches = deliverable_info.get('branches', [])
    for branch in branches:
        prefix = branch['name'].split('/')[0]
        if prefix not in _VALID_BRANCH_PREFIXES:
            mk_error('branch name %s does not use a valid prefix: %s' % (
                branch['name'], _VALID_BRANCH_PREFIXES))


def _guess_deliverable_type(deliverable_name, deliverable_info):
    if 'tempest-plugin' in deliverable_name:
        return 'tempest-plugin'
    if 'type' in deliverable_info:
        return deliverable_info['type']
    return 'other'


def validate_stable_branches(deliverable_info,
                             deliverable_name,
                             workdir,
                             series_name,
                             mk_warning, mk_error):
    "Apply the rules for stable branches."
    header('Validate Stable Branches')
    if ('launchpad' in deliverable_info and
       deliverable_info['launchpad'] in _NO_STABLE_BRANCH_CHECK):
        print('rule does not apply to this repo, skipping')
        return

    branches = deliverable_info.get('branches', [])

    d_type = _guess_deliverable_type(deliverable_name, deliverable_info)
    if d_type == 'tempest-plugin' and branches:
        mk_error('Tempest plugins do not support branching.')
        return

    branch_mode = deliverable_info.get('stable-branch-type', 'std')

    known_releases = {
        r['version']: r
        for r in deliverable_info.get('releases', [])
    }
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
            else:
                for project in known_releases[location]['projects']:
                    if not gitutils.safe_clone_repo(workdir, project['repo'],
                                                    project['hash'], mk_error):
                        continue
                    _require_gitreview(workdir, project['repo'], mk_error)
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
                if not gitutils.safe_clone_repo(workdir, repo, loc, mk_error):
                    continue
                _require_gitreview(workdir, repo, mk_error)
                if not gitutils.commit_exists(workdir, repo, loc):
                    mk_error(
                        ('stable branches should be created from merged '
                         'commits but location %s for branch %s of %s '
                         'does not exist' % (
                             (loc, repo, branch['name'])))
                    )
        elif branch_mode == 'upstream':
            if not isinstance(location, six.string_types):
                mk_error(
                    ('branch location for %s is '
                     'expected to be a string but got a %s' % (
                         branch['name'], type(location)))
                )
        else:
            mk_error(
                ('unrecognized stable-branch-type %r' % (branch_mode,))
            )
        if branch_mode == 'upstream':
            mk_warning(
                'skipping branch name check for upstream mode'
            )
        elif series_name == '_independent':
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


def validate_feature_branches(deliverable_info,
                              deliverable_name,
                              workdir,
                              mk_warning, mk_error):
    "Apply the rules for feature branches."
    header('Validate Feature Branches')
    branches = deliverable_info.get('branches', [])

    d_type = _guess_deliverable_type(deliverable_name, deliverable_info)
    if d_type == 'tempest-plugin' and branches:
        mk_error('Tempest plugins do not support branching.')
        return

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
            _require_gitreview(workdir, repo, mk_error)


def validate_driverfixes_branches(deliverable_info,
                                  deliverable_name,
                                  workdir,
                                  mk_warning, mk_error):
    "Apply the rules for driverfixes branches."
    header('Validate driverfixes Branches')
    known_series = sorted(list(
        d for d in os.listdir('deliverables')
        if not d.startswith('_')
    ))
    branches = deliverable_info.get('branches', [])

    d_type = _guess_deliverable_type(deliverable_name, deliverable_info)
    if d_type == 'tempest-plugin' and branches:
        mk_error('Tempest plugins do not support branching.')
        return

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
            _require_gitreview(workdir, repo, mk_error)


def validate_branch_points(deliverable_info,
                           deliverable_name,
                           workdir,
                           mk_warning,
                           mk_error):
    # Make sure the branch points given are on the expected branches.

    known_releases = {
        r['version']: r
        for r in deliverable_info.get('releases', [])
    }
    branch_mode = deliverable_info.get('stable-branch-type', 'std')

    # Check for 'upstream' branches. These track upstream release names and
    # do not align with OpenStack series names.
    if branch_mode == 'upstream':
        return

    for branch in deliverable_info.get('branches', []):
        header('Validate Branch Points: {}'.format(branch['name']))
        try:
            prefix, series = branch['name'].split('/')
        except ValueError:
            print('could not parse the branch name, skipping')
            continue

        if prefix == 'feature':
            print('rule does not apply to feature branches')
            continue

        elif prefix == 'stable':
            expected = set([
                'master',
                branch['name'],
            ])
        else:
            # driverfixes
            expected = set([
                branch['name'],
                'stable/' + series,
            ])

        if prefix == 'stable' and branch_mode == 'std':
            # location is a version string, so we need to build the
            # map ourselves
            print('using hashes from release {}'.format(branch['location']))
            release = known_releases[branch['location']]
            location = {
                p['repo']: p['hash']
                for p in release['projects']
            }
        else:
            location = branch['location']

        for repo, hash in sorted(location.items()):
            print('\n{}'.format(repo))
            existing_branches = sorted([
                (b.partition('/origin/')[-1]
                 if b.startswith('remotes/origin/')
                 else b)
                for b in gitutils.get_branches(workdir, repo)
            ])

            # Remove the remote name prefix if it is present in the
            # branch name.
            containing = set(
                c.partition('/')[-1] if c.startswith('origin/') else c
                for c in gitutils.branches_containing(
                    workdir, repo, hash)
            )

            print('found {} on branches {} in {}'.format(
                hash, containing, repo))

            for missing in expected.difference(containing):
                if missing not in existing_branches:
                    print('branch {} does not exist in {}, skipping'.format(
                        branch['name'], repo))
                    continue

                if branch['name'] in existing_branches:
                    # The branch already exists but there is something
                    # wrong with the specification. This probably
                    # means someone tried to update the branch setting
                    # after creating the branch, so phrase the error
                    # message to reflect that.
                    mk_error(
                        '{} branch exists in {} and does not seem '
                        'to have been created from {}'.format(
                            branch['name'], repo, hash),
                    )
                else:
                    # The branch does not exist and the proposed point
                    # to create it is not on the expected source
                    # branch, so phrase the error message to reflect
                    # that.
                    mk_error(
                        'commit {} is not on the {} branch '
                        'but it is listed as the branch point for '
                        '{} to be created'.format(
                            hash, missing, branch['name']))


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
        '--debug',
        default=False,
        action='store_true',
        help='throw exception on error',
    )
    parser.add_argument(
        'input',
        nargs='*',
        help=('YAML files to validate, defaults to '
              'files changed in the latest commit'),
    )
    args = parser.parse_args()

    # Set up logging, including making some loggers quiet.
    logging.basicConfig(
        format='%(levelname)7s: %(message)s',
        stream=sys.stdout,
        level=logging.DEBUG,
    )
    logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)

    filenames = args.input or gitutils.find_modified_deliverable_files()
    if not filenames:
        print('no modified deliverable files and no arguments, '
              'skipping validation')
        return 0

    zuul_projects = project_config.get_zuul_project_data()

    team_data = governance.get_team_data()

    errors = []
    warnings = []

    workdir = tempfile.mkdtemp(prefix='releases-')
    print('creating temporary files in %s' % workdir)

    def cleanup_workdir():
        if args.cleanup:
            shutil.rmtree(workdir, True)
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
        deliverable_name = os.path.basename(filename)[:-5]  # strip .yaml

        if series_name in _CLOSED_SERIES:
            continue

        def mk_warning(msg):
            print('WARNING: {}'.format(msg))
            warnings.append('{}: {}'.format(filename, msg))

        def mk_error(msg):
            print('ERROR: {}'.format(msg))
            errors.append('{}: {}'.format(filename, msg))
            if args.debug:
                raise RuntimeError(msg)

        clone_deliverable(deliverable_info, workdir, mk_warning, mk_error)
        validate_schema(deliverable_info, mk_warning, mk_error)
        validate_bugtracker(deliverable_info, mk_warning, mk_error)
        validate_team(deliverable_info, team_data, mk_warning, mk_error)
        validate_release_notes(deliverable_info, mk_warning, mk_error)
        validate_type(deliverable_info, mk_warning, mk_error)
        validate_model(deliverable_info, series_name, mk_warning, mk_error)
        validate_release_type(
            deliverable_info,
            zuul_projects,
            series_name,
            workdir,
            mk_warning,
            mk_error,
        )
        validate_pypi_permissions(
            deliverable_info,
            zuul_projects,
            workdir,
            mk_warning,
            mk_error,
        )
        validate_gitreview(deliverable_info, workdir, mk_warning, mk_error)
        validate_releases(
            deliverable_info,
            zuul_projects,
            series_name,
            workdir,
            mk_warning,
            mk_error,
        )
        validate_tarball_base(
            deliverable_info,
            workdir,
            mk_warning,
            mk_error,
        )
        # Some rules only apply to the most current release.
        if series_name == defaults.RELEASE:
            validate_new_releases(
                deliverable_info,
                deliverable_name,
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
            deprecate_release_highlights(
                deliverable_info,
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
            deliverable_name,
            workdir,
            series_name,
            mk_warning,
            mk_error,
        )
        validate_feature_branches(
            deliverable_info,
            deliverable_name,
            workdir,
            mk_warning,
            mk_error,
        )
        validate_driverfixes_branches(
            deliverable_info,
            deliverable_name,
            workdir,
            mk_warning,
            mk_error,
        )
        validate_branch_points(
            deliverable_info,
            deliverable_name,
            workdir,
            mk_warning,
            mk_error,
        )

    header('Summary')

    print('\n\n%s warnings found' % len(warnings))
    for w in warnings:
        print(w)

    print('\n\n%s errors found' % len(errors))
    for e in errors:
        print(e)

    return 1 if errors else 0
