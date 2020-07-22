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
import json
import logging
import os
import os.path
import shutil
import subprocess
import sys
import tempfile

import requests

from openstack_releases import gitutils
from openstack_releases import yamlutils

LOG = logging.getLogger(__name__)


def git_log(workdir, repo, git_range, extra_args=[]):
    results = {
        'range': git_range,
        'logs': []
    }
    cmd = ['git', 'log', '--no-color']
    cmd.extend(extra_args)
    if isinstance(git_range, str):
        cmd.append(git_range)
    elif isinstance(git_range, tuple):
        cmd.append('{start}..{end}'.format(
            start=git_range[0], end=git_range[1]))
    else:
        cmd.extend(git_range)
    LOG.debug('\n' + ' '.join(cmd) + '\n')
    output = subprocess.check_output(cmd, cwd=os.path.join(workdir, repo))
    results['logs'] = [el for el in output.decode('utf-8').split("\n") if el]
    LOG.debug(results)
    return results


def filter_results(content,
                   ignore_no_results=False,
                   ignore_errors=False,
                   ignore_not_yet_released=False,
                   ignore_all=False):
    filtered = []
    for repo in content:
        removed = False
        if ignore_all and \
            (repo['error'] or
             repo['not_yet_released'] or
             not repo['commits'] or
             not repo['commits'].get('logs', None)):
            removed = True
            LOG.debug("ignoring all")
        elif ignore_errors and repo['error']:
            removed = True
            LOG.debug("ignoring errors")
        elif ignore_not_yet_released and repo['not_yet_released']:
            removed = True
            LOG.debug("ignoring not yet released")
        elif ignore_no_results and (not repo.get('commits', None) or
                                    not repo.get('commits', None).get(
                                        'logs', None)):
            LOG.debug("ignoring no results")
            removed = True
        if not removed:
            filtered.append(repo)
        else:
            LOG.debug('repo {} will be ignored'.format(repo['repo']))
            LOG.debug(repo)
    return filtered


