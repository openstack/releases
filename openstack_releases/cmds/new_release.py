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

from __future__ import print_function

import argparse
import atexit
import os
import shutil
import tempfile

from openstack_releases import gitutils
from openstack_releases import yamlutils

# Release models that support release candidates.
_USES_RCS = ['cycle-with-milestones', 'cycle-trailing']


def get_deliverable_data(series, deliverable):
    deliverable_filename = 'deliverables/%s/%s.yaml' % (
        series, deliverable)
    with open(deliverable_filename, 'r', encoding='utf-8') as f:
        return yamlutils.loads(f.read())


def increment_version(old_version, increment):
    """Compute the new version based on the previous value.

    :param old_version: Parts of the version string for the last
                        release.
    :type old_version: list(str)
    :param increment: Which positions to increment.
    :type increment: tuple(int)

    """
    new_version_parts = []
    clear = False
    for cur, inc in zip(old_version, increment):
        if clear:
            new_version_parts.append('0')
        else:
            new_version_parts.append(str(int(cur) + inc))
            if inc:
                clear = True
    return new_version_parts


def increment_milestone_version(old_version, release_type):
    """Increment a version using the rules for milestone projects.

    :param old_version: Parts of the version string for the last
                        release.
    :type old_version: list(str)
    :param release_type: Either ``'milestone'`` or ``'rc'``.
    :type release_type: str

    """
    if release_type == 'milestone':
        if 'b' in old_version[-1]:
            # Not the first milestone
            new_version_parts = old_version[:-1]
            next_milestone = int(old_version[-1][2:]) + 1
            new_version_parts.append('0b{}'.format(next_milestone))
        else:
            new_version_parts = increment_version(old_version, (1, 0, 0))
            new_version_parts.append('0b1')
    elif release_type == 'rc':
        new_version_parts = old_version[:-1]
        if 'b' in old_version[-1]:
            # First RC
            new_version_parts.append('0rc1')
        else:
            next_rc = int(old_version[-1][3:]) + 1
            new_version_parts.append('0rc{}'.format(next_rc))
    else:
        raise ValueError('Unknown release type {!r}'.format(release_type))
    return new_version_parts


def get_last_series_info(series, deliverable):
    all_series = sorted(os.listdir('deliverables'))
    prev_series = all_series[all_series.index(series) - 1]
    try:
        return get_deliverable_data(prev_series, deliverable)
    except (IOError, OSError, KeyError) as e:
        raise RuntimeError(
            'Could not determine previous version: %s' % (e,))


def feature_increment(last_release):
    """How much do we need to increment the feature number to provision
    for future stable releases in skipped series, based on last release
    found.
    """
    return max(1, last_release['depth'])


def get_release_history(series, deliverable):
    """Retrieve the history of releases for a given deliverable.
    Returns an array of arrays containing the releases for each series,
    in reverse chronological order starting from specified series.
    """
    all_series = sorted(os.listdir('deliverables'), reverse=True)
    release_history = []
    for current_series in all_series[all_series.index(series):-1]:
        try:
            deliv_info = get_deliverable_data(current_series, deliverable)
            releases = deliv_info['releases']
        except (IOError, OSError, KeyError):
            print('No releases for %s in %s, yet.' % (
                deliverable, series))
            releases = []
        release_history.append(releases)
    return release_history


