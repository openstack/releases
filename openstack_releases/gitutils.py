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

import logging
import os
import os.path
import subprocess

from openstack_releases import links
from openstack_releases import processutils

# Disable warnings about insecure connections.
from requests.packages import urllib3
urllib3.disable_warnings()

LOG = logging.getLogger(__name__)

GIT_TAG_TEMPLATE = 'https://opendev.org/%s/src/tag/%s'


def find_modified_deliverable_files():
    "Return a list of files modified by the most recent commit."
    results = processutils.check_output(
        ['git', 'diff', '--name-only', '--pretty=format:', 'HEAD^']
    ).decode('utf-8')
    filenames = [
        line.strip()
        for line in results.splitlines()
        if (line.startswith('deliverables/'))
    ]
    return filenames


def changes_since(workdir, repo, ref):
    """Get all changes between the last ref and the current point.

    :param workdir: The git repo working directory.
    :param repo: The name of the repo.
    :param ref: The starting ref.
    :returns: Merged commits between the two points.
    """
    try:
        changes = processutils.check_output(
            ['git', 'log', '--decorate', '--no-merges', '--pretty=oneline',
             "%s..HEAD" % ref],
            cwd=os.path.join(workdir, repo),
        ).decode('utf-8').strip()
    except processutils.CalledProcessError as err:
        LOG.error('Could not find {}: {}'.format(ref, err))
        changes = ''
    return changes


def commit_exists(workdir, repo, ref):
    """Return boolean specifying whether the reference exists in the repository.

    The commit must have been merged into the repository, but this
    check does not enforce any branch membership.
    """
    try:
        processutils.check_output(
            ['git', 'show', ref],
            cwd=os.path.join(workdir, repo),
        ).decode('utf-8')
    except processutils.CalledProcessError as err:
        LOG.error('Could not find {}: {}'.format(ref, err))
        return False
    return True


def tag_exists(repo, ref):
    """Return boolean specifying whether the reference exists in the repository.

    Uses a cgit query instead of looking locally to avoid cloning a
    repository or having Depends-On settings in a commit message allow
    someone to fool the check.
    """
    url = GIT_TAG_TEMPLATE % (repo, ref)
    return links.link_exists(url)


def ensure_basic_git_config(workdir, repo, settings):
    """Make sure git config is set.

    Given a repo directory and a settings dict, set local config values
    if those settings are not already defined.
    """
    dest = os.path.join(workdir, repo)
    for key, value in settings.items():
        LOG.info('looking for git config {}'.format(key))
        try:
            existing = processutils.check_output(
                ['git', 'config', '--get', key],
                cwd=dest,
            ).decode('utf-8').strip()
            LOG.info('using existing setting of {}: {!r}'.format(key, existing))
        except processutils.CalledProcessError:
            LOG.info('updating setting of {} to {!r}'.format(key, value))
            processutils.check_call(
                ['git', 'config', key, value],
                cwd=dest,
            )


def clone_repo(workdir, repo, ref=None, branch=None):
    "Check out the code."
    LOG.debug('Checking out repository {} to {}'.format(
        repo, branch or ref or 'master'))
    cmd = [
        './tools/clone_repo.sh',
        '--workspace', workdir,
    ]
    if ref:
        cmd.extend(['--ref', ref])
    if branch:
        cmd.extend(['--branch', branch])
    cmd.append(repo)
    processutils.check_call(cmd)
    dest = os.path.join(workdir, repo)
    return dest


def safe_clone_repo(workdir, repo, ref, messages):
    """Clone a git repo and report success or failure.

    Ensure we have a local copy of the repository so we can scan for values
    that are more difficult to get remotely.
    """
    try:
        clone_repo(workdir, repo, ref)
    except Exception as err:
        messages.error(
            'Could not clone repository %s at %s: %s' % (
                repo, ref, err))
        return False
    return True


def checkout_ref(workdir, repo, ref, messages=None):
    """Checkout a specific ref in the repo."""

    LOG.debug('Resetting the repository %s to HEAD', repo)
    # Reset the repo to HEAD just in case any ot the previous steps
    # updated a checked in file.  If this fails we continue to try the
    # requested ref as that shoudl give us a more complete error log.
    try:
        processutils.check_call(
            ['git', 'reset', '--hard'],
            cwd=os.path.join(workdir, repo))
    except processutils.CalledProcessError as err:
        if messages:
            messages.warning(
                'Could not reset repository {} to HEAD: {}'.format(
                    repo, err))

    LOG.debug('Checking out repository %s to %s', repo, ref)
    try:
        processutils.check_call(
            ['git', 'checkout', ref],
            cwd=os.path.join(workdir, repo))
    except processutils.CalledProcessError as err:
        if messages:
            messages.error(
                'Could not checkout repository {} at {}: {}'.format(
                    repo, ref, err))
        return False
    return True


