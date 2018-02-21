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
import re
import shutil
import sys
import tempfile

import requests
import six

# Disable warnings about insecure connections.
from requests.packages import urllib3

from openstack_releases import defaults
from openstack_releases import deliverable
from openstack_releases import gitutils
from openstack_releases import governance
from openstack_releases import npmutils
from openstack_releases import project_config
from openstack_releases import puppetutils
from openstack_releases import pythonutils
from openstack_releases import requirements
from openstack_releases import versionutils
from openstack_releases import yamlutils

LOG = logging.getLogger()

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
    'mitaka',
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


def header(title):
    print('\n%s' % title)
    print('-' * len(title))


def is_a_hash(val):
    "Return bool indicating if val looks like a valid hash."
    return re.search('^[a-f0-9]{40}$', val, re.I) is not None


def validate_series_open(deliverable_info,
                         series_name, filename,
                         messages):
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
    messages.warning(
        'There is no {} branch defined in {}. Is the {} series open?'.format(
            expected_branch, previous_deliverable_file, series_name))


def deprecate_release_highlights(deliverable_info,
                                 messages):
    "No releases in the new series until the previous one has a branch."
    header('Deprecate Release Highlights')
    if not deliverable_info.get('releases'):
        return
    last_release = deliverable_info['releases'][-1]
    if 'highlights' in last_release:
        messages.error(
            'The per-release "highlights" feature is deprecated. '
            'Please use "cycle-highlights" for marketing notes '
            'and reno for release notes.'
        )


def validate_series_first(deliverable_info, series_name,
                          messages):
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
        messages.error(
            'Initial releases in a series must increment at '
            'least the minor version or be beta versions. %r' % (versionstr,)
        )