def get_last_release(release_history, deliverable, release_type):
    depth = 0
    for releases in release_history:
        if releases:
            return dict({'depth': depth}, **releases[-1])
        elif release_type == 'bugfix':
            raise RuntimeError(
                'The first release for a series must '
                'be at least a feature release to allow '
                'for stable releases from the previous series.')
        depth = depth + 1

    raise RuntimeError('No previous version could be found')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'series',
        help='the name of the release series to scan',
    )
    parser.add_argument(
        'deliverable',
        help='the base name of the deliverable file',
    )
    # FIXME(dhellmann): Add milestone and rc types.
    parser.add_argument(
        'release_type',
        choices=('bugfix', 'feature', 'major', 'milestone', 'rc',
                 'procedural', 'eol'),
        help='the type of release to generate',
    )
    parser.add_argument(
        '--no-cleanup',
        dest='cleanup',
        default=True,
        action='store_false',
        help='do not remove temporary files',
    )
    parser.add_argument(
        '--force',
        default=False,
        action='store_true',
        help=('force a new tag, even if the HEAD of the '
              'branch is already tagged'),
    )
    parser.add_argument(
        '--stable-branch',
        default=False,
        action='store_true',
        help='create a new stable branch from the release',
    )
    args = parser.parse_args()

    is_procedural = args.release_type == 'procedural'
    is_eol = args.release_type == 'eol'
    force_tag = args.force

    workdir = tempfile.mkdtemp(prefix='releases-')
    print('creating temporary files in %s' % workdir)

    def cleanup_workdir():
        if args.cleanup:
            shutil.rmtree(workdir, True)
        else:
            print('not cleaning up %s' % workdir)
    atexit.register(cleanup_workdir)

    # Allow for independent projects.
    series = args.series
    if series.lstrip('_') == 'independent':
        series = '_independent'

    # Load existing deliverable data.
    try:
        deliverable_info = get_deliverable_data(
            series, args.deliverable)
    except (IOError, OSError) as e:
        parser.error(e)

    try:
        release_history = get_release_history(series, args.deliverable)
        last_release = get_last_release(
            release_history,
            args.deliverable,
            args.release_type,
        )
    except RuntimeError as err:
        parser.error(err)
    last_version = last_release['version'].split('.')

    add_stable_branch = args.stable_branch or is_procedural
    if args.release_type in ('milestone', 'rc'):
        force_tag = True
        if deliverable_info['release-model'] not in _USES_RCS:
            raise ValueError('Cannot compute RC for {} project {}'.format(
                deliverable_info['release-model'], args.deliverable))
        new_version_parts = increment_milestone_version(
            last_version, args.release_type)
        # We are going to take some special steps for the first
        # release candidate, so figure out if that is what this
        # release will be.
        if args.release_type == 'rc' and new_version_parts[-1][3:] == '1':
            add_stable_branch = True

    elif args.release_type == 'procedural':
        # NOTE(dhellmann): We always compute the new version based on
        # the highest version on the branch, rather than the branch
        # base. If the differences are only patch levels the results
        # do not change, but if there was a minor version update then
        # the new version needs to be incremented based on that.
        new_version_parts = increment_version(last_version, (
            0, feature_increment(last_release), 0)
        )

        # NOTE(dhellmann): Save the SHAs for the commits where the
        # branch was created in each repo, even though that is
        # unlikely to be the same as the last_version, because commits
        # further down the stable branch will not be in the history of
        # the master branch and so we can't tag them as part of the
        # new series *AND* we always want stable branches created from
        # master.
        prev_info = get_last_series_info(series, args.deliverable)
        for b in prev_info['branches']:
            if b['name'].startswith('stable/'):
                last_branch_base = b['location'].split('.')
                break
        else:
            raise ValueError(
                'Could not find a version in branch before {}'.format(
                    series)
            )
        if last_version != last_branch_base:
            print('WARNING: last_version {} branch base {}'.format(
                '.'.join(last_version), '.'.join(last_branch_base)))
        for r in prev_info['releases']:
            if r['version'] == '.'.join(last_branch_base):
                last_version_hashes = {
                    p['repo']: p['hash']
                    for p in r['projects']
                }
                break
        else:
            raise ValueError(
                ('Could not find SHAs for tag '
                 '{} in old deliverable file').format(
                    '.'.join(last_version))
            )

    elif is_eol:
        increment = None
        new_version_parts = None
        new_version = '{}-eol'.format(args.series)

    else:
        increment = {
            'bugfix': (0, 0, 1),
            'feature': (0, feature_increment(last_release), 0),
            'major': (1, 0, 0),
        }[args.release_type]
        new_version_parts = increment_version(last_version, increment)

    if new_version_parts is not None:
        # The EOL tag version string is computed above and the parts
        # list is set to None to avoid recomputing it here.
        new_version = '.'.join(new_version_parts)

    if 'releases' not in deliverable_info:
        deliverable_info['releases'] = []

    print('going from %s to %s' % (last_version, new_version))

    projects = []
    changes = 0
    for repo in deliverable_info['repository-settings'].keys():
        print('processing {}'.format(repo))

        # Look for the most recent time the repo was tagged and use
        # that info as the old sha.
        previous_sha = None
        previous_tag = None
        found = False
        for release in reversed(deliverable_info['releases']):
            for project in release['projects']:
                if project['repo'] == repo:
                    previous_sha = project.get('hash')
                    previous_tag = release['version']
                    print('last tagged as {} at {}'.format(
                        previous_tag, previous_sha))
                    found = True
                    break
            if found:
                break

        repo_info = deliverable_info['repository-settings'][repo]
        tarball_base = repo_info.get('tarball-base')

        if args.release_type == 'procedural':
            # Always use the last tagged hash, which should be coming
            # from the previous series.
            sha = last_version_hashes[repo]

        else:
            # Figure out the hash for the HEAD of the branch.
            gitutils.clone_repo(workdir, repo)

            branches = gitutils.get_branches(workdir, repo)
            version = 'origin/stable/%s' % series
            if not any(branch for branch in branches
                       if branch.endswith(version)):
                version = 'master'

            sha = gitutils.sha_for_tag(workdir, repo, version)

        if is_procedural:
            changes += 1
            print('re-tagging %s at %s (%s)' % (repo, sha,
                                                previous_tag))
            new_project = {
                'repo': repo,
                'hash': sha,
                'comment': 'procedural tag to support creating stable branch',
            }
            if tarball_base:
                new_project['tarball-base'] = tarball_base
            projects.append(new_project)

        if is_eol:
            changes += 1
            print('tagging %s EOL at %s' % (repo, sha))
            new_project = {
                'repo': repo,
                'hash': sha,
            }
            if tarball_base:
                new_project['tarball-base'] = tarball_base
            projects.append(new_project)

        elif previous_sha != sha or force_tag:
            changes += 1
            print('advancing %s from %s (%s) to %s' % (repo,
                                                       previous_sha,
                                                       previous_tag,
                                                       sha))
            new_project = {
                'repo': repo,
                'hash': sha,
            }
            if tarball_base:
                new_project['tarball-base'] = tarball_base
            projects.append(new_project)

        else:
            print('{} already tagged at most recent commit, skipping'.format(
                repo))

    deliverable_info['releases'].append({
        'version': new_version,
        'projects': projects,
    })

    if add_stable_branch:
        branch_name = 'stable/{}'.format(series)

        # First check if this branch is already defined
        if 'branches' in deliverable_info:
            for branch in deliverable_info['branches']:
                if branch.get('name') == branch_name:
                    print('Branch {} already existes, skipping'.format(
                        branch_name))
                    add_stable_branch = False
                    break

        if add_stable_branch:
            print('adding stable branch at {}'.format(new_version))
            deliverable_info.setdefault('branches', []).append({
                'name': branch_name,
                'location': new_version,
            })

    if changes > 0:
        deliverable_filename = 'deliverables/%s/%s.yaml' % (
            series, args.deliverable)
        with open(deliverable_filename, 'w', encoding='utf-8') as f:
            f.write(yamlutils.dumps(deliverable_info))
