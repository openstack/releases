#!/usr/bin/python3
#
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
import os.path
import shutil
import subprocess
import sys
import tempfile

import openstack_releases
from openstack_releases import deliverable


def _get_current_version(reporoot, branch=None):
    """Return the current version of the repository.

    If the repo appears to contain a python project, use setup.py to
    get the version so pbr (if used) can do its thing. Otherwise, use
    git describe.

    """
    cmd = ['git', 'describe', '--tags']
    if branch is not None:
        cmd.append(branch)
    try:
        result = subprocess.check_output(cmd, cwd=reporoot).decode('utf-8').strip()
        if '-' in result:
            # Descriptions that come after a commit look like
            # 2.0.0-1-abcde, and we want to remove the SHA value from
            # the end since we only care about the version number
            # itself, but we need to recognize that the change is
            # unreleased so keep the -1 part.
            result, dash, ignore = result.rpartition('-')
    except subprocess.CalledProcessError:
        # This probably means there are no tags.
        result = '0.0.0'
    return result


def _get_branch_base(reporoot, branch):
    "Return the tag at base of the branch."
    # Based on
    # http://stackoverflow.com/questions/1527234/finding-a-branch-point-with-git
    # git rev-list $(git rev-list --first-parent \
    #   ^origin/stable/newton master | tail -n1)^^!
    #
    # Determine the list of commits accessible from the branch we are
    # supposed to be scanning, but not on master.
    cmd = [
        'git',
        'rev-list',
        '--first-parent',
        branch,  # on the branch
        '^master',  # not on master
    ]
    try:
        parents = subprocess.check_output(
            cmd, cwd=reporoot,
            # Trap stderr so it isn't dumped into our output.
            stderr=subprocess.PIPE,
        ).decode('utf-8').strip()
        if not parents:
            # There are no commits on the branch, yet, so we can use
            # our current-version logic.
            return _get_current_version(reporoot, branch)
    except subprocess.CalledProcessError:
        return None
    parent = parents.splitlines()[-1]
    # Now get the previous commit, which should be the one we tagged
    # to create the branch.
    cmd = [
        'git',
        'rev-list',
        '{}^^!'.format(parent),
    ]
    try:
        sha = subprocess.check_output(cmd, cwd=reporoot).decode('utf-8').strip()
    except subprocess.CalledProcessError:
        return None
    # Now get the tag for that commit.
    cmd = [
        'git',
        'describe',
        '--abbrev=0',
        sha,
    ]
    try:
        return subprocess.check_output(cmd, cwd=reporoot).decode('utf-8').strip()
    except subprocess.CalledProcessError:
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--deliverables-dir',
        default=openstack_releases.deliverable_dir,
        help='location of deliverable files',
    )
    parser.add_argument(
        '--no-cleanup',
        dest='cleanup',
        default=True,
        action='store_false',
        help='do not remove temporary files',
    )
    parser.add_argument(
        'repository_cache',
        help='location of existing copies of repositories',
    )
    parser.add_argument(
        'series',
        help='the release series, such as "newton" or "ocata"',
    )
    parser.add_argument(
        'deliverable',
        nargs='+',
        help='the deliverable name',
    )
    args = parser.parse_args()

    workdir = tempfile.mkdtemp(prefix='releases-')

    def cleanup_workdir():
        if args.cleanup:
            shutil.rmtree(workdir, True)
    atexit.register(cleanup_workdir)

    branch_name = 'origin/stable/' + args.series

    all_deliv = deliverable.Deliverables(
        root_dir=args.deliverables_dir,
        collapse_history=False,
    )
    for deliv in all_deliv.get_deliverables(None, args.series):
        if deliv.name not in args.deliverable:
            continue
        if deliv.get_branch_location(branch_name) is not None:
            # the branch is already defined for this project
            sys.stderr.write('{} already has a branch {}\n'.format(
                deliv.name, branch_name))
            continue
        # We're only importing stable branches, and those are
        # specified by the version number. We therefore only need one
        # repository, and it shouldn't matter which one. That said, we
        # might not actually find the branch in the first repo so loop
        # until we do.
        for r in deliv.repos:
            reporoot = os.path.join(args.repository_cache, r)
            version = _get_branch_base(reporoot, branch_name)
            if version:
                print(deliv.name, args.series, version)
                break
        else:
            sys.stderr.write('could not find {} in any repos for {}\n'.format(
                branch_name, deliv.name))


if __name__ == '__main__':
    main()
