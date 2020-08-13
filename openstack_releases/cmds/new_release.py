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

import argparse
import atexit
import logging
import os
import shutil
import sys
import tempfile

from openstack_releases.cmds.interactive_release import clean_changes
from openstack_releases.cmds.interactive_release import yes_no_prompt
from openstack_releases import gitutils
from openstack_releases import series_status
from openstack_releases import yamlutils

# Release models that support release candidates.
_USES_RCS = ['cycle-with-milestones', 'cycle-trailing', 'cycle-with-rc']

LOG = logging.getLogger('')


def get_deliverable_data(series, deliverable):
    deliverable_filename = 'deliverables/%s/%s.yaml' % (
        series, deliverable)
    with open(deliverable_filename, 'r', encoding='utf-8') as f:
        return yamlutils.loads(f)


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
        elif 'rc' in old_version[-1]:
            # A deliverable exists so we can handle normally
            next_rc = int(old_version[-1][3:]) + 1
            new_version_parts.append('0rc{}'.format(next_rc))
        else:
            # No milestone or rc exists, fallback to the same logic
            # as for '0b1' and increment the major version.
            new_version_parts = increment_version(old_version, (1, 0, 0))
            new_version_parts.append('0rc1')
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
    """Increment the major release number.

    How much do we need to increment the feature number to provision
    for future stable releases in skipped series, based on last release
    found.
    """
    return max(1, last_release['depth'])


def get_release_history(series, deliverable):
    """Retrieve the history of releases for a given deliverable.

    Returns an array of arrays containing the releases for each series,
    in reverse chronological order starting from specified series.
    """
    if series == '_independent':
        included_series = ['_independent']
    else:
        status = series_status.SeriesStatus.default()
        all_series = list(status.names)
        LOG.debug('all series %s', all_series)
        included_series = all_series[all_series.index(series):]
    release_history = []
    LOG.debug('building release history')
    for current_series in included_series:
        try:
            deliv_info = get_deliverable_data(current_series, deliverable)
            releases = deliv_info['releases'] or []
        except (IOError, OSError, KeyError):
            releases = []
        LOG.debug('%s releases: %s', current_series,
                  [r['version'] for r in releases])
        release_history.append(releases)
    return release_history


