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
import sys
import tempfile

import yaml

from openstack_releases import defaults
from openstack_releases import gitutils
from openstack_releases import governance


def header(title):
    print('\n%s' % title)
    print('-' * len(title))


def git_show(workdir, repo, title, ref):
    header('%s %s' % (title, ref))
    cmd = ['git', 'log', '-n', '1', '--decorate', '--format=medium', ref]
    print('\n' + ' '.join(cmd) + '\n')
    subprocess.check_call(cmd, cwd=os.path.join(workdir, repo))
    print()


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


def git_list_existing_branches(workdir, repo):
    header('All Branches with Version Numbers')
    for branch in gitutils.get_branches(workdir, repo):
        try:
            description = subprocess.check_output(
                ['git', 'describe', branch],
                cwd=os.path.join(workdir, repo),
            ).decode('utf-8').strip()
        except subprocess.CalledProcessError as exc:
            description = exc.output
        print('{:<30} {}'.format(branch, description))


def git_branch_contains(workdir, repo, title, commit):
    header('%s %s' % (title, commit))
    cmd = ['git', 'branch', '-r', '--contains', commit]
    print('\n' + ' '.join(cmd) + '\n')
    out = subprocess.check_output(
        cmd,
        cwd=os.path.join(workdir, repo),
    ).decode('utf-8')
    print(out)
    return sorted(
        o.strip()
        for o in out.splitlines()
        if '->' not in o
    )


def git_diff(workdir, repo, git_range, file_pattern):
    repo_dir = os.path.join(workdir, repo)
    files = list(glob.glob(os.path.join(repo_dir,
                                        file_pattern)))
    if files:
        header('Requirements Changes %s' % git_range)
        for f in files:
            cmd = [
                'git', 'diff', '-U0', '--no-color',
                '--ignore-space-change', '--ignore-blank-lines',
                git_range,
                f[len(repo_dir) + 1:],
            ]
            print(' '.join(cmd) + '\n')
            subprocess.check_call(cmd, cwd=repo_dir)
            print()


