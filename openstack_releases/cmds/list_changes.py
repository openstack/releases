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

"""Show the changes that will be included in the release.
"""

from __future__ import print_function

import argparse
import atexit
import glob
import os
import os.path
import shutil
import subprocess
import tempfile

import yaml

from openstack_releases import defaults
from openstack_releases import gitutils


def header(title):
    print('\n%s' % title)
    print('-' * len(title))


def git_log(workdir, repo, title, git_range, extra_args=[]):
    header('%s %s' % (title, git_range))
    cmd = ['git', 'log', '--no-color']
    cmd.extend(extra_args)
    if isinstance(git_range, str):
        cmd.append(git_range)
    else:
        cmd.extend(git_range)
    print('\n' + ' '.join(cmd) + '\n')
    subprocess.check_call(cmd, cwd=os.path.join(workdir, repo))
    print()


def git_diff(workdir, repo, git_range, file_pattern):
    repo_dir = os.path.join(workdir, repo)
    files = list(glob.glob(os.path.join(repo_dir,
                                        file_pattern)))
    if files:
        header('Requirements Changes %s' % git_range)
        cmd = ['git', 'diff', '-U0', '--no-color', git_range]
        cmd.extend(f[len(repo_dir) + 1:] for f in files)
        subprocess.check_call(cmd, cwd=repo_dir)
        print()


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
        print('no modified deliverable files, skipping report')
        return 0

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

    # Remove any inherited PAGER environment variable to avoid
    # blocking the output waiting for input.
    os.environ['PAGER'] = ''

    for filename in filenames:
        if not os.path.exists(filename):
            print('\n%s was removed, skipping' % filename)
            continue
        print('\n' + ('=' * 80))
        print('\nChecking %s\n' % filename)
        with open(filename, 'r') as f:
            deliverable_info = yaml.load(f.read())

        series = os.path.basename(
            os.path.dirname(
                os.path.abspath(filename)
            )
        )
        if series == defaults.RELEASE:
            branch = 'master'
        else:
            branch = 'stable/' + series

        # assume the releases are in order and take the last two
        new_release = deliverable_info['releases'][-1]
        if len(deliverable_info['releases']) >= 2:
            previous_release = deliverable_info['releases'][-2]
        else:
            previous_release = None
        for project in new_release['projects']:
            tag_exists = gitutils.commit_exists(
                project['repo'],
                new_release['version'],
            )
            if tag_exists:
                print('%s %s exists on git server already' %
                      (project['repo'], new_release['version']))

            # Check out the code.
            print('\nChecking out repository')
            subprocess.check_call(
                ['zuul-cloner',
                 '--branch', branch,
                 '--workspace', workdir,
                 'git://git.openstack.org',
                 project['repo'],
                 ]
            )

            start_range = None
            if previous_release:
                previous_project = {
                    x['repo']: x
                    for x in previous_release['projects']
                }.get(project['repo'])
                if previous_project is not None:
                    start_range = previous_project['hash']
            if not start_range:
                start_range = (
                    gitutils.get_latest_tag(workdir, project['repo']) or None
                )

            if start_range:
                git_range = '%s..%s' % (start_range, project['hash'])
            else:
                git_range = project['hash']

            # Show any requirements changes in the upcoming release.
            if start_range:
                git_diff(workdir, project['repo'], git_range, '*requirements*.txt')

            # Show the changes since the last release, first as a
            # graph view so we can check for bad merges, and then with
            # more detail.
            git_log(workdir, project['repo'],
                    'Release %s will include' % new_release['version'],
                    git_range,
                    extra_args=['--graph', '--oneline', '--decorate',
                                '--topo-order'])
            git_log(workdir, project['repo'],
                    'Details Contents',
                    git_range,
                    extra_args=['--no-merges', '--topo-order'])

            # If the sha for HEAD and the requested release don't
            # match, show any unreleased changes on the branch. We ask
            # git to give us the real SHA for the requested release in
            # case the deliverables file has the short version of the
            # hash.
            head_sha = gitutils.sha_for_tag(workdir, project['repo'], 'HEAD')
            requested_sha = gitutils.sha_for_tag(
                workdir,
                project['repo'],
                project['hash'],
            )
            if head_sha == requested_sha:
                print('Request releases from HEAD on %s' % branch)
            else:
                git_log(workdir, project['repo'], 'Release will NOT include',
                        '%s..%s' % (requested_sha, head_sha),
                        extra_args=['--format=%h %ci %s'])

            # Show any changes in the previous release but not in this
            # release, in case someone picks an "early" SHA or a
            # regular commit instead of the appropriate merge commit.
            if previous_release:
                git_log(
                    workdir, project['repo'],
                    'Patches in previous release but not in this one',
                    [project['hash'],
                     '--not',
                     previous_release['version']],
                    extra_args=['--topo-order', '--oneline', '--no-merges'],
                )
                header('New release %s includes previous release %s' %
                       (new_release['version'], previous_release['version']))
                if not tag_exists:
                    subprocess.check_call(
                        ['git', 'tag', new_release['version'],
                         project['hash']],
                        cwd=os.path.join(workdir, project['repo']),
                    )
                print('\ngit tag --contains %s\n' %
                      previous_release['version'])
                containing_tags = subprocess.check_output(
                    ['git', 'tag',
                     '--contains',
                     previous_release['version']],
                    cwd=os.path.join(workdir, project['repo']),
                ).split()
                print('Containing tags:', containing_tags)
                if new_release['version'] not in containing_tags:
                    print('WARNING: Missing %s' % new_release['version'])
                else:
                    print('Found new version %s' % new_release['version'])

                is_ancestor = gitutils.check_ancestry(
                    workdir,
                    project['repo'],
                    previous_release['version'],
                    project['hash'],
                )
                if is_ancestor:
                    print('SHA found in descendants')
                else:
                    print('SHA NOT FOUND in descendants')

            # Show more details about the commit being tagged.
            header('Details for commit receiving new tag')
            print('\ngit describe %s\n' % project['hash'])
            try:
                subprocess.check_call(
                    ['git', 'describe', project['hash']],
                    cwd=os.path.join(workdir, project['repo']),
                )
            except subprocess.CalledProcessError as e:
                print('WARNING: Could not run git describe: %s' % e)

    return 0
