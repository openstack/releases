#!/usr/bin/env python
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

"""Try to verify that the latest commit contains valid SHA values.

"""

from __future__ import print_function

import argparse
import subprocess
import sys

import requests
import yaml

# Disable warnings about insecure connections.
from requests.packages import urllib3
urllib3.disable_warnings()

CGIT_TEMPLATE = 'http://git.openstack.org/cgit/%s/commit/?id=%s'

COMMON_NAMES = set([
    'master',
    'HEAD',
    'origin/master',
    'gerrit/master',
])


def find_modified_deliverable_files():
    "Return a list of files modified by the most recent commit."
    results = subprocess.check_output(
        ['git', 'show', '--name-only', '--pretty=format:']
    )
    filenames = [
        l.strip()
        for l in results.splitlines()
        if l.startswith('deliverables/')
    ]
    return filenames


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'input',
        nargs='*',
        help=('YAML files to validate, defaults to '
              'files changed in the latest commit'),
    )
    args = parser.parse_args()

    filenames = args.input or find_modified_deliverable_files()

    num_errors = 0

    for filename in filenames:
        print('\nChecking %s' % filename)
        with open(filename, 'r') as f:
            deliverable_info = yaml.load(f.read())

        # Look for the launchpad project
        try:
            lp_name = deliverable_info['launchpad']
        except KeyError:
            num_errors += 1
            print('no launchpad project name given')
        else:
            print('launchpad project %s ' % lp_name, end='')
            lp_resp = requests.get('https://api.launchpad.net/1.0/' + lp_name)
            if (lp_resp.status_code // 100) == 4:
                print('MISSING')
                num_errors += 1
            else:
                print('found')

        for release in deliverable_info['releases']:
            for project in release['projects']:
                print('%s %s %s ' % (project['repo'],
                                     release['version'],
                                     project['hash']),
                      end='')

                if project['hash'] in COMMON_NAMES:
                    print('NOT A SHA HASH')
                    num_errors += 1
                else:
                    url = CGIT_TEMPLATE % (project['repo'],
                                           project['hash'])
                    response = requests.get(url)
                    missing_commit = (
                        (response.status_code // 100 != 2)
                        or 'Bad object id' in response.text
                    )
                    print('MISSING' if missing_commit else 'found')
                    if missing_commit:
                        num_errors += 1

    return 1 if num_errors else 0


if __name__ == '__main__':
    sys.exit(main())