def generate_output(content, output_format='std',
                    ignore_no_results=False,
                    ignore_errors=False,
                    ignore_not_yet_released=False,
                    ignore_all=False):
    filtered = filter_results(content, ignore_no_results, ignore_errors,
                              ignore_not_yet_released, ignore_all)
    if output_format == 'json':
        return json.dumps(filtered, indent=4)
    if output_format == 'yaml':
        return yamlutils.dumps(filtered)
    if output_format == 'std':
        out = []
        for repo in filtered:
            out.append(
                '\033[1m\033[91m[ Unreleased changes in '
                '{rep} ({br}) ]\033[0m'.format(rep=repo['repo'],
                                               br=repo['branch'])
            )

            if repo['not_yet_released'] or repo['error']:
                out.append(repo['msg'])
                continue

            range_msg = 'Changes between {start} and {end}'.format(
                start=repo['commits']['range'][0],
                end=repo['commits']['range'][1])
            out.append(range_msg)
            if repo['commits'].get('logs', None):
                out.append("\n".join(repo['commits']['logs']))
            out.append('')
        return '\n'.join(out)


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
        "-v",
        "--verbosity",
        action="count",
        help="increase output verbosity",
        default=0)
    parser.add_argument(
        "--ignore-no-results",
        action='store_true',
        default=False,
        help="Ignore projects without difference between the HEAD and"
             "the retrieved previous tag."
             "They will be ignored in the command output.")
    parser.add_argument(
        "--ignore-errors",
        action='store_true',
        default=False,
        help="Ignore projects in error (repos not found).")
    parser.add_argument(
        "--ignore-not-yet-released",
        action='store_true',
        default=False,
        help="Ignore projects not yet released (previous tag not found).")
    parser.add_argument(
        "-I",
        "--ignore-all",
        action='store_true',
        default=False,
        help="Ignore projects without difference between the HEAD and"
             "previous tag, projects not yet released, projects in error."
             "Similar to call command with "
             "`--ignore-no-results --ignore-errors --ignore-not-yet-released`"
             "They will be ignored in the command output.")
    parser.add_argument(
        "-f",
        "--format",
        choices=['std', 'json', 'yaml'],
        default='std',
        help="Output format")
    parser.add_argument(
        'branch',
        help=('Branch to analyze'),
    )
    parser.add_argument(
        'repos',
        nargs='*',
        help=('Repos to analyze, '
              'repo should be e.g. openstack/glance'),
    )
    args = parser.parse_args()

    log_level = logging.ERROR
    if args.verbosity >= 3:
        log_level = logging.DEBUG
    elif args.verbosity >= 2:
        log_level = logging.INFO
    elif args.verbosity >= 1:
        log_level = logging.WARNING

    # Set up logging, including making some loggers quiet.
    logging.basicConfig(
        format='%(levelname)7s: %(message)s',
        stream=sys.stdout,
        level=log_level,
    )
    logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)

    workdir = tempfile.mkdtemp(prefix='releases-')
    LOG.debug('creating temporary files in %s' % workdir)

    def cleanup_workdir():
        if args.cleanup:
            shutil.rmtree(workdir, True)
        else:
            LOG.info('not cleaning up %s' % workdir)
    atexit.register(cleanup_workdir)

    # Remove any inherited PAGER environment variable to avoid
    # blocking the output waiting for input.
    os.environ['PAGER'] = ''
    output = []

    for repo in args.repos:
        current = {
            'repo': repo,
            'branch': args.branch,
            'commits': None,
            'error': False,
            'not_yet_released': False,
            'msg': ''
        }
        url = 'https://opendev.org/{}'.format(repo)
        res = requests.get(url)
        if res.status_code == 404:
            current.update({'error': True})
            current.update(
                {'msg': "fatal: repository '{}' not found".format(url)})
            output.append(current)
            continue

        # Start by checking out master, always. We need the repo
        # checked out before we can tell if the stable branch
        # really exists.
        gitutils.clone_repo(
            workdir,
            repo,
            branch='master',
        )

        # Set some git configuration values to allow us to perform
        # local operations like tagging.
        gitutils.ensure_basic_git_config(
            workdir, repo,
            {'user.email': 'openstack-infra@lists.openstack.org',
             'user.name': 'OpenStack Proposal Bot'},
        )

        # Determine which branch we should actually be looking
        # at. Assume any series for which there is no stable
        # branch will be on 'master'.
        if gitutils.stable_branch_exists(workdir, repo, args.branch):
            branch = 'stable/' + args.branch
        else:
            branch = 'master'

        if branch != 'master':
            # Check out the repo again to the right branch if we
            # didn't get it the first time.
            gitutils.clone_repo(
                workdir,
                repo,
                branch=branch,
            )

        # look at the previous tag for the parent of the commit
        # getting the new release
        previous_tag = gitutils.get_latest_tag(workdir, repo, always=False)

        if not previous_tag:
            current.update({'not_yet_released': True})
            current.update(
                {'msg': '{} has not yet been released'.format(repo)})
            output.append(current)
            continue

        start_range = previous_tag
        head_sha = gitutils.get_head(workdir, repo)

        if not start_range:
            current.update({'not_yet_released': True})
            current.update(
                {'msg': '{} has not yet been released'.format(repo)})
            output.append(current)
            continue

        commits = git_log(workdir, repo, (start_range, head_sha),
                          extra_args=[
                              '--no-color',
                              '--no-merges',
                              '--graph',
                              '--format=%h %ci %s'])

        current.update({'commits': commits})
        output.append(current)

    LOG.debug(output)

    out = generate_output(output, output_format=args.format,
                          ignore_no_results=args.ignore_no_results,
                          ignore_errors=args.ignore_errors,
                          ignore_not_yet_released=args.ignore_not_yet_released,
                          ignore_all=args.ignore_all)
    print("".join(out))
    return 0
