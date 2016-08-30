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

"""Look for releases listed in a series but not actually tagged.

"""

from __future__ import print_function

import argparse
import glob
import os
import os.path

import yaml

# Disable warnings about insecure connections.
from requests.packages import urllib3

from openstack_releases import defaults
from openstack_releases import gitutils

urllib3.disable_warnings()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--series', '-s',
        help='release series to scan',
    )
    parser.add_argument(
        'input',
        nargs='*',
        help=('YAML files to validate, defaults to '
              'files changed in the latest commit'),
    )
    args = parser.parse_args()

    if args.input:
        filenames = args.input
    elif args.series:
        filenames = glob.glob('deliverables/%s/*.yaml' % args.series)
    else:
        filenames = gitutils.find_modified_deliverable_files()
    if not filenames:
        print('no modified deliverable files, validating all releases from %s'
              % defaults.RELEASE)
        filenames = glob.glob('deliverables/' + defaults.RELEASE + '/*.yaml')

    errors = []

    for filename in filenames:
        print('\nChecking %s' % filename)
        if not os.path.exists(filename):
            print("File was deleted, skipping.")
            continue
        with open(filename, 'r') as f:
            deliverable_info = yaml.load(f.read())

        for release in deliverable_info['releases']:

            for project in release['projects']:
                # Report if the version has already been
                # tagged. We expect it to not exist, but neither
                # case is an error because sometimes we want to
                # import history and sometimes we want to make new
                # releases.
                print('%s %s' % (project['repo'], release['version']), end=' ')
                version_exists = gitutils.tag_exists(
                    project['repo'], release['version'],
                )
                if version_exists:
                    print('found')
                else:
                    print('MISSING')
                    errors.append(
                        '%s missing tag %s' % (
                            project['repo'],
                            release['version'],
                        )
                    )

    if errors:
        print('\n\n%s errors found' % len(errors))
        for e in errors:
            print(e)

    return 1 if errors else 0
