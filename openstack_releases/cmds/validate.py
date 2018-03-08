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
import inspect
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

_TYPE_TO_RELEASE_TYPE = {
    'library': 'python-pypi',
    'service': 'python-service',
    'horizon-plugin': 'horizon',
}

_PYTHON_RELEASE_TYPES = ['python-service', 'python-pypi', 'neutron', 'horizon']

_PLEASE = ('It is too expensive to determine this value during '
           'the site build, please set it explicitly.')


def header(title, underline='-'):
    print('\n%s' % title)
    print(underline * len(title))


def is_a_hash(val):
    "Return bool indicating if val looks like a valid hash."
    return re.search('^[a-f0-9]{40}$', val, re.I) is not None


def validate_series_open(deliv, context):
    "No releases in the new series until the previous one has a branch."

    if deliv.series != defaults.RELEASE:
        print('this rule only applies to the most current series, skipping')
        return

    if not deliv.is_released:
        print('no releases, skipping')
        return

    if deliv.is_independent:
        print('rule does not apply to independent projects')
        return

    deliverables_dir = os.path.dirname(
        os.path.dirname(context.filename)
    )
    deliverable_base = os.path.basename(context.filename)
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
    idx = all_deliverable_files.index(context.filename)
    if idx == 0:
        # This is the first cycle-based deliverable file.
        print('this is the first cycle-based version of this deliverable, '
              'skipping further checks')
        return

    previous_deliverable_file = all_deliverable_files[idx - 1]
    previous_series = os.path.basename(
        os.path.dirname(previous_deliverable_file)
    )
    expected_branch = 'stable/' + previous_series
    previous_deliverable = deliverable.Deliverable.read_file(
        previous_deliverable_file
    )
    for branch in previous_deliverable.branches:
        if branch.name == expected_branch:
            # Everything is OK
            print('found branch {} in {}'.format(
                branch.name,
                previous_deliverable_file,
            ))
            return
    context.warning(
        'There is no {} branch defined in {}. Is the {} series open?'.format(
            expected_branch, previous_deliverable_file, deliv.series))


def validate_series_first(deliv, context):
    "The first release in a series needs to end with '.0'."

    if deliv.is_independent:
        print('rule does not apply to independent projects')
        return

    releases = deliv.releases
    if len(releases) != 1:
        # We only have to check this when the first release is being
        # applied in the file.
        print('this rule only applies to the first release in a series')
        return

    versionstr = releases[0].version
    patchlevel = versionstr.rpartition('.')[-1]
    if not (patchlevel == '0' or patchlevel.startswith('0b')):
        context.error(
            'Initial releases in a series must increment at '
            'least the minor version or be beta versions. %r' % (versionstr,)
        )