def get_last_release(release_history, deliverable, release_type):
    depth = 0
    for releases in release_history:
        LOG.debug('looking for previous version in %s',
                  [r['version'] for r in releases])
        if releases:
            LOG.debug('using %s', releases[-1]['version'])
            return dict({'depth': depth}, **releases[-1])
        elif release_type == 'bugfix':
            raise RuntimeError(
                'The first release for a series must '
                'be at least a feature release to allow '
                'for stable releases from the previous series.')
        depth = depth + 1

    return None


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
    parser.add_argument(
        '-v', '--verbose',
        default=False,
        action='store_true',
        help='be more chatty',
    )
    parser.add_argument(
        '-i', '--interactive',
        default=False,
        action='store_true',
        help='Be interactive and only make releases when instructed'
    )
    parser.add_argument(
        'release_type',
        choices=('bugfix', 'feature', 'major', 'milestone', 'rc',
                 'procedural', 'eol', 'em', 'releasefix'),
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
        '--debug',
        default=False,
        action='store_true',
        help='show tracebacks on errors',
    )
    parser.add_argument(
        '--stable-branch',
        default=False,
        action='store_true',
        help='create a new stable branch from the release',
    )
    parser.add_argument(
        '--intermediate-branch',
        default=False,
        action='store_true',
        help='create a new intermediate branch with the form bugfix/n.n; '
             'this is usually needed only by projects with a '
             'cycle-with-intermediary release model'
    )
    args = parser.parse_args()

    # Set up logging, including making some loggers quiet.
    logging.basicConfig(
        format='%(levelname)7s: %(message)s',
        stream=sys.stdout,
        level=logging.DEBUG if args.verbose else logging.INFO,
    )
    logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)

    is_procedural = args.release_type in 'procedural'
    is_retagging = is_procedural or args.release_type == 'releasefix'
    is_eol = args.release_type == 'eol'
    is_em = args.release_type == 'em'
    force_tag = args.force

    workdir = tempfile.mkdtemp(prefix='releases-')
    LOG.info('creating temporary files in %s', workdir)

    def error(msg):
        if args.debug:
            raise msg
        else:
            parser.error(msg)

    def cleanup_workdir():
        if args.cleanup:
            shutil.rmtree(workdir, True)
        else:
            LOG.warning('not cleaning up %s', workdir)
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
        error(e)

    # Ensure we have a list for releases, even if it is empty.
    if deliverable_info.get('releases') is None:
        deliverable_info['releases'] = []

    try:
        release_history = get_release_history(series, args.deliverable)
        this_series_history = release_history[0]
        last_release = get_last_release(
            release_history,
            args.deliverable,
            args.release_type,
        )
    except RuntimeError as err:
        error(err)
    if last_release:
        last_version = last_release['version'].split('.')
    else:
        last_version = None
    LOG.debug('last_version %r', last_version)
    diff_start = None

    add_stable_branch = args.stable_branch or is_procedural

    add_intermediate_branch = args.intermediate_branch

    # Validate new tag can be applied
    if last_version and 'eol' in last_version[0]:
        raise ValueError('Cannot create new release after EOL tagging.')

    if last_version is None:
        # Deliverables that have never been released before should
        # start at 0.1.0, indicating they are not feature complete or
        # stable but have features.
        LOG.debug('defaulting to 0.1.0 for first release')
        new_version_parts = ['0', '1', '0']

    elif args.release_type in ('milestone', 'rc'):
        force_tag = True
        if deliverable_info['release-model'] not in _USES_RCS:
            raise ValueError('Cannot compute RC for {} project {}'.format(
                deliverable_info['release-model'], args.deliverable))
        new_version_parts = increment_milestone_version(
            last_version, args.release_type)
        LOG.debug('computed new version %s release type %s',
                  new_version_parts, args.release_type)
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
            LOG.warning('last_version %s branch base %s',
                        '.'.join(last_version), '.'.join(last_branch_base))
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

    elif args.release_type == 'releasefix':
        increment = (0, 0, 1)
        new_version_parts = increment_version(last_version, increment)
        last_version_hashes = {
            p['repo']: p['hash']
            for p in last_release['projects']
        }
        # Go back 2 releases so the release announcement includes the
        # actual changes.
        try:
            diff_start_release = this_series_history[-2]
        except IndexError:
            # We do not have 2 releases in this series yet, so go back
            # to the stable branch creation point.
            prev_info = get_last_series_info(series, args.deliverable)
            for b in prev_info['branches']:
                if b['name'].startswith('stable/'):
                    diff_start = b['location']
                    LOG.info('using branch point from previous '
                             'series as diff-start: %r', diff_start)
                    break
        else:
            diff_start = diff_start_release['version']
            LOG.info('using release from same series as diff-start: %r',
                     diff_start)

    elif is_eol or is_em:
        last_version_hashes = {
            p['repo']: p['hash']
            for p in last_release['projects']
        }
        increment = None
        new_version_parts = None
        new_version = '{}-{}'.format(args.series, args.release_type)

    else:
        increment = {
            'bugfix': (0, 0, 1),
            'feature': (0, feature_increment(last_release), 0),
            'major': (1, 0, 0),
        }[args.release_type]
        new_version_parts = increment_version(last_version, increment)
        LOG.debug('computed new version %s', new_version_parts)

    if new_version_parts is not None:
        # The EOL/EM tag version string is computed above and the parts
        # list is set to None to avoid recomputing it here.
        new_version = '.'.join(new_version_parts)

    if 'releases' not in deliverable_info:
        deliverable_info['releases'] = []

    LOG.info('going from %s to %s', last_version, new_version)

    projects = []
    changes = 0
    for repo in deliverable_info['repository-settings'].keys():
        LOG.info('processing %s', repo)

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
                    LOG.info('last tagged as %s at %s',
                             previous_tag, previous_sha)
                    found = True
                    break
            if found:
                break

        if is_retagging or (
                is_em and deliverable_info['release-model'] != 'untagged'):
            # Always use the last tagged hash, which should be coming
            # from the previous series or last release.
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

            # Check out the working repo to the sha
            gitutils.checkout_ref(workdir, repo, sha)

        if is_retagging:
            changes += 1
            LOG.info('re-tagging %s at %s (%s)', repo, sha, previous_tag)
            if is_procedural:
                comment = 'procedural tag to support creating stable branch'
            else:
                comment = 'procedural tag to handle release job failure'
            new_project = {
                'repo': repo,
                'hash': sha,
                'comment': comment,
            }
            projects.append(new_project)

        elif is_eol or is_em:
            changes += 1
            LOG.info('tagging %s %s at %s',
                     repo,
                     args.release_type.upper(),
                     sha)
            new_project = {
                'repo': repo,
                'hash': sha,
            }
            projects.append(new_project)

        elif previous_sha != sha or force_tag:
            # TODO(tonyb): Do this early and also prompt for release type.
            # Once we do that we can probably deprecate interactive-release
            if args.interactive:
                # NOTE(tonyb): This is pretty much just copied from
                # interactive-release
                last_tag = '.'.join(last_version)
                change_lines = list(clean_changes(gitutils.changes_since(
                    workdir, repo, last_tag).splitlines()))
                max_changes_show = 100
                LOG.info('')
                if last_tag:
                    LOG.info("%s changes to %s since %s are:",
                             len(change_lines), repo, last_tag)
                else:
                    LOG.info("%s changes to %s are:", len(change_lines), repo)
                for sha, descr in change_lines[0:max_changes_show]:
                    LOG.info("* %s %s", sha[:7], descr)
                leftover_change_lines = change_lines[max_changes_show:]
                if leftover_change_lines:
                    LOG.info("   and %s more changes...",
                             len(leftover_change_lines))
                LOG.info('')

            changes += 1
            LOG.info('advancing %s from %s (%s) to %s',
                     repo, previous_sha, previous_tag, sha)
            new_project = {
                'repo': repo,
                'hash': sha,
            }
            projects.append(new_project)

        else:
            LOG.info('%s already tagged at most recent commit, skipping', repo)

    new_release_info = {
        'version': new_version,
        'projects': projects,
    }
    if diff_start:
        new_release_info['diff-start'] = diff_start
    deliverable_info['releases'].append(new_release_info)

    if add_stable_branch:
        branch_name = 'stable/{}'.format(series)

        # First check if this branch is already defined
        if 'branches' in deliverable_info:
            for branch in deliverable_info['branches']:
                if branch.get('name') == branch_name:
                    LOG.debug('Branch %s already exists, skipping',
                              branch_name)
                    add_stable_branch = False
                    break

        if add_stable_branch:
            LOG.info('adding stable branch at %s', new_version)
            deliverable_info.setdefault('branches', []).append({
                'name': branch_name,
                'location': new_version,
            })

    if add_intermediate_branch:
        new_branch = new_version.rsplit('.', 1)[0]
        branch_name = 'bugfix/{}'.format(new_branch)

        # First check if this branch is already defined
        if 'branches' in deliverable_info:
            for branch in deliverable_info['branches']:
                if branch.get('name') == branch_name:
                    LOG.debug('Branch %s already exists, skipping',
                              branch_name)
                    add_intermediate_branch = False
                    break

        if add_intermediate_branch:
            LOG.info('adding intermediate branch at %s', new_version)
            deliverable_info.setdefault('branches', []).append({
                'name': branch_name,
                'location': new_version,
            })

    create_release = changes > 0
    if create_release and args.interactive:
        create_release = yes_no_prompt(
            'Create a release in %s containing those changes? ' % series)

    if create_release:
        deliverable_filename = 'deliverables/%s/%s.yaml' % (
            series, args.deliverable)
        with open(deliverable_filename, 'w', encoding='utf-8') as f:
            f.write(yamlutils.dumps(deliverable_info))
