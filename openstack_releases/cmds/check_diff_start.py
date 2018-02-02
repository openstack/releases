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

"""Compare diff-start values to the base of branches.

"""

from __future__ import print_function

import argparse
import atexit
import glob
import os
import os.path
import shutil
import tempfile

# Disable warnings about insecure connections.
from requests.packages import urllib3

from openstack_releases import defaults
from openstack_releases import gitutils
from openstack_releases import yamlutils

urllib3.disable_warnings()


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
        'prev_series',
        help='previous series name',
    )
    parser.add_argument(
        'input',
        nargs='*',
        help=('YAML files to examine, defaults to '
              'files changed in the latest commit'),
    )
    args = parser.parse_args()

    filenames = args.input or gitutils.find_modified_deliverable_files()
    if not filenames:
        print('no modified deliverable files, validating all releases from %s'
              % defaults.RELEASE)
        filenames = glob.glob('deliverables/' + defaults.RELEASE + '/*.yaml')

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

    for filename in filenames:
        print('\nChecking %s' % filename)
        if not os.path.isfile(filename):
            print("File was deleted, skipping.")
            continue
        with open(filename, 'r') as f:
            deliverable_info = yamlutils.loads(f.read())

        branch = 'stable/' + args.prev_series

        if not deliverable_info.get('releases'):
            print('  no releases')
            continue

        # assume the releases are in order and take the last one
        new_release = deliverable_info['releases'][-1]
        print('version {}'.format(new_release['version']))

        diff_start = new_release.get('diff-start')
        if not diff_start:
            print('  no diff-start')
            continue
        else:
            print('  diff-start: {!r}'.format(diff_start))

        for project in new_release['projects']:
            gitutils.clone_repo(workdir, project['repo'])

            branch_base = gitutils.get_branch_base(
                workdir, project['repo'], branch,
            )
            if branch_base:
                branch_version = gitutils.get_latest_tag(
                    workdir, project['repo'], branch_base,
                )
                if diff_start == branch_version:
                    print('  SAME')
                else:
                    print('  DIFFERENT {} at {}'.format(
                        branch_version, branch_base))