def validate_bugtracker(deliv, context):
    "Does the bug tracker info link to something that exists?"
    lp_name = deliv.launchpad_id
    sb_id = deliv.storyboard_id
    if lp_name:
        try:
            lp_resp = requests.get('https://api.launchpad.net/1.0/' + lp_name)
        except requests.exceptions.ConnectionError as e:
            # The flakey Launchpad API failed. Don't punish the user for that.
            context.warning('Could not verify launchpad project %s (%s)' %
                            (lp_name, e))
        else:
            if (lp_resp.status_code // 100) == 4:
                context.error('Launchpad project %s does not exist' % lp_name)
        print('launchpad project ID {} OK'.format(lp_name))
    elif sb_id:
        try:
            projects_resp = requests.get(
                'https://storyboard.openstack.org/api/v1/projects'
            )
        except requests.exceptions.ConnectionError as e:
            # The flakey Launchpad API failed. Don't punish the user for that.
            context.warning('Could not verify storyboard project %s (%s)' %
                            (sb_id, e))
        else:
            if (projects_resp.status_code // 100) == 4:
                context.warning(
                    'Could not verify storyboard project, API call failed.'
                )
            for project in projects_resp.json():
                if sb_id == project.get('id'):
                    break
            else:
                context.error(
                    'Did not find a storyboard project with ID %s' % sb_id
                )
            print('storyboard project ID {} OK'.format(sb_id))
    else:
        context.error('No launchpad or storyboard project given')


def validate_team(deliv, context):
    "Look for the team name in the governance data."
    if deliv.team not in context.team_data:
        context.warning('Team %r not in governance data' %
                        deliv.team)
    else:
        print('owned by team {}'.format(deliv.team))


def validate_release_notes(deliv, context):
    "Make sure the release notes page exists, if it is specified."
    notes_link = deliv.release_notes

    if not notes_link:
        print('no release-notes given, skipping')
        return

    if isinstance(notes_link, dict):
        # Dictionary mapping repositories to links. We don't want any
        # repositories that are not known, so check that as well as
        # the actual links.
        for repo_name in sorted(notes_link.keys()):
            if repo_name not in deliv.known_repo_names:
                context.error(
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
            context.error('Could not fetch release notes page %s: %s' %
                          (link, rn_resp.status_code))
        else:
            print('{} OK'.format(link))


def validate_model(deliv, context):
    "Require a valid release model"

    LOG.debug('release model {}'.format(deliv.model))

    if not deliv.is_independent and not deliv.model:
        # If the deliverable is not independent it must declare a
        # release model.
        context.error(
            'no release-model specified',
        )

    if deliv.model == 'independent' and deliv.series != 'independent':
        # If the project is release:independent, make sure
        # that's where the deliverable file is.
        context.error(
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
        context.error(
            'deliverables in the _independent directory '
            'should all use the independent release model'
        )

    if deliv.model == 'untagged' and deliv.is_released:
        context.error(
            'untagged deliverables should not have a "releases" section'
        )
        return


def clone_deliverable(deliv, context):
    """Clone all of the repositories for the deliverable into the workdir.

    Returns boolean indicating whether all of the clones could be
    performed as expected.

    """
    cloned = set()
    ok = True
    for repo in deliv.repos:
        if repo.name in cloned:
            continue
        if repo.is_retired:
            LOG.info('{} is retired, skipping clone'.format(repo.name))
            continue
        if not gitutils.safe_clone_repo(context.workdir, repo.name,
                                        'master', context):
            ok = False
    return ok


def _require_gitreview(repo, context):
    LOG.debug('looking for .gitreview in %s' % repo)
    filename = os.path.join(
        context.workdir, repo, '.gitreview',
    )
    if not os.path.exists(filename):
        context.error('%s has no .gitreview file' % (repo,))
    else:
        print('found {}'.format(filename))


def validate_gitreview(deliv, context):
    "All repos must include a .gitreview file for new releases."
    checked = set()
    for release in deliv.releases:
        for project in release.projects:
            if project.repo.name in checked:
                continue
            checked.add(project.repo.name)
            if project.repo.is_retired:
                print('{} is retired, skipping'.format(
                    project.repo.name))
                continue
            version_exists = gitutils.commit_exists(
                context.workdir, project.repo.name, release.version,
            )
            if not version_exists:
                LOG.debug('checking {} at {} for {}'.format(
                    project.repo.name, project.hash, release.version))
                gitutils.safe_clone_repo(
                    context.workdir, project.repo.name, project.hash, context)
                _require_gitreview(context.workdir, project.repo.name, context)
            else:
                print('version {} exists, skipping'.format(
                    release.version))


def get_release_type(deliv, repo, workdir):
    "Return tuple with release type and whether it was explicitly set."
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


def validate_release_type(deliv, context):
    "Does the most recent release comply with the rules for the release-type?"

    if deliv.artifact_link_mode == 'none':
        print('link-mode is "none", skipping release-type checks')
        return

    if not deliv.releases:
        print('no releases listed, skipping release-type checks')
        return

    release = deliv.releases[-1]
    for project in release.projects:

        LOG.debug('checking release-type for {}'.format(project.repo.name))

        release_type, was_explicit = get_release_type(
            deliv, project.repo.name, context.workdir,
        )
        if was_explicit:
            LOG.debug('found explicit release-type {!r}'.format(
                release_type))
        else:
            LOG.debug('release-type not given, '
                      'guessing {!r}'.format(release_type))

        version_exists = gitutils.commit_exists(
            context.workdir, project.repo.name, release.version,
        )

        if not version_exists:
            LOG.debug('new version {}, checking release jobs'.format(
                release.version))
            project_config.require_release_jobs_for_repo(
                deliv,
                context.zuul_projects,
                project.repo,
                release_type,
                context,
            )


def validate_tarball_base(deliv, context):
    "Does tarball-base match the expected value?"

    if deliv.artifact_link_mode != 'tarball':
        print('rule does not apply for link-mode {}, skipping'.format(
            deliv.artifact_link_mode))
        return

    if not deliv.is_released:
        print('no releases, skipping')
        return

    release = deliv.releases[-1]
    for project in release.projects:
        version_exists = gitutils.commit_exists(
            context.workdir, project.repo.name, release.version,
        )
        # Check that the sdist name and tarball-base name match.
        try:
            sdist = pythonutils.get_sdist_name(context.workdir,
                                               project.repo.name)
        except Exception as err:
            msg = 'Could not get the name of {} for version {}: {}'.format(
                project.repo.name, release.version, err)
            if version_exists:
                # If there was a problem with an existing
                # release, treat it as a warning so we
                # don't prevent new releases.
                context.warning(msg)
            else:
                context.error(msg)
        else:
            if sdist is not None:
                tarball_base = project.tarball_base
                expected = tarball_base or os.path.basename(project.repo.name)
                if sdist != expected:
                    if tarball_base:
                        action = 'is set to'
                    else:
                        action = 'defaults to'
                    context.error(
                        ('tarball-base for %s %s %s %r '
                         'but the sdist name is actually %r. ' +
                         _PLEASE)
                        % (project.repo.name, release.version,
                           action, expected, sdist))
                else:
                    print('{!r} matches expected {!r}'.format(
                        sdist, expected))


def validate_pypi_permissions(deliv, context):
    "Do we have permission to upload to PyPI?"

    for repo in deliv.repos:

        job_templates = context.zuul_projects.get(repo.name, {}).get(
            'templates', [])
        LOG.debug('{} has job templates {}'.format(repo.name, job_templates))

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

        LOG.debug('{} publishes to PyPI via {}'.format(repo.name, pypi_jobs))

        pypi_name = repo.pypi_name

        if not pypi_name:
            try:
                sdist = pythonutils.get_sdist_name(context.workdir, repo.name)
            except Exception as err:
                context.warning(
                    'Could not determine the sdist name '
                    'for {} to check PyPI permissions: {}'.format(
                        repo.name, err)
                )
                continue

            LOG.debug('using sdist name as pypi-name {!r}'.format(sdist))
            pypi_name = sdist

        uploaders = pythonutils.get_pypi_uploaders(pypi_name)
        if not uploaders:
            context.error(
                'could not find users with permission to upload packages '
                'for {}. Is the sdist name correct?'.format(pypi_name)
            )
        elif 'openstackci' not in uploaders:
            context.error(
                'openstackci does not have permission to upload packages '
                'for {}. Current owners include: {}'.format(
                    pypi_name, ', '.join(sorted(uploaders)))
            )
        else:
            print('found {} able to upload to {}'.format(
                sorted(uploaders), pypi_name))


def validate_release_sha_exists(deliv, context):
    "Ensure the hashes for each release exist."

    for release in deliv.releases:

        LOG.debug('checking {}'.format(release.version))

        for project in release.projects:

            # Check the SHA specified for the tag.
            LOG.debug('{} SHA {}'.format(project.repo.name, project.hash))

            if not is_a_hash(project.hash):
                context.error(
                    ('%(repo)s version %(version)s release from '
                     '%(hash)r, which is not a hash') % {
                         'repo': project.repo.name,
                         'hash': project.hash,
                         'version': release.version}
                )
                continue

            if not gitutils.safe_clone_repo(context.workdir, project.repo.name,
                                            project.hash, context):
                continue

            print('successfully cloned {}'.format(project.hash))

            # Report if the SHA exists or not (an error if it
            # does not).
            sha_exists = gitutils.commit_exists(
                context.workdir, project.repo.name, project.hash,
            )
            if not sha_exists:
                context.error('No commit %(hash)r in %(repo)r'
                              % {'hash': project.hash,
                                 'repo': project.repo.name})


def validate_existing_tags(deliv, context):
    "Ensure tags that exist point to the SHAs listed."

    for release in deliv.releases:

        LOG.debug('checking {}'.format(release.version))

        for project in release.projects:

            LOG.debug('{} SHA {}'.format(project.repo.name, project.hash))

            if not gitutils.safe_clone_repo(context.workdir, project.repo.name,
                                            project.hash, context):
                continue

            # Report if the version has already been
            # tagged. We expect it to not exist, but neither
            # case is an error because sometimes we want to
            # import history and sometimes we want to make new
            # releases.
            version_exists = gitutils.commit_exists(
                context.workdir, project.repo.name, release.version,
            )
            if not version_exists:
                print('{} does not have {} tag yet, skipping'.format(
                    project.repo.name, release.version))
                continue

            actual_sha = gitutils.sha_for_tag(
                context.workdir,
                project.repo.name,
                release.version,
            )
            if actual_sha != project.hash:
                context.error(
                    ('Version %s in %s is on '
                     'commit %s instead of %s') %
                    (release.version,
                     project.repo.name,
                     actual_sha,
                     project.hash))
            else:
                print('{} tag exists and is correct for {}'.format(
                    release.version, project.repo.name))


def validate_version_numbers(deliv, context):
    "Ensure the version numbers are valid."

    prev_version = None
    for release in deliv.releases:

        LOG.debug('checking {}'.format(release.version))

        for project in release.projects:

            if not gitutils.safe_clone_repo(context.workdir, project.repo.name,
                                            project.hash, context):
                continue

            version_exists = gitutils.commit_exists(
                context.workdir, project.repo.name, release.version,
            )
            if version_exists:
                print('tag exists, skipping further validation')
                continue

            LOG.debug('Found new version {} for {}'.format(
                release.version, project.repo))

            release_type, was_explicit = get_release_type(
                deliv, project.repo, context.workdir,
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
                LOG.debug('applying puppet version rules')
                puppet_ver = puppetutils.get_version(
                    context.workdir, project.repo.name)
                if puppet_ver != release.version:
                    context.error(
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
                LOG.debug('applying nodejs version rules')
                npm_ver = npmutils.get_version(
                    context.workdir, project.repo.name)
                if npm_ver != release.version:
                    context.error(
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
                if deliv.series == defaults.RELEASE:
                    report = context.error
                else:
                    report = context.warning
                requirements.find_bad_lower_bound_increases(
                    context.workdir, project.repo.name,
                    prev_version, release.version, project.hash,
                    report,
                )

            had_error = False
            for e in versionutils.validate_version(
                    release.version,
                    release_type=release_type,
                    pre_ok=(deliv.model in _USES_PREVER)):
                msg = ('could not validate version %r: %s' %
                       (release.version, e))
                context.error(msg)
                had_error = True

            if not had_error:
                print('{} for {} OK'.format(
                    release.version, project.repo.name))

        prev_version = release.version


def validate_new_releases_at_end(deliv, context):
    "New releases must be added to the end of the list."

    # Remember which entries are new so we can verify that they
    # appear at the end of the file.
    new_releases = {}

    for release in deliv.releases:

        for project in release.projects:

            if not gitutils.safe_clone_repo(context.workdir, project.repo.name,
                                            project.hash, context):
                continue

            version_exists = gitutils.commit_exists(
                context.workdir, project.repo.name, release.version,
            )
            if version_exists:
                print('tag exists, skipping further validation')
                continue

            LOG.debug('Found new version {} for {}'.format(
                release.version, project.repo))
            new_releases[release.version] = release

    # Make sure that new entries have been appended to the file.
    for v, nr in new_releases.items():
        LOG.debug('comparing {!r} to {!r}'.format(nr, deliv.releases[-1]))
        if nr != deliv.releases[-1]:
            msg = ('new release %s must be listed last, '
                   'with one new release per patch' % nr.version)
            context.error(msg)
        else:
            print('OK')


def validate_release_branch_membership(deliv, context):
    "Commits being tagged need to be on the right branch."

    if deliv.is_independent:
        context.warning('skipping descendant test for '
                        'independent project, verify '
                        'branch manually')
        return

    prev_version = None

    for release in deliv.releases:

        LOG.debug('checking {}'.format(release.version))

        for project in release.projects:

            if not gitutils.safe_clone_repo(context.workdir, project.repo.name,
                                            project.hash, context):
                continue

            version_exists = gitutils.commit_exists(
                context.workdir, project.repo.name, release.version,
            )
            if version_exists:
                print('tag exists, skipping further validation')
                continue

            LOG.debug('Found new version {} for {}'.format(
                release.version, project.repo))

            # If this is the first version in the series,
            # check that the commit is actually on the
            # targeted branch.
            if not gitutils.check_branch_sha(context.workdir,
                                             project.repo.name,
                                             deliv.series,
                                             project.hash):
                msg = '%s %s not present in %s branch' % (
                    project.repo.name,
                    project.hash,
                    deliv.series,
                )
                context.error(msg)

            if not prev_version:
                print('no ancestry check for first version in a series')
                continue

            # Check to see if we are re-tagging the same
            # commit with a new version.
            old_sha = gitutils.sha_for_tag(
                context.workdir,
                project.repo.name,
                prev_version,
            )
            if old_sha == project.hash:
                # FIXME(dhellmann): This needs a test.
                LOG.debug('The SHA is being retagged with a new version')
            else:
                # Check to see if the commit for the new
                # version is in the ancestors of the
                # previous release, meaning it is actually
                # merged into the branch.
                is_ancestor = gitutils.check_ancestry(
                    context.workdir,
                    project.repo.name,
                    prev_version,
                    project.hash,
                )
                if not is_ancestor:
                    context.error(
                        '%s %s receiving %s '
                        'is not a descendant of %s' % (
                            project.repo.name,
                            project.hash,
                            release.version,
                            prev_version,
                        )
                    )
                else:
                    print('ancestry OK')

        prev_version = release.version


def validate_new_releases(deliv, context):
    "Apply validation rules that only apply to the current series."

    if deliv.series != defaults.RELEASE:
        print('this rule only applies to the most current series, skipping')
        return

    if not deliv.is_released:
        print('no releases, skipping')
        return

    final_release = deliv.releases[-1]
    expected_repos = set(
        r.name
        for r in governance.get_repositories(
            context.team_data,
            deliverable_name=deliv.name,
        )
    )
    link_mode = deliv.artifact_link_mode
    if link_mode != 'none' and not expected_repos:
        context.error('unable to find deliverable %s in the governance list' %
                      deliv.name)
    actual_repos = set(
        p.repo.name
        for p in final_release.projects
    )
    for extra in actual_repos.difference(expected_repos):
        context.warning(
            'release %s includes repository %s '
            'that is not in the governance list' %
            (final_release.version, extra)
        )
    for missing in expected_repos.difference(actual_repos):
        context.warning(
            'release %s is missing %s, '
            'which appears in the governance list: %s' %
            (final_release.version, missing, expected_repos)
        )
    for repo in actual_repos:
        if repo not in deliv.known_repo_names:
            context.error(
                'release %s includes repository %s '
                'that is not in the repository-settings section' %
                (final_release.version, repo)
            )
    for missing in deliv.known_repo_names:
        if missing not in actual_repos:
            context.warning(
                'release %s is missing %s, '
                'which appears in the repository-settings list' %
                (final_release.version, missing)
            )


def validate_branch_prefixes(deliv, context):
    "Ensure all branch names have good prefixes."
    for branch in deliv.branches:
        if branch.prefix not in _VALID_BRANCH_PREFIXES:
            context.error('branch name %s does not use a valid prefix: %s' % (
                branch.name, _VALID_BRANCH_PREFIXES))


def validate_stable_branches(deliv, context):
    "Apply the rules for stable branches."

    if deliv.launchpad_id in _NO_STABLE_BRANCH_CHECK:
        print('rule does not apply to this repo, skipping')
        return

    if deliv.type == 'tempest-plugin' and deliv.branches:
        context.error('Tempest plugins do not support branching.')
        return

    branch_mode = deliv.stable_branch_type

    known_releases = {
        r.version: r
        for r in deliv.releases
    }
    known_series = sorted(list(
        d for d in os.listdir('deliverables')
        if not d.startswith('_')
    ))
    for branch in deliv.branches:
        try:
            prefix, series = branch.name.split('/')
        except ValueError:
            context.error(
                ('stable branch name expected to be stable/name '
                 'but got %s') % (branch.name,))
            continue
        if prefix != 'stable':
            print('{} is not a stable branch, skipping'.format(
                branch.name))
            continue

        location = branch.location

        if branch_mode == 'std':
            if not isinstance(location, six.string_types):
                context.error(
                    ('branch location for %s is '
                     'expected to be a string but got a %s' % (
                         branch.name, type(location)))
                )
            if location not in known_releases:
                context.error(
                    ('stable branches must be created from existing '
                     'tagged releases, and %s for %s is not found in the '
                     'list of releases for this deliverable' % (
                         location, branch.name))
                )

        elif branch_mode == 'tagless':
            if not isinstance(location, dict):
                context.error(
                    ('branch location for %s is '
                     'expected to be a mapping but got a %s' % (
                         branch.name, type(location)))
                )
                # The other rules aren't going to be testable, so skip them.
                continue
            for repo, loc in sorted(location.items()):
                if not is_a_hash(loc):
                    context.error(
                        ('tagless stable branches should be created '
                         'from commits by SHA but location %s for '
                         'branch %s of %s does not look '
                         'like a SHA' % (
                             (loc, repo, branch.name)))
                    )
                    # We can't clone the location if it isn't a SHA.
                    continue
                if not gitutils.safe_clone_repo(context.workdir, repo, loc,
                                                context):
                    continue
                if not gitutils.commit_exists(context.workdir, repo, loc):
                    context.error(
                        ('stable branches should be created from merged '
                         'commits but location %s for branch %s of %s '
                         'does not exist' % (
                             (loc, repo, branch.name)))
                    )

        elif branch_mode == 'upstream':
            if not isinstance(location, six.string_types):
                context.error(
                    ('branch location for %s is '
                     'expected to be a string but got a %s' % (
                         branch.name, type(location)))
                )

        else:
            context.error(
                ('unrecognized stable-branch-type %r' % (branch_mode,))
            )

        if branch_mode == 'upstream':
            context.warning(
                'skipping branch name check for upstream mode'
            )

        elif deliv.is_independent:
            if series not in known_series:
                context.error(
                    ('stable branches must be named for known series '
                     'but %s was not found in %s' % (
                         branch.name, known_series))
                )

        else:
            if series != deliv.series:
                context.error(
                    ('cycle-based projects must match series names '
                     'for stable branches. %s should be stable/%s' % (
                         branch.name, deliv.series))
                )


def validate_feature_branches(deliv, context):
    "Apply the rules for feature branches."

    if deliv.type == 'tempest-plugin' and deliv.branches:
        context.error('Tempest plugins do not support branching.')
        return

    for branch in deliv.branches:
        try:
            prefix, series = branch.name.split('/')
        except ValueError:
            context.error(
                ('feature branch name expected to be feature/name '
                 'but got %s') % (branch.name,))
            continue
        if prefix != 'feature':
            print('{} is not a feature branch, skipping'.format(
                branch.name))
            continue

        location = branch.location

        if not isinstance(location, dict):
            context.error(
                ('branch location for %s is '
                 'expected to be a mapping but got a %s' % (
                     branch.name, type(location)))
            )
            # The other rules aren't going to be testable, so skip them.
            continue

        for repo, loc in sorted(location.items()):
            if not is_a_hash(loc):
                context.error(
                    ('feature branches should be created from commits by SHA '
                     'but location %s for branch %s of %s does not look '
                     'like a SHA' % (
                         (loc, repo, branch.name)))
                )
            if not gitutils.commit_exists(context.workdir, repo, loc):
                context.error(
                    ('feature branches should be created from merged commits '
                     'but location %s for branch %s of %s does not exist' % (
                         (loc, repo, branch.name)))
                )


def validate_driverfixes_branches(deliv, context):
    "Apply the rules for driverfixes branches."

    if deliv.type == 'tempest-plugin' and deliv.branches:
        context.error('Tempest plugins do not support branching.')
        return

    known_series = sorted(list(
        d for d in os.listdir('deliverables')
        if not d.startswith('_')
    ))

    for branch in deliv.branches:
        try:
            prefix, series = branch.name.split('/')
        except ValueError:
            context.error(
                ('driverfixes branch name expected to be driverfixes/name '
                 'but got %s') % (branch.name,))
            continue

        if prefix != 'driverfixes':
            print('{} is not a driverfixes branch, skipping'.format(
                branch.name))
            continue

        if series not in known_series:
            context.error(
                ('driverfixes branches must be named for known series '
                 'but %s was not found in %s' % (
                     branch.name, known_series))
            )

        location = branch.location
        if not isinstance(location, dict):
            context.error(
                ('branch location for %s is '
                 'expected to be a mapping but got a %s' % (
                     branch.name, type(location)))
            )
            # The other rules aren't going to be testable, so skip them.
            continue

        for repo, loc in sorted(location.items()):
            if not is_a_hash(loc):
                context.error(
                    ('driverfixes branches should be created from commits by '
                     'SHA but location %s for branch %s of %s does not look '
                     'like a SHA' % (
                         (loc, repo, branch.name)))
                )
            if not gitutils.commit_exists(context.workdir, repo, loc):
                context.error(
                    ('driverfixes branches should be created from merged '
                     'commits but location %s for branch %s of %s does not '
                     'exist' % (
                         (loc, repo, branch.name)))
                )
            _require_gitreview(repo, context)


def validate_branch_points(deliv, context):
    "Make sure the branch points given are on the expected branches."

    # Check for 'upstream' branches. These track upstream release names and
    # do not align with OpenStack series names.
    if deliv.stable_branch_type == 'upstream':
        print('this project follows upstream branching conventions, skipping')
        return

    for branch in deliv.branches:
        LOG.debug('checking branch {!r}'.format(branch.name))
        try:
            prefix, series = branch.name.split('/')
        except ValueError:
            print('could not parse the branch name, skipping')
            continue

        if prefix == 'feature':
            print('these rules do not apply to feature branches, skipping')
            continue

        elif prefix == 'stable':
            expected = set([
                'master',
                branch.name,
            ])

        else:
            # driverfixes
            expected = set([
                branch.name,
                'stable/' + series,
            ])

        location = branch.get_repo_map()

        for repo, hash in sorted(location.items()):
            LOG.debug('checking repo {}'.format(repo))
            existing_branches = sorted([
                (b.partition('/origin/')[-1]
                 if b.startswith('remotes/origin/')
                 else b)
                for b in gitutils.get_branches(context.workdir, repo)
            ])

            # Remove the remote name prefix if it is present in the
            # branch name.
            containing = set(
                c.partition('/')[-1] if c.startswith('origin/') else c
                for c in gitutils.branches_containing(
                    context.workdir, repo, hash)
            )

            LOG.debug('found {} on branches {} in {}'.format(
                hash, containing, repo))

            for missing in expected.difference(containing):
                if missing not in existing_branches:
                    print('branch {} does not exist in {}, '
                          'skipping'.format(branch.name, repo))
                    continue

                if branch.name in existing_branches:
                    # The branch already exists but there is something
                    # wrong with the specification. This probably
                    # means someone tried to update the branch setting
                    # after creating the branch, so phrase the error
                    # message to reflect that.
                    context.error(
                        '{} branch exists in {} and does not seem '
                        'to have been created from {}'.format(
                            branch.name, repo, hash),
                    )
                else:
                    # The branch does not exist and the proposed point
                    # to create it is not on the expected source
                    # branch, so phrase the error message to reflect
                    # that.
                    context.error(
                        'commit {} is not on the {} branch '
                        'but it is listed as the branch point for '
                        '{} to be created'.format(
                            hash, missing, branch.name))


# if the branch already exists, the name is by definition valid
# if the branch exists, the data in the map must match reality
#
# FIXME(dhellmann): these two rules become more challenging to
# implement when we think about EOLed branches. I'm going to punt on
# that for now, and if it turns into an issue we can think about how
# to handle validation while still allowing branches to be deleted.


class ValidationContext(object):

    _zuul_projects = None
    _team_data = None

    def __init__(self, debug=False, cleanup=True):
        self.warnings = []
        self.errors = []
        self.debug = debug
        self.cleanup = cleanup
        self.filename = None
        self._setup_workdir()

    def _setup_workdir(self):
        workdir = tempfile.mkdtemp(prefix='releases-')
        LOG.debug('creating temporary files in {}'.format(workdir))

        def cleanup_workdir():
            if self.cleanup:
                shutil.rmtree(workdir, True)
            else:
                print('not cleaning up %s' % workdir)
        atexit.register(cleanup_workdir)

        self.workdir = workdir

    def set_filename(self, filename):
        self.filename = filename

    def warning(self, msg):
        LOG.warning(msg)
        self.warnings.append('{}: {}'.format(self.filename, msg))

    def error(self, msg):
        LOG.error(msg)
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

    @property
    def zuul_projects(self):
        if not self._zuul_projects:
            self._zuul_projects = project_config.get_zuul_project_data()
        return self._zuul_projects

    @property
    def team_data(self):
        if not self._team_data:
            self._team_data = governance.get_team_data()
        return self._team_data


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
        LOG.warning('no modified deliverable files and no arguments, '
                    'skipping validation')
        return 0

    context = ValidationContext(
        debug=args.debug,
        cleanup=args.cleanup,
    )

    for filename in filenames:
        header('Checking %s' % filename, '=')

        if not os.path.isfile(filename):
            print("File was deleted, skipping.")
            continue

        context.set_filename(filename)

        deliv = deliverable.Deliverable.read_file(filename)

        if deliv.series in _CLOSED_SERIES:
            print('File is part of a closed series, skipping')
            continue

        checks = [
            clone_deliverable,
            validate_bugtracker,
            validate_team,
            validate_release_notes,
            validate_model,
            validate_release_type,
            validate_pypi_permissions,
            validate_gitreview,
            validate_release_sha_exists,
            validate_existing_tags,
            validate_version_numbers,
            validate_new_releases_at_end,
            validate_release_branch_membership,
            validate_tarball_base,
            validate_new_releases,
            validate_series_open,
            validate_series_first,
            validate_branch_prefixes,
            validate_stable_branches,
            validate_feature_branches,
            validate_driverfixes_branches,
            validate_branch_points,
        ]
        for check in checks:
            title = inspect.getdoc(check).splitlines()[0].strip()
            header(title)
            check(deliv, context)

    context.show_summary()

    return 1 if context.errors else 0