def validate_bugtracker(deliv, messages):
    "Look for the bugtracker info"
    header('Validate Bug Tracker')
    lp_name = deliv.launchpad_id
    sb_id = deliv.storyboard_id
    if lp_name:
        try:
            lp_resp = requests.get('https://api.launchpad.net/1.0/' + lp_name)
        except requests.exceptions.ConnectionError as e:
            # The flakey Launchpad API failed. Don't punish the user for that.
            messages.warning('Could not verify launchpad project %s (%s)' %
                             (lp_name, e))
        else:
            if (lp_resp.status_code // 100) == 4:
                messages.error('Launchpad project %s does not exist' % lp_name)
        LOG.debug('launchpad project ID {}'.format(lp_name))
    elif sb_id:
        try:
            projects_resp = requests.get(
                'https://storyboard.openstack.org/api/v1/projects'
            )
        except requests.exceptions.ConnectionError as e:
            # The flakey Launchpad API failed. Don't punish the user for that.
            messages.warning('Could not verify storyboard project %s (%s)' %
                             (sb_id, e))
        else:
            if (projects_resp.status_code // 100) == 4:
                messages.warning(
                    'Could not verify storyboard project, API call failed.'
                )
            for project in projects_resp.json():
                if sb_id == project.get('id'):
                    break
            else:
                messages.error(
                    'Did not find a storyboard project with ID %s' % sb_id
                )
            LOG.debug('storyboard project ID {}'.format(sb_id))
    else:
        messages.error('No launchpad or storyboard project given')


def validate_team(deliv, team_data, messages):
    "Look for the team name"
    header('Validate Team')
    if deliv.team not in team_data:
        messages.warning('Team %r not in governance data' %
                         deliv.team)
    LOG.debug('owned by team {}'.format(deliv.team))


def validate_release_notes(deliv, messages):
    "Make sure the release notes page exists, if it is specified."
    header('Validate Release Notes')
    notes_link = deliv.release_notes
    if not notes_link:
        print('no release-notes given')
        return
    if isinstance(notes_link, dict):
        # Dictionary mapping repositories to links. We don't want any
        # repositories that are not known, so check that as well as
        # the actual links.
        for repo_name in sorted(notes_link.keys()):
            if repo_name not in deliv.known_repo_names:
                messages.error(
                    'linking to release notes for unknown '
                    'repository {}'.format(
                        repo_name)
                )
        links = list(notes_link.values())
    else:
        links = [notes_link]
    for link in links:
        rn_resp = requests.get(link)
        if (rn_resp.status_code // 100) != 2:
            messages.error('Could not fetch release notes page %s: %s' %
                           (link, rn_resp.status_code))
        else:
            LOG.debug('{} OK'.format(link))


def validate_model(deliv, series_name, messages):
    "Require a valid release model"
    header('Validate Model')

    if not deliv.is_independent and not deliv.model:
        # If the deliverable is not independent it must declare a
        # release model.
        messages.error(
            'no release-model specified',
        )

    if deliv.model == 'independent' and deliv.series != 'independent':
        # If the project is release:independent, make sure
        # that's where the deliverable file is.
        messages.error(
            'uses the independent release model '
            'and should be in the _independent '
            'directory'
        )

    # If the project is declaring some other release model, make
    # sure it is not in the _independent directory.  We have to
    # bypass the model property because that always returns
    # 'independent' for deliverables in that series.
    model_value = deliv.data.get('release-model', 'independent')
    if deliv.series == 'independent' and model_value != 'independent':
        messages.error(
            'deliverables in the _independent directory '
            'should all use the independent release model'
        )

    LOG.debug('release model {}'.format(deliv.model))


def clone_deliverable(deliv, workdir, messages):
    """Clone all of the repositories for the deliverable into the workdir.

    Returns boolean indicating whether all of the clones could be
    performed as expected.

    """
    cloned = set()
    ok = True
    header('Checking out source code')
    for repo in deliv.repos:
        if repo.name in cloned:
            continue
        if repo.is_retired:
            LOG.info('{} is retired, skipping clone'.format(repo.name))
            continue
        if not gitutils.safe_clone_repo(workdir, repo.name,
                                        'master', messages):
            ok = False
    return ok


def _require_gitreview(workdir, repo, messages):
    print('\nlooking for .gitreview in %s' % repo)
    filename = os.path.join(
        workdir, repo, '.gitreview',
    )
    if not os.path.exists(filename):
        messages.error('%s has no .gitreview file' % (repo,))
    else:
        LOG.debug('found {}'.format(filename))


def validate_gitreview(deliv, workdir, messages):
    "All repos must include a .gitreview file for new releases."
    header('Validate .gitreview')
    checked = set()
    for release in deliv.releases:
        for project in release.projects:
            if project.repo.name in checked:
                continue
            checked.add(project.repo.name)
            if project.repo.is_retired:
                LOG.debug('{} is retired, skipping'.format(
                    project.repo.name))
                continue
            version_exists = gitutils.commit_exists(
                workdir, project.repo.name, release.version,
            )
            if not version_exists:
                LOG.debug('checking {} at {} for {}'.format(
                    project.repo.name, project.hash, release.version))
                gitutils.safe_clone_repo(
                    workdir, project.repo.name, project.hash, messages)
                _require_gitreview(workdir, project.repo.name, messages)
            else:
                LOG.debug('version {} exists, skipping'.format(
                    release.version))

_TYPE_TO_RELEASE_TYPE = {
    'library': 'python-pypi',
    'service': 'python-service',
    'horizon-plugin': 'horizon',
}

_PYTHON_RELEASE_TYPES = ['python-service', 'python-pypi', 'neutron', 'horizon']


def get_release_type(deliv, repo, workdir):
    """Return tuple with release type and boolean indicating whether it
    was explicitly set.

    """
    if deliv.release_type is not None:
        return (deliv.release_type, True)

    from_type = _TYPE_TO_RELEASE_TYPE.get(deliv.type)
    if from_type is not None:
        return (from_type, False)

    if deliv.include_pypi_link:
        return ('python-pypi', False)

    if puppetutils.looks_like_a_module(workdir, repo.name):
        return ('puppet', False)

    if npmutils.looks_like_a_module(workdir, repo.name):
        return ('nodejs', False)

    return ('python-service', False)


def validate_release_type(deliv,
                          zuul_projects,
                          workdir,
                          messages):
    """Apply validation rules for the deliverable based on 'release-type'
    to the most recent release of a deliverable.

    """
    header('Validate release-type')

    if deliv.artifact_link_mode == 'none':
        LOG.info('link-mode is "none", skipping release-type checks')
        return

    if not deliv.releases:
        LOG.info('no releases listed, skipping release-type checks')
        return

    release = deliv.releases[-1]
    for project in release.projects:

        LOG.info('checking release-type for {}'.format(project.repo.name))

        release_type, was_explicit = get_release_type(
            deliv, project.repo.name, workdir,
        )
        if was_explicit:
            LOG.info('found explicit release-type {!r}'.format(
                release_type))
        else:
            LOG.info('release-type not given, '
                     'guessing {!r}'.format(release_type))

        version_exists = gitutils.commit_exists(
            workdir, project.repo.name, release.version,
        )

        if not version_exists:
            LOG.info('new version {}, checking release jobs'.format(
                release.version))
            project_config.require_release_jobs_for_repo(
                deliv,
                zuul_projects,
                project.repo,
                release_type,
                messages,
            )


def validate_tarball_base(deliv, workdir, messages):

    if deliv.artifact_link_mode != 'tarball':
        LOG.info('rule does not apply for link-mode {}, skipping'.format(
            deliv.artifact_link_mode))
        return

    if not deliv.is_released:
        LOG.info('no releases, skipping')
        return

    release = deliv.releases[-1]
    for project in release.projects:
        version_exists = gitutils.commit_exists(
            workdir, project.repo.name, release.version,
        )
        # Check that the sdist name and tarball-base name match.
        try:
            sdist = pythonutils.get_sdist_name(workdir,
                                               project.repo.name)
        except Exception as err:
            msg = 'Could not get the name of {} for version {}: {}'.format(
                project.repo.name, release.version, err)
            if version_exists:
                # If there was a problem with an existing
                # release, treat it as a warning so we
                # don't prevent new releases.
                messages.warning(msg)
            else:
                messages.error(msg)
        else:
            if sdist is not None:
                tarball_base = project.tarball_base
                expected = tarball_base or os.path.basename(project.repo.name)
                if sdist != expected:
                    if tarball_base:
                        action = 'is set to'
                    else:
                        action = 'defaults to'
                    messages.error(
                        ('tarball-base for %s %s %s %r '
                         'but the sdist name is actually %r. ' +
                         _PLEASE)
                        % (project.repo.name, release.version,
                           action, expected, sdist))


def validate_pypi_permissions(deliv, zuul_projects, workdir,
                              messages):

    header('Validate PyPI Permissions')

    for repo in deliv.repos:

        job_templates = zuul_projects.get(repo.name, {}).get('templates', [])
        LOG.debug('{} has job templates {}'.format(repo.name, job_templates))

        # Look for jobs that appear to be talking about publishing to
        # PyPI. There are variations.
        pypi_jobs = [
            j
            for j in job_templates
            if 'pypi' in j
        ]

        if not pypi_jobs:
            LOG.info('rule does not apply to repos not publishing to PyPI')
            continue

        LOG.info('{} publishes to PyPI via {}'.format(repo.name, pypi_jobs))

        pypi_name = repo.pypi_name

        if not pypi_name:
            try:
                sdist = pythonutils.get_sdist_name(workdir, repo.name)
            except Exception as err:
                messages.warning(
                    'Could not determine the sdist name '
                    'for {} to check PyPI permissions: {}'.format(
                        repo.name, err)
                )
                continue

            LOG.debug('using sdist name as pypi-name {!r}'.format(sdist))
            pypi_name = sdist

        uploaders = pythonutils.get_pypi_uploaders(pypi_name)
        if not uploaders:
            # Names like "openstack_requirements" are translated to
            # "openstack-requirements" in the PyPI API.
            alt_name = pypi_name.replace('_', '-')
            LOG.debug('retrying with pypi_name name {!r}'.format(alt_name))
            uploaders = pythonutils.get_pypi_uploaders(alt_name)

        if not uploaders:
            messages.error(
                'could not find users with permission to upload packages '
                'for {}. Is the sdist name correct?'.format(pypi_name)
            )
        elif 'openstackci' not in uploaders:
            messages.error(
                'openstackci does not have permission to upload packages '
                'for {}. Current owners include: {}'.format(
                    pypi_name, ', '.join(sorted(uploaders)))
            )
        else:
            LOG.debug('found {} able to upload to {}'.format(
                sorted(uploaders), pypi_name))


def validate_releases(deliv, zuul_projects,
                      series_name,
                      workdir,
                      messages):
    """Apply validation rules to the 'releases' list for the deliverable.
    """
    header('Validate Releases')

    # Remember which entries are new so we can verify that they
    # appear at the end of the file.
    new_releases = {}

    if deliv.model == 'untagged' and deliv.is_released:
        messages.error(
            'untagged deliverables should not have a "releases" section'
        )
        return

    prev_version = None
    prev_projects = set()
    for release in deliv.releases:

        LOG.info('checking {}'.format(release.version))

        for project in release.projects:

            # Check the SHA specified for the tag.
            LOG.info('{} SHA {}'.format(project.repo.name, project.hash))

            if not is_a_hash(project.hash):
                messages.error(
                    ('%(repo)s version %(version)s release from '
                     '%(hash)r, which is not a hash') % {
                         'repo': project.repo.name,
                         'hash': project.hash,
                         'version': release.version}
                )
            else:

                if not gitutils.safe_clone_repo(workdir, project.repo.name,
                                                project.hash, messages):
                    continue

                # Report if the version has already been
                # tagged. We expect it to not exist, but neither
                # case is an error because sometimes we want to
                # import history and sometimes we want to make new
                # releases.
                version_exists = gitutils.commit_exists(
                    workdir, project.repo.name, release.version,
                )
                if version_exists:
                    actual_sha = gitutils.sha_for_tag(
                        workdir,
                        project.repo.name,
                        release.version,
                    )
                    if actual_sha != project.hash:
                        messages.error(
                            ('Version %s in %s is on '
                             'commit %s instead of %s') %
                            (release.version,
                             project.repo.name,
                             actual_sha,
                             project.hash))
                    print('tag exists, skipping further validation')
                    continue

                # Report if the SHA exists or not (an error if it
                # does not).
                sha_exists = gitutils.commit_exists(
                    workdir, project.repo.name, project.hash,
                )
                if not sha_exists:
                    messages.error('No commit %(hash)r in %(repo)r'
                                   % {'hash': project.hash,
                                      'repo': project.repo.name})
                    # No point in running extra checks if the SHA just
                    # doesn't exist.
                    continue

                LOG.info('Found new version {} for {}'.format(
                    release.version, project.repo))
                new_releases[release.version] = release
                if prev_projects and project.repo.name not in prev_projects:
                    LOG.debug('not included in previous release for %s: %s' %
                              (prev_version, ', '.join(sorted(prev_projects))))
                else:

                    release_type, was_explicit = get_release_type(
                        deliv, project.repo, workdir,
                    )
                    if was_explicit:
                        LOG.debug('found explicit release-type {!r}'.format(
                            release_type))
                    else:
                        LOG.debug('release-type not given, '
                                  'guessing {!r}'.format(release_type))

                    # If this is a puppet module, ensure
                    # that the tag and metadata file
                    # match.
                    if release_type == 'puppet':
                        LOG.info('applying puppet version rules')
                        puppet_ver = puppetutils.get_version(
                            workdir, project.repo.name)
                        if puppet_ver != release.version:
                            messages.error(
                                '%s metadata contains "%s" '
                                'but is being tagged "%s"' % (
                                    project.repo.name,
                                    puppet_ver,
                                    release.version,
                                )
                            )

                    # If this is a npm module, ensure
                    # that the tag and metadata file
                    # match.
                    if release_type == 'nodejs':
                        LOG.info('applying nodejs version rules')
                        npm_ver = npmutils.get_version(
                            workdir, project.repo.name)
                        if npm_ver != release.version:
                            messages.error(
                                '%s package.json contains "%s" '
                                'but is being tagged "%s"' % (
                                    project.repo.name,
                                    npm_ver,
                                    release.version,
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
                            report = messages.error
                        else:
                            report = messages.warning
                        requirements.find_bad_lower_bound_increases(
                            workdir, project.repo.name,
                            prev_version, release.version, project.hash,
                            report,
                        )

                    for e in versionutils.validate_version(
                            release.version,
                            release_type=release_type,
                            pre_ok=(deliv.model in _USES_PREVER)):
                        msg = ('could not validate version %r: %s' %
                               (release.version, e))
                        messages.error(msg)

                    if deliv.is_independent:
                        messages.warning('skipping descendant test for '
                                         'independent project, verify '
                                         'branch manually')

                    else:
                        # If this is the first version in the series,
                        # check that the commit is actually on the
                        # targeted branch.
                        if not gitutils.check_branch_sha(workdir,
                                                         project.repo.name,
                                                         series_name,
                                                         project.hash):
                            msg = '%s %s not present in %s branch' % (
                                project.repo.name,
                                project.hash,
                                series_name,
                            )
                            messages.error(msg)

                        if prev_version:
                            # Check to see if we are re-tagging the same
                            # commit with a new version.
                            old_sha = gitutils.sha_for_tag(
                                workdir,
                                project.repo.name,
                                prev_version,
                            )
                            if old_sha == project.hash:
                                # FIXME(dhellmann): This needs a test.
                                LOG.info('Retagging the SHA with '
                                         'a new version')
                            else:
                                # Check to see if the commit for the new
                                # version is in the ancestors of the
                                # previous release, meaning it is actually
                                # merged into the branch.
                                is_ancestor = gitutils.check_ancestry(
                                    workdir,
                                    project.repo.name,
                                    prev_version,
                                    project.hash,
                                )
                                if not is_ancestor:
                                    messages.error(
                                        '%s %s receiving %s '
                                        'is not a descendant of %s' % (
                                            project.repo.name,
                                            project.hash,
                                            release.version,
                                            prev_version,
                                        )
                                    )

        prev_version = release.version
        prev_projects = set(p.repo.name for p in release.projects)

    # Make sure that new entries have been appended to the file.
    for v, nr in new_releases.items():
        print('comparing {!r} to {!r}'.format(nr, deliv.releases[-1]))
        if nr != deliv.releases[-1]:
            msg = ('new release %s must be listed last, '
                   'with one new release per patch' % nr.version)
            messages.error(msg)


def validate_new_releases(deliv, team_data, messages):

    """Apply validation rules that only apply to the current series.
    """
    header('Validate New Releases')

    if not deliv.is_released:
        LOG.info('no releases, skipping')
        return

    final_release = deliv.releases[-1]
    expected_repos = set(
        r.name
        for r in governance.get_repositories(
            team_data,
            deliverable_name=deliv.name,
        )
    )
    link_mode = deliv.artifact_link_mode
    if link_mode != 'none' and not expected_repos:
        messages.error('unable to find deliverable %s in the governance list' %
                       deliv.name)
    actual_repos = set(
        p.repo.name
        for p in final_release.projects
    )
    for extra in actual_repos.difference(expected_repos):
        messages.warning(
            'release %s includes repository %s '
            'that is not in the governance list' %
            (final_release.version, extra)
        )
    for missing in expected_repos.difference(actual_repos):
        messages.warning(
            'release %s is missing %s, '
            'which appears in the governance list: %s' %
            (final_release.version, missing, expected_repos)
        )
    for repo in actual_repos:
        if repo not in deliv.known_repo_names:
            messages.error(
                'release %s includes repository %s '
                'that is not in the repository-settings section' %
                (final_release.version, repo)
            )
    for missing in deliv.known_repo_names:
        if missing not in actual_repos:
            messages.warning(
                'release %s is missing %s, '
                'which appears in the repository-settings list' %
                (final_release.version, missing)
            )


def validate_branch_prefixes(deliverable_info, messages):
    "Ensure all branches have good prefixes."
    header('Validate Branch Prefixes')
    branches = deliverable_info.get('branches', [])
    for branch in branches:
        prefix = branch['name'].split('/')[0]
        if prefix not in _VALID_BRANCH_PREFIXES:
            messages.error('branch name %s does not use a valid prefix: %s' % (
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
                             messages):
    "Apply the rules for stable branches."
    header('Validate Stable Branches')
    if ('launchpad' in deliverable_info and
       deliverable_info['launchpad'] in _NO_STABLE_BRANCH_CHECK):
        print('rule does not apply to this repo, skipping')
        return

    branches = deliverable_info.get('branches', [])

    d_type = _guess_deliverable_type(deliverable_name, deliverable_info)
    if d_type == 'tempest-plugin' and branches:
        messages.error('Tempest plugins do not support branching.')
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
            messages.error(
                ('stable branch name expected to be stable/name '
                 'but got %s') % (branch['name'],))
            continue
        if prefix != 'stable':
            continue
        location = branch.get('location')
        if branch_mode == 'std':
            if not isinstance(location, six.string_types):
                messages.error(
                    ('branch location for %s is '
                     'expected to be a string but got a %s' % (
                         branch['name'], type(location)))
                )
            if location not in known_releases:
                messages.error(
                    ('stable branches must be created from existing '
                     'tagged releases, and %s for %s is not found in the '
                     'list of releases for this deliverable' % (
                         location, branch['name']))
                )
        elif branch_mode == 'tagless':
            if not isinstance(location, dict):
                messages.error(
                    ('branch location for %s is '
                     'expected to be a mapping but got a %s' % (
                         branch['name'], type(location)))
                )
                # The other rules aren't going to be testable, so skip them.
                continue
            for repo, loc in sorted(location.items()):
                if not is_a_hash(loc):
                    messages.error(
                        ('tagless stable branches should be created '
                         'from commits by SHA but location %s for '
                         'branch %s of %s does not look '
                         'like a SHA' % (
                             (loc, repo, branch['name'])))
                    )
                    # We can't clone the location if it isn't a SHA.
                    continue
                if not gitutils.safe_clone_repo(workdir, repo, loc, messages):
                    continue
                if not gitutils.commit_exists(workdir, repo, loc):
                    messages.error(
                        ('stable branches should be created from merged '
                         'commits but location %s for branch %s of %s '
                         'does not exist' % (
                             (loc, repo, branch['name'])))
                    )
        elif branch_mode == 'upstream':
            if not isinstance(location, six.string_types):
                messages.error(
                    ('branch location for %s is '
                     'expected to be a string but got a %s' % (
                         branch['name'], type(location)))
                )
        else:
            messages.error(
                ('unrecognized stable-branch-type %r' % (branch_mode,))
            )
        if branch_mode == 'upstream':
            messages.warning(
                'skipping branch name check for upstream mode'
            )
        elif series_name == '_independent':
            if series not in known_series:
                messages.error(
                    ('stable branches must be named for known series '
                     'but %s was not found in %s' % (
                         branch['name'], known_series))
                )
        else:
            if series != series_name:
                messages.error(
                    ('cycle-based projects must match series names '
                     'for stable branches. %s should be stable/%s' % (
                         branch['name'], series_name))
                )


def validate_feature_branches(deliverable_info,
                              deliverable_name,
                              workdir,
                              messages):
    "Apply the rules for feature branches."
    header('Validate Feature Branches')
    branches = deliverable_info.get('branches', [])

    d_type = _guess_deliverable_type(deliverable_name, deliverable_info)
    if d_type == 'tempest-plugin' and branches:
        messages.error('Tempest plugins do not support branching.')
        return

    for branch in branches:
        try:
            prefix, series = branch['name'].split('/')
        except ValueError:
            messages.error(
                ('feature branch name expected to be feature/name '
                 'but got %s') % (branch['name'],))
            continue
        if prefix != 'feature':
            continue
        location = branch['location']
        if not isinstance(location, dict):
            messages.error(
                ('branch location for %s is '
                 'expected to be a mapping but got a %s' % (
                     branch['name'], type(location)))
            )
            # The other rules aren't going to be testable, so skip them.
            continue
        for repo, loc in sorted(location.items()):
            if not is_a_hash(loc):
                messages.error(
                    ('feature branches should be created from commits by SHA '
                     'but location %s for branch %s of %s does not look '
                     'like a SHA' % (
                         (loc, repo, branch['name'])))
                )
            if not gitutils.commit_exists(workdir, repo, loc):
                messages.error(
                    ('feature branches should be created from merged commits '
                     'but location %s for branch %s of %s does not exist' % (
                         (loc, repo, branch['name'])))
                )


def validate_driverfixes_branches(deliverable_info,
                                  deliverable_name,
                                  workdir,
                                  messages):
    "Apply the rules for driverfixes branches."
    header('Validate driverfixes Branches')
    known_series = sorted(list(
        d for d in os.listdir('deliverables')
        if not d.startswith('_')
    ))
    branches = deliverable_info.get('branches', [])

    d_type = _guess_deliverable_type(deliverable_name, deliverable_info)
    if d_type == 'tempest-plugin' and branches:
        messages.error('Tempest plugins do not support branching.')
        return

    for branch in branches:
        try:
            prefix, series = branch['name'].split('/')
        except ValueError:
            messages.error(
                ('driverfixes branch name expected to be driverfixes/name '
                 'but got %s') % (branch['name'],))
            continue
        if prefix != 'driverfixes':
            continue
        location = branch['location']
        if series not in known_series:
            messages.error(
                ('driverfixes branches must be named for known series '
                 'but %s was not found in %s' % (
                     branch['name'], known_series))
            )
        if not isinstance(location, dict):
            messages.error(
                ('branch location for %s is '
                 'expected to be a mapping but got a %s' % (
                     branch['name'], type(location)))
            )
            # The other rules aren't going to be testable, so skip them.
            continue
        for repo, loc in sorted(location.items()):
            if not is_a_hash(loc):
                messages.error(
                    ('driverfixes branches should be created from commits by '
                     'SHA but location %s for branch %s of %s does not look '
                     'like a SHA' % (
                         (loc, repo, branch['name'])))
                )
            if not gitutils.commit_exists(workdir, repo, loc):
                messages.error(
                    ('driverfixes branches should be created from merged '
                     'commits but location %s for branch %s of %s does not '
                     'exist' % (
                         (loc, repo, branch['name'])))
                )
            _require_gitreview(workdir, repo, messages)


def validate_branch_points(deliverable_info,
                           deliverable_name,
                           workdir,
                           messages):
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
                    messages.error(
                        '{} branch exists in {} and does not seem '
                        'to have been created from {}'.format(
                            branch['name'], repo, hash),
                    )
                else:
                    # The branch does not exist and the proposed point
                    # to create it is not on the expected source
                    # branch, so phrase the error message to reflect
                    # that.
                    messages.error(
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


class MessageCollector(object):

    def __init__(self, debug=False):
        self.warnings = []
        self.errors = []
        self.debug = debug
        self.filename = None

    def set_filename(self, filename):
        self.filename = filename

    def warning(self, msg):
        print('WARNING: {}'.format(msg))
        self.warnings.append('{}: {}'.format(self.filename, msg))

    def error(self, msg):
        print('ERROR: {}'.format(msg))
        self.errors.append('{}: {}'.format(self.filename, msg))
        if self.debug:
            raise RuntimeError(msg)

    def show_summary(self):
        header('Summary')

        print('\n\n%s warnings found' % len(self.warnings))
        for w in self.warnings:
            print(w)

        print('\n\n%s errors found' % len(self.errors))
        for e in self.errors:
            print(e)


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

    workdir = tempfile.mkdtemp(prefix='releases-')
    print('creating temporary files in %s' % workdir)

    def cleanup_workdir():
        if args.cleanup:
            shutil.rmtree(workdir, True)
        else:
            print('not cleaning up %s' % workdir)
    atexit.register(cleanup_workdir)

    messages = MessageCollector(debug=args.debug)

    for filename in filenames:
        print('\nChecking %s' % filename)

        if not os.path.isfile(filename):
            print("File was deleted, skipping.")
            continue

        messages.set_filename(filename)

        deliv = deliverable.Deliverable.read_file(filename)

        if deliv.series in _CLOSED_SERIES:
            continue

        clone_deliverable(deliv, workdir, messages)
        validate_bugtracker(deliv, messages)
        validate_team(deliv, team_data, messages)
        validate_release_notes(deliv, messages)
        validate_model(deliv, deliv.series, messages)
        validate_release_type(
            deliv,
            zuul_projects,
            workdir,
            messages,
        )
        validate_pypi_permissions(
            deliv,
            zuul_projects,
            workdir,
            messages,
        )
        validate_gitreview(deliv, workdir, messages)
        validate_releases(
            deliv,
            zuul_projects,
            deliv.series,
            workdir,
            messages,
        )
        validate_tarball_base(deliv, workdir, messages)
        # Some rules only apply to the most current release.
        if deliv.series == defaults.RELEASE:
            validate_new_releases(
                deliv,
                team_data,
                messages,
            )
            validate_series_open(
                deliv._data,
                deliv.series,
                filename,
                messages,
            )
            deprecate_release_highlights(
                deliv._data,
                messages,
            )
        validate_series_first(
            deliv._data,
            deliv.series,
            messages,
        )
        validate_branch_prefixes(
            deliv._data,
            messages,
        )
        validate_stable_branches(
            deliv._data,
            deliv.name,
            workdir,
            deliv.series,
            messages,
        )
        validate_feature_branches(
            deliv._data,
            deliv.name,
            workdir,
            messages,
        )
        validate_driverfixes_branches(
            deliv._data,
            deliv.name,
            workdir,
            messages,
        )
        validate_branch_points(
            deliv._data,
            deliv.name,
            workdir,
            messages,
        )

    messages.show_summary()

    return 1 if messages.errors else 0
