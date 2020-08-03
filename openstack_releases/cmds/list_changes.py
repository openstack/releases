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

import argparse
import atexit
import glob
import json
import logging
import os
import os.path
import re
import shutil
import subprocess
import sys
import tempfile

from openstack_governance import governance
import pyfiglet
import requests

from openstack_releases import defaults
from openstack_releases import deliverable
from openstack_releases import gitutils
from openstack_releases import hound
from openstack_releases import liaisons
from openstack_releases import release_notes
from openstack_releases import yamlutils


def header(title):
    print('\n%s' % title)
    print('-' * len(title))


def banner(text):
    pyfiglet.print_figlet(text, font='banner', width=120)


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
            # strip to the real tag value
            match = re.match('^(.*)-[0-9]+-g[a-f0-9]+', description,
                             re.IGNORECASE)
            if match:
                tag = match.groups()[0]
            else:
                tag = ''
        except subprocess.CalledProcessError as exc:
            description = exc.output.decode('utf-8').strip()
            tag = ''
        if not tag:
            print('{:<30} {:<20}'.format(branch, description))
        else:
            try:
                date = subprocess.check_output(
                    ['git', 'log', '-1', '--pretty=format:%ar', tag],
                    cwd=os.path.join(workdir, repo),
                ).decode('utf-8').strip()
            except subprocess.CalledProcessError as exc:
                date = exc.output.decode('utf-8')
            print('{:<30} {:<20} {:<12} {}'.format(
                branch, description, tag, date))


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


def git_diff(workdir, repo, git_range, file_pattern, title=''):
    repo_dir = os.path.join(workdir, repo)
    files = list(glob.glob(os.path.join(repo_dir,
                                        file_pattern)))
    if files:
        if title:
            header(title)
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


