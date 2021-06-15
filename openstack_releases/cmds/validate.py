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

"""Try to verify that the latest commit contains valid SHA values."""

import argparse
import atexit
import collections
import functools
import glob
import inspect
import logging
import os
import os.path
import re
import shutil
import sys
import tempfile

from openstack_governance import governance
import requests
import six

# Disable warnings about insecure connections.
from requests.packages import urllib3

from openstack_releases import defaults
from openstack_releases import deliverable
from openstack_releases import gitutils
from openstack_releases import npmutils
from openstack_releases import project_config
from openstack_releases import puppetutils
from openstack_releases import pythonutils
from openstack_releases import requirements
from openstack_releases import versionutils
from openstack_releases import xstaticutils

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
    'newton',
    'ocata',
    'pike',
    'queens',
])

_USES_PREVER = set([
    'cycle-with-milestones',
    'cycle-trailing',
    'cycle-with-rc',
])

_VALID_BRANCH_PREFIXES = set([
    'stable',
    'feature',
    'bugfix',
])

_NO_STABLE_BRANCH_CHECK = set([
    'gnocchi',
    'rally',
    'puppet-pacemaker',  # tracks upstream version
    'openstack/tenks',
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


def applies_to_current(f):
    @functools.wraps(f)
    def decorated(deliv, context):
        if deliv.series != defaults.RELEASE:
            print('this rule only applies to the most current series, skipping')
            return
        return f(deliv, context)
    return decorated


def applies_to_released(f):
    @functools.wraps(f)
    def decorated(deliv, context):
        if not deliv.is_released:
            print('no releases, skipping')
            return
        return f(deliv, context)
    return decorated


def applies_to_cycle(f):
    @functools.wraps(f)
    def decorated(deliv, context):
        if deliv.is_independent:
            print('rule does not apply to independent projects')
            return
        return f(deliv, context)
    return decorated


# Remember which tags already exist so we don't have to repeat the
# expensive check.
existing_tag_cache = collections.defaultdict(set)


def includes_new_tag(deliv, context):
    "Return true if the deliverable is describing a new tag."
    for release in deliv.releases:
        for project in release.projects:

            if project.repo.is_retired:
                LOG.info('{} is retired, skipping'.format(project.repo.name))
                continue

            if release.version in existing_tag_cache[project.repo.name]:
                LOG.debug('%s already tagged %s, skipping',
                          project.repo.name, release.version)
                continue

            version_exists = gitutils.commit_exists(
                context.workdir, project.repo.name, release.version,
            )
            if version_exists:
                existing_tag_cache[project.repo.name].add(release.version)
                LOG.debug('%s already tagged %s, skipping',
                          project.repo.name, release.version)
            else:
                return True
    return False


def skip_existing_tags(f):
    @functools.wraps(f)
    def decorated(deliv, context):
        if includes_new_tag(deliv, context):
            return f(deliv, context)
        else:
            print('This rule only applies to new tags.')
    return decorated


def skip_em_eol_tags(f):
    @functools.wraps(f)
    def decorated(deliv, context):
        em_or_eol = False
        for release in deliv.releases:
            if '-em' in release.version or '-eol' in release.version:
                print('Skipping rule for EM or EOL tagging.')
                em_or_eol = True
                break
        if not em_or_eol:
            return f(deliv, context)
    return decorated


@skip_existing_tags
@applies_to_cycle
@applies_to_released
@applies_to_current
def validate_series_open(deliv, context):
    "No releases in the new series until the previous one has a branch."

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


@skip_existing_tags
@applies_to_released
@applies_to_cycle
def validate_series_first(deliv, context):
    "The first release in a series needs to end with '.0'."

    if deliv.type == 'tempest-plugin':
        print('this rule does not apply to branchless tempest plugins')
        return

    releases = deliv.releases
    if len(releases) != 1:
        # We only have to check this when the first release is being
        # applied in the file.
        print('this rule only applies to the first release in a series')
        return

    versionstr = releases[0].version
    patchlevel = versionstr.rpartition('.')[-1]
    # Make sure first release of a series is more than just a bugfix bump so
    # there is room for a stable release in the previous cycle
    if not (patchlevel == '0' or
            patchlevel.startswith('0b') or patchlevel.startswith('0rc')):
        context.error(
            'Initial releases in a series must increment at '
            'least the minor version or be beta versions. %r' % (versionstr,)
        )


@skip_existing_tags
@applies_to_current
@applies_to_released
@applies_to_cycle
def validate_pre_release_progression(deliv, context):
    "Pre-release versions must be applied in progressive order"

    if not deliv.is_milestone_based:
        print('this rule only applies to milestone-based projects')
        return

    releases = deliv.releases

    # Milestone-based deliverables cannot directly do a final release
    if len(releases) == 1:
        if not releases[-1].is_pre_release_version:
            context.error('A RC release must be present before final release '
                          'for deliverables following a milestone-based cycle')
        return

    previous_release = releases[-2]
    current_release = releases[-1]

    LOG.debug(
        'checking progression from {} to {}'.format(
            previous_release.version, current_release.version)
    )

    if 'rc' in current_release.version:
        version_type = 'Release candidate'
        previous_type = 'a beta or release candidate'
        allowed = ['b', 'rc']
    elif 'b' in current_release.version:
        version_type = 'Beta'
        previous_type = 'an alpha or beta'
        allowed = ['a', 'b']
    elif 'a' in current_release.version:
        version_type = 'Alpha'
        previous_type = 'an alpha'
        allowed = ['a']
    else:
        # Final versions must come after release candidates
        # or other final versions.
        version_type = 'Final'
        previous_type = 'a release candidate or final'
        allowed = ['rc', 'final']

    def checks():
        for pre in allowed:
            if pre == 'final':
                yield not previous_release.is_pre_release_version
            else:
                yield pre in previous_release.version

    if not any(checks()):
        context.error(
            ('{} version {} must come after '
             '{} version, not {}').format(
                 version_type,
                 current_release.version,
                 previous_type,
                 previous_release.version)
        )
    else:
        print('OK')


@skip_existing_tags
@applies_to_released
def validate_series_final(deliv, context):
    "The final release after a RC should tag the same commit."

    releases = deliv.releases
    if len(releases) < 2:
        # We only have to check this when the first release is being
        # applied in the file.
        print('this rule only applies to the final release in a series')
        return

    previous_release = releases[-2]
    current_release = releases[-1]

    if (current_release.is_release_candidate or
            not previous_release.is_release_candidate):
        print('this rule only applies when tagging a final from a candidate')
        return

    current_projects = sorted(releases[-1].projects)
    previous_projects = sorted(previous_release.projects)
    for c_proj, p_proj in zip(current_projects, previous_projects):
        LOG.debug(
            'comparing {}:{} with {}:{}'.format(
                c_proj.repo.name, c_proj.hash,
                p_proj.repo.name, p_proj.hash,
            ))
        if c_proj.repo.name != p_proj.repo.name:
            context.error(
                '{} does not match {} so there is some missing info '
                'in this release'.format(c_proj.repo.name, p_proj.repo.name)
            )
        elif c_proj.hash != p_proj.hash:
            context.error(
                '{} for {} is on {} but should be {} '
                'to match version {}'.format(
                    current_release.version, c_proj.repo.name, c_proj.hash,
                    p_proj.hash, previous_release.version)
            )
        else:
            print('OK')


def _require_tag_on_all_repos(deliv, current_release, eol_or_em, context):
    # The tag should be applied to all of the repositories for the
    # deliverable.
    actual_repos = set(p.repo.name for p in current_release.projects)
    expected_repos = set(r.name for r in deliv.repos)
    error = False
    for extra in actual_repos.difference(expected_repos):
        error = True
        context.error(
            '%s release %s includes repository %s '
            'that is not in deliverable' %
            (eol_or_em, current_release.version, extra)
        )
    for missing in expected_repos.difference(actual_repos):
        error = True
        context.error(
            'release %s is missing %s, '
            'which appears in the deliverable' %
            (current_release.version, missing)
        )
    if not error:
        print('OK')


@skip_existing_tags
@applies_to_released
def validate_series_eol(deliv, context):
    """The EOL tag should be applied to all repositories."""

    current_release = deliv.releases[-1]

    if not current_release.is_eol:
        print('this rule only applies when tagging a series as end-of-life')
        return

    if len(deliv.branches) == 0:
        context.error('only branched deliverables can be tagged EOL')

    _require_tag_on_all_repos(
        deliv,
        current_release,
        'EOL',
        context,
    )


@skip_existing_tags
@applies_to_released
def validate_series_em(deliv, context):
    """The EM tag should be applied to the previous release."""

    current_release = deliv.releases[-1]

    if not current_release.is_em:
        print('this rule only applies when tagging '
              'a series as extended-maintenance')
        return

    if len(deliv.releases) == 1:
        context.error('at least one release will have to been done to '
                      'mark as extended-maintenance')
        print('This deliverable may need to be cleaned up if a '
              'release was not actually done for the series.')
        return

    if len(deliv.branches) == 0:
        context.error('only branched deliverables can be tagged EM')

    _require_tag_on_all_repos(
        deliv,
        current_release,
        'extended maintenance',
        context,
    )

    # Make sure we are taking the last release
    previous_release = deliv.releases[-2]
    for project in deliv.known_repo_names:
        current_proj = current_release.project(project)
        previous_proj = previous_release.project(project)

        if current_proj is None or previous_proj is None:
            # Error will be picked up above
            continue

        current_hash = current_proj.hash
        previous_hash = previous_proj.hash
        if current_hash != previous_hash:
            context.error('EM tag must match the last release, tagging '
                          '%s, last release %s' %
                          (current_hash, previous_hash))


@skip_em_eol_tags
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
                # TODO(fungi): This can be changed to simply check
                # that sb_id == project.get('name') later if all the
                # data gets updated from numbers to names.
                if sb_id in (project.get('id'), project.get('name')):
                    break
            else:
                context.error(
                    'Did not find a storyboard project with ID %s' % sb_id
                )
            print('storyboard project ID {} OK'.format(sb_id))
    else:
        context.error('No launchpad or storyboard project given')


@skip_em_eol_tags
def validate_team(deliv, context):
    "Look for the team name in the governance data."
    try:
        context.gov_data.get_team(deliv.team)
    except ValueError:
        context.warning(
            'Team {} not in governance data. '
            'Only official teams should use this repository '
            'for managing releases. See README.rst for details.'.format(
                deliv.team))
    else:
        print('owned by team {}'.format(deliv.team))


@skip_em_eol_tags
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


@skip_em_eol_tags
def validate_model(deliv, context):
    "Require a valid release model"

    LOG.debug('release model {}'.format(deliv.model))

    if not deliv.is_independent and not deliv.model:
        # If the deliverable is not independent it must declare a
        # release model.
        context.error(
            'no release-model specified',
        )

    if (deliv.model in ['independent', 'abandoned'] and
            deliv.series != 'independent'):
        # If the project is release:independent or abandoned, make sure
        # the deliverable file is in _independent.
        context.error(
            'uses the independent or abandoned release model '
            'and should be in the _independent '
            'directory'
        )

    # If the project is declaring some other release model, make
    # sure it is not in the _independent directory.  We have to
    # bypass the model property because that always returns
    # 'independent' for deliverables in that series.
    model_value = deliv.data.get('release-model', 'independent')
    if (deliv.series == 'independent' and
            model_value not in ['independent', 'abandoned']):
        context.error(
            'deliverables in the _independent directory '
            'should use either the independent or abandoned release models'
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


@skip_existing_tags
def validate_gitreview(deliv, context):
    "All repos must include a .gitreview file for new releases."
    checked = set()
    for release in deliv.releases:
        for project in release.projects:
            if project.repo.name in checked or project.repo.is_retired:
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
                gitutils.checkout_ref(
                    context.workdir, project.repo.name, project.hash, context)
                _require_gitreview(project.repo.name, context)
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


@skip_em_eol_tags
@skip_existing_tags
@applies_to_released
def validate_release_type(deliv, context):
    "Does the most recent release comply with the rules for the release-type?"

    if deliv.artifact_link_mode == 'none':
        print('link-mode is "none", skipping release-type checks')
        return

    release = deliv.releases[-1]
    for project in release.projects:

        LOG.debug('checking release-type for {}'.format(project.repo.name))

        release_type, was_explicit = get_release_type(
            deliv, project.repo, context.workdir,
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
            gitutils.checkout_ref(
                context.workdir, project.repo.name, project.hash, context)
            project_config.require_release_jobs_for_repo(
                deliv,
                project.repo,
                release_type,
                context,
            )


@skip_em_eol_tags
@applies_to_released
def validate_tarball_base(deliv, context):
    "Does tarball-base match the expected value?"

    if deliv.artifact_link_mode != 'tarball':
        print('rule does not apply for link-mode {}, skipping'.format(
            deliv.artifact_link_mode))
        return

    release = deliv.releases[-1]
    for project in release.projects:

        if project.repo.is_retired:
            LOG.info('%s is retired, skipping', project.repo.name)
            continue

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


@skip_em_eol_tags
@applies_to_released
def validate_build_sdist(deliv, context):
    "Can we build an sdist for a python project?"

    release = deliv.releases[-1]
    for project in release.projects:
        if project.repo.is_retired:
            LOG.info('%s is retired, skipping', project.repo.name)
            continue

        version_exists = gitutils.commit_exists(
            context.workdir, project.repo.name, release.version,
        )
        if version_exists:
            print('version {} was already tagged, skipping'.format(
                release.version))
            continue

        gitutils.checkout_ref(
            context.workdir, project.repo.name, project.hash, context)

        # Set some git configuration values to allow us to perform
        # local operations like tagging.
        gitutils.ensure_basic_git_config(
            context.workdir, project.repo.name,
            {'user.email': 'openstack-infra@lists.openstack.org',
             'user.name': 'OpenStack Proposal Bot'},
        )

        # Ensure us that build sdist will works with tags. That help to detect
        # branching problems early. The goal is to avoid to try to add a tag
        # to a branch which is older than another tag already on that
        # branch/in that branch's history
        gitutils.add_tag(
            context.workdir, project.repo.name, release.version, project.hash
        )

        try:
            pythonutils.build_sdist(
                context.workdir, project.repo.name)
        except Exception as err:
            context.error(
                'Failed to build sdist for {}: {}'.format(
                    project.repo.name, err))
        finally:
            # Removing the temporary tag to avoid to mislead next tests, else
            # if not deleted the tag will remain active in the repo and it
            # will be see as an existing tag.
            gitutils.delete_tag(
                context.workdir,
                project.repo.name,
                release.version
            )


@skip_em_eol_tags
@skip_existing_tags
@applies_to_released
def validate_pypi_readme(deliv, context):
    "Does the README look right for PyPI?"

    # Check out the repositories to the hash for the latest release on
    # the branch so we can find the setup.py and README.rst there (if
    # it exists), in case that has been removed from master after a
    # project is retired. This also ensures we get the right name for
    # the branch, in case the sdist name changes over time.
    latest_release = deliv.releases[-1]
    for project in latest_release.projects:
        gitutils.checkout_ref(
            context.workdir, project.repo.name, project.hash, context)

    if latest_release.is_eol:
        print('skipping README validation for EOL tag {}'.format(
            latest_release.version))
        return
    if latest_release.is_em:
        print('skipping README validation for EM tag {}'.format(
            latest_release.version))
        return

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
            print('rule only applies to repos publishing to PyPI')
            continue

        LOG.debug('{} publishes to PyPI via {}'.format(repo.name, pypi_jobs))

        try:
            pythonutils.check_readme_format(context.workdir, repo.name)
        except Exception as err:
            context.error('README check for {} failed: {}'.format(
                repo.name, err))
        else:
            print('OK')


@skip_em_eol_tags
@skip_existing_tags
@applies_to_released
def validate_pypi_permissions(deliv, context):
    "Do we have permission to upload to PyPI?"

    # Check out the repositories to the hash for the latest release on
    # the branch so we can find the setup.py there (if it exists), in
    # case that has been removed from master after a project is
    # retired. This also ensures we get the right name for the branch,
    # in case the sdist name changes over time.
    latest_release = deliv.releases[-1]
    for project in latest_release.projects:
        gitutils.checkout_ref(
            context.workdir, project.repo.name, project.hash, context)

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
                return

            LOG.debug('using sdist name as pypi-name {!r}'.format(sdist))
            pypi_name = sdist

        if not pypi_name:
            context.error(
                'Could not determine a valid PyPI dist name for {}'.format(
                    deliv.name))
            return

        uploaders = pythonutils.get_pypi_uploaders(pypi_name)
        if not uploaders:
            pypi_info = pythonutils.get_pypi_info(pypi_name)
            if not pypi_info:
                LOG.debug('no %s project data on pypi, assuming it will be '
                          'created by release',
                          pypi_name)
            else:
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


@skip_existing_tags
@applies_to_released
def validate_deliverable_is_not_abandoned(deliv, context):
    "Ensure the deliverable is not an independent abandoned deliverable."

    if deliv.model == 'abandoned':
        context.error('Abandoned deliverables should not see new releases')


@skip_existing_tags
@applies_to_released
def validate_release_sha_exists(deliv, context):
    "Ensure the hashes for each release exist."

    for release in deliv.releases:

        LOG.debug('checking {}'.format(release.version))

        for project in release.projects:
            if project.repo.is_retired:
                LOG.info('%s is retired, skipping', project.repo.name)
                continue

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

            if not gitutils.checkout_ref(context.workdir, project.repo.name,
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


@applies_to_released
def validate_existing_tags(deliv, context):
    "Ensure tags that exist point to the SHAs listed."

    for release in deliv.releases:

        LOG.debug('checking {}'.format(release.version))

        for project in release.projects:
            if project.repo.is_retired:
                LOG.info('%s is retired, skipping', project.repo.name)
                continue

            LOG.debug('{} SHA {}'.format(project.repo.name, project.hash))

            if not gitutils.checkout_ref(context.workdir, project.repo.name,
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
                    'Version {} in {} is on '
                    'commit {!r} instead of {!r}'.format(
                        release.version,
                        project.repo.name,
                        actual_sha,
                        project.hash)
                )
            else:
                print('{} tag exists and is correct for {}'.format(
                    release.version, project.repo.name))


@skip_existing_tags
@applies_to_released
def validate_version_numbers(deliv, context):
    "Ensure the version numbers are valid."

    # Track the previous version tag attached to each repository, by
    # name.
    prev_version = {}

    for release in deliv.releases:

        LOG.debug('checking {}'.format(release.version))

        if release.is_eol:
            LOG.debug('Found new EOL tag {} for {}'.format(
                release.version, deliv.name))
            if deliv.is_independent:
                context.warning(
                    'EOL tag {} on independent deliverable, branch not validated'.format(
                        release.version))
                continue
            if release.eol_series != deliv.series:
                context.error(
                    'EOL tag {} does not refer to the {} series.'.format(
                        release.version, deliv.series))
            continue

        if release.is_em:
            LOG.debug('Found new EM tag {} for {}'.format(
                release.version, deliv.name))
            if deliv.is_independent:
                context.warning(
                    'EM tag {} on independent deliverable, branch not validated'.format(
                        release.version))
                continue
            if release.em_series != deliv.series:
                context.error(
                    'EM tag {} does not refer to the {} series.'.format(
                        release.version, deliv.series))
            continue

        if release.is_last:
            LOG.debug('Found new LAST tag {} for {}'.format(
                release.version, deliv.name))
            if deliv.is_independent:
                context.warning(
                    'LAST tag {} on independent deliverable, branch not validated'.format(
                        release.version))
                continue
            if release.version != "{}-last".format(deliv.series):
                context.error(
                    "LAST tag {} should match branch name (e.g {}-last)".format(
                        release.version, deliv.series))
            if not deliv.series_info.is_em:
                context.error(
                    "LAST tag {} aren't allowed on a series ({}) that are not EM".format(
                        release.version, deliv.series))
            continue

        for project in release.projects:

            if not gitutils.checkout_ref(context.workdir, project.repo.name,
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

            # If this is an xstatic package, ensure the package version in code
            # matches the tag being requested.
            if release_type == 'xstatic':
                LOG.debug('performing xstatic version checks')
                xs_versions = xstaticutils.get_versions(
                    context.workdir, project.repo.name)
                if not xs_versions:
                    context.error(
                        '%s should contain a PACKAGE_VERSION but none found')
                for xs_version in xs_versions:
                    if xs_version != release.version:
                        context.error(
                            '%s xstatic.pkg has PACKAGE_VERSION "%s" but is '
                            'being tagged as "%s"' % (
                                project.repo.name,
                                xs_version,
                                release.version,
                            )
                        )

            # If we know the previous version and the
            # project is a python deliverable make sure
            # the requirements haven't changed in a way
            # not reflecting the version.
            if (prev_version.get(project.repo.name) and
                    release_type in _PYTHON_RELEASE_TYPES):
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
                    prev_version.get(project.repo.name),
                    release.version, project.hash,
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

        # Update the previous version information without discarding
        # any data about repositories that were not tagged in this
        # release.
        for project in release.projects:
            prev_version[project.repo.name] = release.version


@skip_existing_tags
@applies_to_released
def validate_new_releases_at_end(deliv, context):
    "New releases must be added to the end of the list."

    # Remember which entries are new so we can verify that they
    # appear at the end of the file.
    new_releases = {}

    for release in deliv.releases:

        for project in release.projects:

            if not gitutils.checkout_ref(context.workdir, project.repo.name,
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
    for _, nr in new_releases.items():
        LOG.debug('comparing {!r} to {!r}'.format(nr, deliv.releases[-1]))
        if nr != deliv.releases[-1]:
            msg = ('new release %s must be listed last, '
                   'with one new release per patch' % nr.version)
            context.error(msg)
        else:
            print('OK')


@skip_em_eol_tags
@skip_existing_tags
@applies_to_released
def validate_new_releases_in_open_series(deliv, context):
    "New releases may only be added to open series."

    if deliv.allows_releases:
        print('{} has status {!r} for {} and allows releases'.format(
            deliv.name, deliv.series, deliv.stable_status))
        return

    LOG.debug('%s has status %r for %s and will not allow new releases',
              deliv.name, deliv.stable_status, deliv.series)

    # Remember which entries are new so we can verify that they
    # appear at the end of the file.
    new_releases = {}

    for release in deliv.releases:

        for project in release.projects:

            if not gitutils.checkout_ref(context.workdir, project.repo.name,
                                         project.hash, context):
                continue

            version_exists = gitutils.commit_exists(
                context.workdir, project.repo.name, release.version,
            )
            if version_exists:
                print('tag exists, skipping further validation')
                continue

            if release.is_eol:
                LOG.debug('Found new EOL tag {} for {}'.format(
                    release.version, project.repo))
            elif release.is_em:
                LOG.debug('Found new EM tag {} for {}'.format(
                    release.version, project.repo))
            elif release.is_last:
                LOG.debug('Found new LAST tag {} for {}'.format(
                    release.version, project.repo))
            else:
                LOG.debug('Found new version {} for {}'.format(
                    release.version, project.repo))
                new_releases[release.version] = release

    if new_releases:
        # The series is closed but there is a new release.
        msg = ('deliverable {} has status {!r} for {} '
               'and cannot have new releases tagged').format(
                   deliv.name, deliv.stable_status, deliv.series)
        context.error(msg)
    else:
        print('OK')


@applies_to_released
def validate_release_branch_membership(deliv, context):
    "Commits being tagged need to be on the right branch."

    if deliv.is_independent:
        context.warning('skipping descendant test for '
                        'independent project, verify '
                        'branch manually')
        return

    # Track the previous version tag attached to each repository, by
    # name.
    prev_version = {}

    for release in deliv.releases:

        LOG.debug('checking {}'.format(release.version))

        for project in release.projects:
            if project.repo.is_retired:
                LOG.info('%s is retired, skipping', project.repo.name)
                continue

            if not gitutils.checkout_ref(context.workdir, project.repo.name,
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

            if not prev_version.get(project.repo.name):
                print('no ancestry check for first version in a series')
                continue

            # Check to see if we are re-tagging the same
            # commit with a new version.
            old_sha = gitutils.sha_for_tag(
                context.workdir,
                project.repo.name,
                prev_version[project.repo.name],
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
                    prev_version[project.repo.name],
                    project.hash,
                )
                if not is_ancestor:
                    context.error(
                        '%s %s receiving %s '
                        'is not a descendant of %s' % (
                            project.repo.name,
                            project.hash,
                            release.version,
                            prev_version[project.repo.name],
                        )
                    )
                else:
                    print('ancestry OK')

        # Update the previous version information without discarding
        # any data about repositories that were not tagged in this
        # release.
        for project in release.projects:
            prev_version[project.repo.name] = release.version


@skip_em_eol_tags
@applies_to_current
@applies_to_released
def validate_new_releases(deliv, context):
    "Apply validation rules that only apply to the current series."

    final_release = deliv.releases[-1]
    expected_repos = set(
        r.name
        for r in context.gov_data.get_repositories(
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
            context.error(
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

    if (deliv.launchpad_id in _NO_STABLE_BRANCH_CHECK or
            deliv.storyboard_id in _NO_STABLE_BRANCH_CHECK):
        print('rule does not apply to this repo, skipping')
        return

    if deliv.type == 'tempest-plugin' and deliv.branches:
        context.error('Tempest plugins do not support branching.')
        return

    branch_mode = deliv.stable_branch_type

    if branch_mode == 'none' and deliv.branches:
        context.error('Deliverables with stable-branch-mode:none '
                      'do not support stable branching.')
        return

    if deliv.releases and deliv.releases[-1].is_eol:
        print('rule does not apply to end-of-life repos, skipping')
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
                ('stable branch name expected to be stable/name '
                 'but got %s') % (branch.name,))
            continue
        if prefix != 'stable' and prefix != 'bugfix':
            print('{} is not a stable or bugfix branch, skipping'.format(
                branch.name))
            continue

        location = branch.location

        if branch_mode == 'std' or branch_mode == 'std-with-versions':
            if not isinstance(location, six.string_types):
                context.error(
                    ('branch location for %s is '
                     'expected to be a string but got a %s' % (
                         branch.name, type(location)))
                )

            if not deliv.known_repo_names:
                context.error(
                    ('Unable to validate branch {} for '
                     '{} without repository information').format(
                         branch.name, deliv.name,
                    )
                )
                return
            branch_exists = all(
                gitutils.branch_exists(
                    context.workdir,
                    repo,
                    prefix,
                    series,
                )
                for repo in deliv.known_repo_names if
                not deliv.get_repo(repo).is_retired
            )
            if branch_exists:
                print('{} branch already exists, skipping validation'.format(
                    branch.name))
                continue

            if deliv.is_independent or prefix == 'bugfix':
                print('"latest release" rule does not apply '
                      'to independent repositories or bugfix '
                      'branches, skipping')
            else:
                latest_release = deliv.releases[-1]
                if location != latest_release.version:
                    context.error(
                        ('stable branches must be created from the latest '
                         'tagged release, and %s for %s does not match %s' % (
                             location, branch.name, latest_release.version))
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
                if not gitutils.checkout_ref(context.workdir, repo, loc,
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
                if branch_mode == 'std-with-versions':
                    # Not a normal stable branch, so it must be a versioned
                    # bugfix branch (bugfix/3.1)
                    expected_version = '.'.join(location.split('.')[0:2])
                    if series != expected_version:
                        context.error(
                            'cycle-based projects must match series names '
                            'for stable branches, or branch based on version '
                            'for short term support. %s should be stable/%s '
                            'or bugfix/%s' % (
                                branch.name, deliv.series, expected_version))
                else:
                    context.error(
                        'cycle-based projects must match series names '
                        'for stable branches. %s should be stable/%s' % (
                            branch.name, deliv.series))


def validate_feature_branches(deliv, context):
    "Apply the rules for feature branches."

    if deliv.type == 'tempest-plugin' and deliv.branches:
        context.error('Tempest plugins do not support branching.')
        return

    for branch in deliv.branches:
        try:
            prefix, _ = branch.name.split('/')
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

        if prefix != 'stable':
            print('these rules do not apply to feature branches, skipping')
            continue

        expected = set([
            'master',
            branch.name,
        ])

        location = branch.get_repo_map()

        for repo, hash in sorted(location.items()):
            if deliv.get_repo(repo).is_retired:
                continue
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
    _gov_data = None

    def __init__(self, debug=False, cleanup=True):
        self.warnings = []
        self.errors = []
        self.debug = debug
        self.cleanup = cleanup
        self.filename = None
        self._setup_workdir()
        self.function_name = 'unknown'

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

    def set_function(self, function):
        self.function_name = function.__name__

    def warning(self, msg):
        LOG.warning(msg)
        self.warnings.append('{}: {}: {}'.format(
            self.filename, self.function_name, msg))

    def error(self, msg):
        LOG.error(msg)
        self.errors.append('{}: {}: {}'.format(
            self.filename, self.function_name, msg))
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
    def gov_data(self):
        if not self._gov_data:
            self._gov_data = governance.Governance.from_remote_repo()
        return self._gov_data


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
            validate_build_sdist,
            # Check readme after sdist build to slightly optimize things
            validate_pypi_readme,
            validate_gitreview,
            validate_deliverable_is_not_abandoned,
            validate_release_sha_exists,
            validate_existing_tags,
            validate_version_numbers,
            validate_new_releases_at_end,
            validate_new_releases_in_open_series,
            validate_release_branch_membership,
            validate_tarball_base,
            validate_new_releases,
            validate_series_open,
            validate_series_first,
            validate_series_final,
            validate_pre_release_progression,
            validate_series_eol,
            validate_series_em,
            validate_branch_prefixes,
            validate_stable_branches,
            validate_feature_branches,
            validate_branch_points,
        ]
        for check in checks:
            title = inspect.getdoc(check).splitlines()[0].strip()
            header(title)
            context.set_function(check)
            check(deliv, context)

    context.show_summary()

    return 1 if context.errors else 0
