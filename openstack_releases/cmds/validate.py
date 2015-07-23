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
import glob
import re

import requests
import yaml

# Disable warnings about insecure connections.
from requests.packages import urllib3
urllib3.disable_warnings()

from openstack_releases import gitutils


DEFAULT_RELEASE = 'liberty'


def is_a_hash(val):
    "Return bool indicating if val looks like a valid hash."
    return re.search('^[a-f0-9]{40}$', val, re.I) is not None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'input',
        nargs='*',
        help=('YAML files to validate, defaults to '
              'files changed in the latest commit'),
    )
    args = parser.parse_args()

    filenames = args.input or gitutils.find_modified_deliverable_files()
    if not filenames:
        print('no modified deliverable files, validating all releases from %s'
              % DEFAULT_RELEASE)
        filenames = glob.glob('deliverables/' + DEFAULT_RELEASE + '/*.yaml')

    errors = []

    for filename in filenames:
        print('\nChecking %s' % filename)
        with open(filename, 'r') as f:
            deliverable_info = yaml.load(f.read())

        # Look for the launchpad project
        try:
            lp_name = deliverable_info['launchpad']
        except KeyError:
            errors.append('No launchpad project given in %s' % filename)
            print('no launchpad project name given')
        else:
            print('launchpad project %s ' % lp_name, end='')
            lp_resp = requests.get('https://api.launchpad.net/1.0/' + lp_name)
            if (lp_resp.status_code // 100) == 4:
                print('MISSING')
                errors.append('Launchpad project %s does not exist' % lp_name)
            else:
                print('found')

        for release in deliverable_info['releases']:
            for project in release['projects']:
                print('%s %s %s ' % (project['repo'],
                                     release['version'],
                                     project['hash']),
                      end='')

                if not is_a_hash(project['hash']):
                    print('NOT A SHA HASH')
                    errors.append(
                        ('%(repo)s version %(version)s release from '
                         '%(hash)r, which is not a hash') % project
                    )
                else:
                    exists = gitutils.commit_has_merged(
                        project['repo'], project['hash'],
                    )
                    if not exists:
                        print('MISSING')
                        errors.append('No commit %(hash)r in %(repo)r'
                                      % project)
                    else:
                        print('found')

    if errors:
        print('\n%s errors found' % len(errors))
        for e in errors:
            print(e)

    return 1 if errors else 0