def gerrit_query(*query):
    url = 'https://review.openstack.org/changes/?q=' + '+'.join(query)
    response = requests.get(url)
    if (response.status_code // 100) != 2:
        raise RuntimeError(
            'Bad HTTP response from gerrit %s: %s' %
            (url, response.status_code)
        )
    elif response.content[:4] == b")]}'":
        content = response.content[5:].decode('utf-8')
        return json.loads(content)
    else:
        print('could not parse response from %s' % url)
        print(repr(content))
        raise RuntimeError('failed to parse gerrit response')


def list_gerrit_patches(title, template, query):
    header('{}: "{}"'.format(title, query))
    try:
        reviews = gerrit_query(query)
    except Exception as err:
        print(err)
    else:
        for r in reviews:
            if 'topic' not in r:
                r['topic'] = ''
            try:
                print(template.format(**r))
            except Exception as err:
                print('Could not format review data: {}'.format(err))
                print(r)
        print('{} results\n'.format(len(reviews)))


def show_watched_queries(branch, repo):
    with open('watched_queries.yml', 'r', encoding='utf-8') as f:
        watched_queries = yamlutils.loads(f.read())
    template = watched_queries['template']
    for q in watched_queries['queries']:
        list_gerrit_patches(
            q['title'],
            q.get('template', template),
            q['query'].format(
                branch=branch,
                project=repo,
            ),
        )


def show_dependency_listings(package_name, official_repos):
    header('Users of {}'.format(package_name))
    hound.show_dependency_listings(package_name, official_repos)


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
        '--no-shortcut', '--force', '-f',
        dest='shortcut',
        default=True,
        action='store_false',
        help='if a tag has been applied, skip the repo',
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
        print('no modified deliverable files, skipping report')
        return 0

    workdir = tempfile.mkdtemp(prefix='releases-')
    print('creating temporary files in %s' % workdir)

    def cleanup_workdir():
        if args.cleanup:
            shutil.rmtree(workdir, True)
        else:
            print('not cleaning up %s' % workdir)
    atexit.register(cleanup_workdir)

    gov_data = governance.Governance.from_remote_repo()
    official_repos = set(
        r.name
        for r in gov_data.get_repositories()
    )

    all_deliverables = deliverable.Deliverables(
        './deliverables',
        False,
    )

    liaison_data = liaisons.get_liaisons()

    # Remove any inherited PAGER environment variable to avoid
    # blocking the output waiting for input.
    os.environ['PAGER'] = ''

    for filename in filenames:
        if not os.path.exists(filename):
            print('\n%s was removed, skipping' % filename)
            continue
        print('\n' + ('=' * 80))
        print('\nChecking %s\n' % filename)
        deliv = deliverable.Deliverable.read_file(filename)

        stable_branch = deliv.series not in ['independent', defaults.RELEASE]

        # By default assume the project does not use milestones.
        header('Release model')
        print(deliv.model)

        header('Team details')
        if deliv.team:
            team_name = deliv.team
            try:
                team = gov_data.get_team(team_name)
            except ValueError:
                team = None
            if team:
                print('found team %s' % team_name)
                print('  PTL    : %(name)s (%(irc)s)' % team.ptl)
                for liaison in liaison_data.get(team.name.lower(), []):
                    print('  Liaison: %(name)s (%(irc)s)' % liaison)
                team_deliv = team.deliverables.get(deliv.name)
                if team_deliv:
                    print('found deliverable %s' % deliv.name)
                    for rn, repo in sorted(team_deliv.repositories.items()):
                        follows_stable_policy = 'stable:follows-policy' in repo.tags
                        print('\nrepo %s\ntags:' % repo.name)
                        for t in repo.tags:
                            print('  %s' % t)
                        print('')
                        if stable_branch and follows_stable_policy:
                            banner('Needs Stable Policy Review')
                            print()
                else:
                    print(('no deliverable %r found for team %r, '
                           'cannot report on governance status') %
                          (deliv.name, team_name))
                if not deliv.is_independent:
                    # Show other deliverables owned by the team and
                    # included in this series.
                    team_deliv_in_series = all_deliverables.get_deliverables(
                        team.name, deliv.series)
                    if team_deliv_in_series:
                        print('Other {} deliverables in {}:'.format(
                            team.name, deliv.series))
                    for d in team_deliv_in_series:
                        print('  {} ({})'.format(d.name, d.latest_release or None))
                    print()
            else:
                print('no team %r found, cannot report on governance status' %
                      team_name)
        else:
            print('no team name given, cannot report on governance status')

        # If there are no releases listed, this is probably a new
        # deliverable file for initializing a new series. We don't
        # need to list its changes.
        if not deliv.is_released:
            header('No releases')
            print('no releases were found, assuming an initialization file')
            continue

        # assume the releases are in order and take the last one
        new_release = deliv.releases[-1]

        for project in new_release.projects:

            tag_exists = gitutils.tag_exists(
                project.repo.name,
                new_release.version,
            )
            if tag_exists:
                print('%s %s exists on git server already' %
                      (project.repo.name, new_release.version))
                if args.shortcut:
                    print('skipping further processing')
                    continue

            if project.repo.is_retired:
                print('%s is retired' % (project.repo.name,))
                if args.shortcut:
                    print('skipping further processing')
                    continue

            # Start by checking out master, always. We need the repo
            # checked out before we can tell if the stable branch
            # really exists.
            gitutils.clone_repo(
                workdir,
                project.repo.name,
                branch='master',
            )

            # Set some git configuration values to allow us to perform
            # local operations like tagging.
            gitutils.ensure_basic_git_config(
                workdir, project.repo.name,
                {'user.email': 'openstack-infra@lists.openstack.org',
                 'user.name': 'OpenStack Proposal Bot'},
            )

            # Determine which branch we should actually be looking
            # at. Assume any series for which there is no stable
            # branch will be on 'master'.
            if gitutils.stable_branch_exists(workdir,
                                             project.repo.name,
                                             deliv.series):
                branch = 'stable/' + deliv.series
            else:
                branch = 'master'

            if branch != 'master':
                # Check out the repo again to the right branch if we
                # didn't get it the first time.
                gitutils.clone_repo(
                    workdir,
                    project.repo.name,
                    branch=branch,
                )

            # look at the previous tag for the parent of the commit
            # getting the new release
            previous_tag = gitutils.get_latest_tag(
                workdir,
                project.repo.name,
                '{}^'.format(project.hash),
                always=False,
            )
            try:
                previous_release = deliv.get_release(previous_tag)
            except ValueError:
                previous_release = None

            start_range = previous_tag
            if previous_release:
                previous_project = {
                    x.repo.name: x
                    for x in previous_release.projects
                }.get(project.repo.name)
                if previous_project is not None:
                    start_range = previous_tag

            if start_range:
                git_range = '%s..%s' % (start_range, project.hash)
            else:
                git_range = project.hash

            # Show details about the commit being tagged.
            header('Details for commit receiving new tag %s' %
                   new_release.version)
            print('\ngit describe %s\n' % project.hash)
            try:
                subprocess.check_call(
                    ['git', 'describe', project.hash],
                    cwd=os.path.join(workdir, project.repo.name),
                )
            except subprocess.CalledProcessError as e:
                print('WARNING: Could not run git describe: %s' % e)

            git_show(
                workdir=workdir,
                repo=project.repo.name,
                title='Check existing tags',
                ref=project.hash,
            )

            git_list_existing_branches(
                workdir=workdir,
                repo=project.repo.name,
            )

            branches = git_branch_contains(
                workdir=workdir,
                repo=project.repo.name,
                title='Branches containing commit',
                commit=project.hash,
            )

            header('Relationship to HEAD')
            if deliv.is_independent:
                if branches:
                    tag_branch = branches[0]
                else:
                    tag_branch = branch
                head_sha = gitutils.sha_for_tag(
                    workdir,
                    project.repo.name,
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
                    project.repo.name,
                    tag_branch,
                )
                print('HEAD of {} is {}'.format(tag_branch, head_sha))
            requested_sha = gitutils.sha_for_tag(
                workdir,
                project.repo.name,
                project.hash,
            )
            # If the sha for HEAD and the requested release don't
            # match, show any unreleased changes on the branch. We ask
            # git to give us the real SHA for the requested release in
            # case the deliverables file has the short version of the
            # hash.
            if head_sha == requested_sha:
                print('\nRequest releases from HEAD on %s' % tag_branch)
            else:
                git_log(workdir, project.repo.name, 'Release will NOT include',
                        '%s..%s' % (requested_sha, head_sha),
                        extra_args=['--format=%h %ci %s'])

            show_watched_queries(branch, project.repo.name)

            # Show any requirements changes in the upcoming release.
            # Include setup.cfg, in case the project uses "extras".
            if start_range:
                git_diff(workdir, project.repo.name, git_range, '*requirements*.txt',
                         'Requirements Changes %s' % git_range)
                git_diff(workdir, project.repo.name, git_range, 'doc/requirements.txt',
                         'Doc Requirements Changes %s' % git_range)
                git_diff(workdir, project.repo.name, git_range, 'setup.cfg',
                         'setup.cfg Changes %s' % git_range)
                git_diff(workdir, project.repo.name, git_range, 'bindep.txt',
                         'bindep.txt Changes %s' % git_range)

            # Before we try to determine if the previous release
            # is an ancestor or produce the release notes we need
            # the tag to exist in the local repository.
            if not tag_exists:
                header('Applying Temporary Tag')
                print('\ngit tag {version} {hash}'.format(
                    version=new_release.version,
                    hash=project.hash,
                ))
                subprocess.check_call(
                    ['git', 'tag', new_release.version,
                     project.hash],
                    cwd=os.path.join(workdir, project.repo.name),
                )

            # Show any changes in the previous release but not in this
            # release, in case someone picks an "early" SHA or a
            # regular commit instead of the appropriate merge commit.
            previous_tag_exists = False
            if previous_release:
                previous_tag_exists = gitutils.tag_exists(
                    project.repo.name,
                    previous_release.version,
                )
            if previous_tag_exists:
                git_log(
                    workdir, project.repo.name,
                    'Patches in previous release but not in this one',
                    [previous_release.version,
                     '--not',
                     project.hash],
                    extra_args=['--topo-order', '--oneline', '--no-merges'],
                )

                # The tag will have been added as a local tag above if
                # it does not already exist.
                header('New release %s includes previous release %s' %
                       (new_release.version, previous_release.version))
                print('\ngit tag --contains %s\n' %
                      previous_release.version)
                containing_tags = subprocess.check_output(
                    ['git', 'tag',
                     '--contains',
                     previous_release.version],
                    cwd=os.path.join(workdir, project.repo.name),
                ).decode('utf-8').split()
                print('Containing tags:', containing_tags)
                if new_release.version not in containing_tags:
                    print('WARNING: Missing %s' % new_release.version)
                else:
                    print('Found new version %s' % new_release.version)

                is_ancestor = gitutils.check_ancestry(
                    workdir,
                    project.repo.name,
                    previous_release.version,
                    project.hash,
                )
                if is_ancestor:
                    print('SHA found in descendants')
                else:
                    print('SHA NOT FOUND in descendants')

            # Show the changes since the last release, first as a
            # graph view so we can check for bad merges, and then with
            # more detail.
            git_log(workdir, project.repo.name,
                    'Release %s will include' % new_release.version,
                    git_range,
                    extra_args=['--graph', '--oneline', '--decorate',
                                '--topo-order'])
            git_log(workdir, project.repo.name,
                    'Details Contents',
                    git_range,
                    extra_args=['--no-merges', '--topo-order'])

            # The tag will have been added as a local tag above if it does
            # not already exist.
            header('Release Notes')
            try:
                notes = release_notes.generate_release_notes(
                    repo=project.repo.name,
                    repo_path=os.path.join(workdir, project.repo.name),
                    start_revision=new_release.diff_start or start_range or '',
                    end_revision=new_release.version,
                    show_dates=True,
                    skip_requirement_merges=True,
                    is_stable=branch.startswith('stable/'),
                    series=deliv.series,
                    email='test-job@openstack.org',
                    email_from='test-job@openstack.org',
                    email_reply_to='noreply@openstack.org',
                    email_tags='',
                    include_pypi_link=False,
                    changes_only=False,
                    first_release=deliv.is_first_release,
                    deliverable_file=filename,
                    description='',
                    publishing_dir_name=project.repo.name,
                )
            except Exception:
                logging.exception('Failed to produce release notes')
            else:
                print('\n')
                print(notes)

            if 'library' in deliv.type:
                show_dependency_listings(
                    project.guess_sdist_name(),
                    official_repos,
                )

    return 0