def sha_for_tag(workdir, repo, version):
    """Return the SHA for a given tag"""
    # git log 2.3.11 -n 1 --pretty=format:%H
    try:
        actual_sha = processutils.check_output(
            ['git', 'log', str(version), '-n', '1', '--pretty=format:%H'],
            cwd=os.path.join(workdir, repo),
            stderr=subprocess.STDOUT,
        ).decode('utf-8')
        actual_sha = actual_sha.strip()
    except processutils.CalledProcessError as e:
        LOG.info('ERROR getting SHA for tag %r: %s [%s]',
                 version, e, e.output.strip())
        actual_sha = ''
    return actual_sha


def _filter_branches(output):
    "Strip garbage from branch list output"
    return [
        n
        for n in output.strip().split()
        if '/' in n or n == 'master'
    ]


def branch_exists(workdir, repo, prefix, identifier):
    """Does the prefix/identifier branch exist.

    Checks if a named branch already exists.
    :param workdir: The working directory for the local clone.
    :param repo: The name of the repo.
    :param prefix: The branch prefix (e.g. "stable" or "bugfix").
    :param idenifier: The branch identifier (series name or version).
    """
    remote_match = 'remotes/origin/{}/{}'.format(prefix, identifier)
    try:
        containing_branches = _filter_branches(
            processutils.check_output(
                ['git', 'branch', '-a'],
                cwd=os.path.join(workdir, repo),
            ).decode('utf-8')
        )
        LOG.debug('looking for %s', remote_match)
        LOG.debug('found branches: %s', containing_branches)
        return (remote_match in containing_branches)
    except processutils.CalledProcessError as e:
        LOG.error('failed checking for branch: %s [%s]', e, e.output.strip())
        return False


def stable_branch_exists(workdir, repo, series):
    "Does the stable/series branch exist?"
    return branch_exists(workdir, repo, 'stable', series)


def check_branch_sha(workdir, repo, series, sha):
    """Check if the SHA is in the targeted branch.

    The SHA must appear on a stable/$series branch (if it exists) or
    master (if stable/$series does not exist). It is up to the
    reviewer to verify that releases from master are in a sensible
    location relative to other existing branches.

    We do not compare $series against the existing branches ordering
    because that would prevent us from retroactively creating a stable
    branch for a project after a later stable branch is created (i.e.,
    if stable/N exists we could not create stable/N-1).

    """
    remote_match = 'remotes/origin/stable/%s' % series
    try:
        containing_branches = _filter_branches(
            processutils.check_output(
                ['git', 'branch', '-a', '--contains', sha],
                cwd=os.path.join(workdir, repo),
            ).decode('utf-8')
        )
        # If the patch is on the named branch, everything is fine.
        if remote_match in containing_branches:
            LOG.debug('found %s branch', remote_match)
            return True
        LOG.debug('did not find %s in branches containing %s: %s',
                  remote_match, sha, containing_branches)
        # If the expected branch does not exist yet, this may be a
        # late release attempt to create that branch or just a project
        # that hasn't branched, yet, and is releasing from master for
        # that series. Allow the release, as long as it is on the
        # master branch.
        all_branches = _filter_branches(
            processutils.check_output(
                ['git', 'branch', '-a'],
                cwd=os.path.join(workdir, repo),
            ).decode('utf-8')
        )
        if remote_match not in all_branches:
            if 'master' in containing_branches:
                LOG.debug('did not find %s but SHA is on master',
                          remote_match)
                return True
            if 'origin/master' in containing_branches:
                LOG.debug('did not find %s but SHA is on origin/master',
                          remote_match)
                return True
        # At this point we know the release is not from the required
        # branch and it is not from master, which means it is the
        # wrong branch and should not be allowed.
        LOG.debug('did not find SHA on %s or master or origin/master',
                  remote_match)
        return False
    except processutils.CalledProcessError as e:
        LOG.error('failed checking SHA on branch: %s [%s]' % (e, e.output.strip()))
        return False


def check_ancestry(workdir, repo, old_version, sha):
    "Check if the SHA is in the ancestry of the previous version."
    try:
        ancestors = processutils.check_output(
            ['git', 'log', '--oneline', '--ancestry-path',
             '%s..%s' % (old_version, sha)],
            cwd=os.path.join(workdir, repo),
        ).decode('utf-8').strip()
        return bool(ancestors)
    except processutils.CalledProcessError as e:
        LOG.error('failed checking ancestry: %s [%s]' % (e, e.output.strip()))
        return False