def main():
    if not sys.stdout.encoding:
        # Wrap sys.stdout with a writer that knows how to handle
        # encoding Unicode data.
        import codecs
        wrapped_stdout = codecs.getwriter('UTF-8')(sys.stdout)
        sys.stdout = wrapped_stdout

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

    team_data = governance.get_team_data()

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
        if series == '_independent':
            default_model = 'independent'
        else:
            default_model = 'no release model specified'

        # By default assume the project does not use milestones.
        header('Release model')
        print(deliverable_info.get('release-model', default_model))

        header('Team details')
        if 'team' in deliverable_info:
            team_name = deliverable_info['team']
            team_dict = team_data.get(team_name)
            if team_dict:
                team = governance.Team(team_name, team_dict)
                print('found team %s' % team_name)
                print('  PTL    : %(name)s (%(irc)s)' % team.ptl)
                print('  Liaison: %s (%s)\n' % team.liaison)
                deliverable_name = os.path.basename(filename)[:-5]  # remove .yaml
                deliverable = team.deliverables.get(deliverable_name)
                if deliverable:
                    print('found deliverable %s' % deliverable_name)
                    for rn, repo in sorted(deliverable.repositories.items()):
                        print('\nrepo %s\ntags:' % repo.name)
                        for t in repo.tags:
                            print('  %s' % t)
                        print('')
                else:
                    print(('no deliverable %r found for team %r, '
                           'cannot report on governance status') %
                          (deliverable_name, team_name))
            else:
                print('no team %r found, cannot report on governance status' %
                      team_name)
        else:
            print('no team name given, cannot report on governance status')

        if series == defaults.RELEASE:
            branch = 'master'
        else:
            branch = 'stable/' + series

        # If there are no releases listed, this is probably a new
        # deliverable file for initializing a new series. We don't
        # need to list its changes.
        if not deliverable_info.get('releases'):
            header('No releases')
            print('no releases were found, assuming an initialization file')
            continue

        # assume the releases are in order and take the last one
        new_release = deliverable_info['releases'][-1]

        # build a map between version numbers and the release details
        by_version = {
            str(r['version']): r
            for r in deliverable_info['releases']
        }

        for project in new_release['projects']:

            tag_exists = gitutils.commit_exists(
                project['repo'],
                new_release['version'],
            )
            if tag_exists:
                print('%s %s exists on git server already' %
                      (project['repo'], new_release['version']))

            # Check out the code.
            print('\nChecking out repository {}'.format(project['repo']))
            subprocess.check_call(
                ['zuul-cloner',
                 '--branch', branch,
                 '--workspace', workdir,
                 'git://git.openstack.org',
                 project['repo'],
                 ]
            )

            # look at the previous tag for the parent of the commit
            # getting the new release
            previous_tag = gitutils.get_latest_tag(
                workdir,
                project['repo'],
                '{}^'.format(project['hash'])
            )
            previous_release = by_version.get(previous_tag)

            start_range = previous_tag
            if previous_release:
                previous_project = {
                    x['repo']: x
                    for x in previous_release['projects']
                }.get(project['repo'])
                if previous_project is not None:
                    start_range = previous_tag

            if start_range:
                git_range = '%s..%s' % (start_range, project['hash'])
            else:
                git_range = project['hash']

            # Show details about the commit being tagged.
            header('Details for commit receiving new tag %s' %
                   new_release['version'])
            print('\ngit describe %s\n' % project['hash'])
            try:
                subprocess.check_call(
                    ['git', 'describe', project['hash']],
                    cwd=os.path.join(workdir, project['repo']),
                )
            except subprocess.CalledProcessError as e:
                print('WARNING: Could not run git describe: %s' % e)

            git_show(
                workdir=workdir,
                repo=project['repo'],
                title='Check existing tags',
                ref=project['hash'],
            )

            git_list_existing_branches(
                workdir=workdir,
                repo=project['repo'],
            )

            branches = git_branch_contains(
                workdir=workdir,
                repo=project['repo'],
                title='Branches containing commit',
                commit=project['hash'],
            )

            header('Relationship to HEAD')
            if series == '_independent':
                if branches:
                    tag_branch = branches[0]
                else:
                    tag_branch = branch
                head_sha = gitutils.sha_for_tag(
                    workdir,
                    project['repo'],
                    tag_branch,
                )
                print('HEAD of {} is {}'.format(tag_branch, head_sha))
            else:
                if (branch in branches) or (not branches):
                    tag_branch = branch
                else:
                    tag_branch = branches[0]
                head_sha = gitutils.sha_for_tag(
                    workdir,
                    project['repo'],
                    tag_branch,
                )
                print('HEAD of {} is {}'.format(tag_branch, head_sha))
            requested_sha = gitutils.sha_for_tag(
                workdir,
                project['repo'],
                project['hash'],
            )
            # If the sha for HEAD and the requested release don't
            # match, show any unreleased changes on the branch. We ask
            # git to give us the real SHA for the requested release in
            # case the deliverables file has the short version of the
            # hash.
            if head_sha == requested_sha:
                print('\nRequest releases from HEAD on %s' % tag_branch)
            else:
                git_log(workdir, project['repo'], 'Release will NOT include',
                        '%s..%s' % (requested_sha, head_sha),
                        extra_args=['--format=%h %ci %s'])

            # Show any requirements changes in the upcoming release.
            # Include setup.cfg, in case the project uses "extras".
            if start_range:
                git_diff(workdir, project['repo'], git_range, '*requirements*.txt')
                git_diff(workdir, project['repo'], git_range, 'setup.cfg')

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

            # Show any changes in the previous release but not in this
            # release, in case someone picks an "early" SHA or a
            # regular commit instead of the appropriate merge commit.
            previous_tag_exists = False
            if previous_release:
                previous_tag_exists = gitutils.commit_exists(
                    project['repo'],
                    previous_release,
                )
            if previous_tag_exists:
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
                ).decode('utf-8').split()
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

    return 0
