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
import os
import os.path
import shutil
import subprocess
import tempfile

import yaml

from openstack_releases import defaults
from openstack_releases import gitutils


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
        print('\nChecking %s' % filename)
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
            if gitutils.commit_exists(project['repo'],
                                      new_release['version']):
                print('%s %s exists already' %
                      (project['repo'], new_release['version']))
                continue

            if previous_release:
                git_range = '%s..%s' % (previous_release['version'],
                                        project['hash'])
            else:
                git_range = project['hash']

            # Check out the code.
            subprocess.check_call(
                ['zuul-cloner',
                 '--branch', branch,
                 '--workspace', workdir,
                 'git://git.openstack.org',
                 project['repo'],
                 ]
            )
            header = '%s %s' % (project['repo'], git_range)
            print('\n%s' % header)
            print('-' * len(header))

            # Show the log output.
            log_cmd = [
                'git', 'log', '--no-color',
                '--format=%h %ci %s', '--no-merges',
                git_range,
            ]
            subprocess.check_call(
                log_cmd,
                cwd=os.path.join(workdir, project['repo']),
            )
            print()

    return 0