def get_head(workdir, repo):
    cmd = ['git', 'log', '-n', '1', '--pretty=tformat:%h']
    try:
        return processutils.check_output(
            cmd,
            cwd=os.path.join(workdir, repo),
            stderr=subprocess.STDOUT,
        ).decode('utf-8').strip()
    except processutils.CalledProcessError as e:
        LOG.warning('failed to retrieve HEAD: %s [%s]',
                    e, e.output.strip())
        return None


def get_latest_tag(workdir, repo, sha=None, always=True):
    cmd = ['git', 'describe', '--abbrev=0']
    if always:
        cmd.append('--always')
    if sha is not None:
        cmd.append(sha)
    LOG.debug(' '.join(cmd))
    try:
        return processutils.check_output(
            cmd,
            cwd=os.path.join(workdir, repo),
            stderr=subprocess.STDOUT,
        ).decode('utf-8').strip()
    except processutils.CalledProcessError as e:
        LOG.warning('failed to retrieve latest tag: %s [%s]',
                    e, e.output.strip())
        return None


def add_tag(workdir, repo, tag, sha):
    cmd = ['git', 'tag', '-m', 'temporary tag', tag, sha]
    try:
        LOG.info(' '.join(cmd))
        return processutils.check_output(
            cmd,
            cwd=os.path.join(workdir, repo),
            stderr=subprocess.STDOUT,
        ).decode('utf-8').strip()
    except processutils.CalledProcessError as e:
        LOG.warning('failed to add tag: %s [%s]',
                    e, e.output.strip())
        return None


def get_branches(workdir, repo):
    try:
        output = processutils.check_output(
            ['git', 'branch', '-a'],
            cwd=os.path.join(workdir, repo),
            stderr=subprocess.STDOUT,
        ).decode('utf-8').strip()
        # Example output:
        # * (no branch)
        #   master
        #   stable/mitaka
        #   stable/newton
        #   stable/ocata
        #   remotes/origin/HEAD -> origin/master
        #   remotes/origin/master
        #   remotes/origin/stable/mitaka
        #   remotes/origin/stable/newton
        #   remotes/origin/stable/ocata
        results = []
        for line in output.splitlines():
            branch = line.strip().lstrip('*').strip()
            if branch.startswith('('):
                continue
            if '->' in branch:
                continue
            results.append(branch)
        return results
    except processutils.CalledProcessError as e:
        LOG.error('failed to retrieve list of branches: %s [%s]',
                  e, e.output.strip())
        return []


def branches_containing(workdir, repo, ref):
    try:
        output = processutils.check_output(
            ['git', 'branch', '-r', '--contains', ref],
            cwd=os.path.join(workdir, repo),
            stderr=subprocess.STDOUT,
        ).decode('utf-8').strip()
        # Example output:
        #   origin/stable/ocata
        results = []
        for line in output.splitlines():
            results.append(line.strip())
        return results
    except processutils.CalledProcessError as e:
        LOG.error('failed to retrieve list of branches containing %s: %s [%s]',
                  ref, e, e.output.strip())
        return []


def get_branch_base(workdir, repo, branch):
    "Return SHA at base of branch."
    # http://stackoverflow.com/questions/1527234/finding-a-branch-point-with-git
    # git rev-list $(git rev-list --first-parent ^origin/stable/newton master | tail -n1)^^!
    #
    # Determine the first parent.
    cmd = [
        'git',
        'rev-list',
        '--first-parent',
        '^origin/{}'.format(branch),
        'master',
    ]
    try:
        parents = processutils.check_output(
            cmd,
            cwd=os.path.join(workdir, repo),
            stderr=subprocess.STDOUT,
        ).decode('utf-8').strip()
    except processutils.CalledProcessError as e:
        LOG.warning('failed to retrieve branch base: %s [%s]',
                    e, e.output.strip())
        return None
    parent = parents.splitlines()[-1]
    # Now get the ^^! commit
    cmd = [
        'git',
        'rev-list',
        '{}^^!'.format(parent),
    ]
    try:
        return processutils.check_output(
            cmd,
            cwd=os.path.join(workdir, repo),
            stderr=subprocess.STDOUT,
        ).decode('utf-8').strip()
    except processutils.CalledProcessError as e:
        LOG.warning('failed to retrieve branch base: %s [%s]',
                    e, e.output.strip())
        return None
