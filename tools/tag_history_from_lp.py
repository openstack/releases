#!/usr/bin/env python
#
# Ensure the given milestone exists on Launchpad
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

from __future__ import print_function
from __future__ import unicode_literals

import argparse
import os
import re
import subprocess
import sys

from launchpadlib.launchpad import Launchpad


def abort(code, errmsg):
    print(errmsg, file=sys.stderr)
    sys.exit(code)


# Argument parsing
parser = argparse.ArgumentParser(description='Create milestones on LP')
parser.add_argument('project', help='launchpad project name')
parser.add_argument('repo', nargs='+', help='repository directory')
args = parser.parse_args()

# Connect to LP
print("connecting to launchpad")
try:
    launchpad = Launchpad.login_with('openstack-releasing', 'production')
except Exception, error:
    abort(2, 'Could not connect to Launchpad: ' + str(error))

# Retrieve project
try:
    project = launchpad.projects[args.project]
except KeyError:
    abort(2, '  Could not find project: %s' % args.project)

series_data = {}
BASE_URL = 'http://git.openstack.org/cgit/openstack/%s/tag/?id=%s'
PATTERN = re.compile(r'tag name[^(]*\(([^)]*)\)', re.MULTILINE)

# <tr><td>tag name</td><td>2014.1.5 (44bb894f36c58ba51b6cc64763209f4c97f89206)</td></tr>  # noqa

before = os.getcwd()
dev_null = open('/dev/null', 'w')

for repo in args.repo:
    os.chdir(repo)
    repo_short_name = 'openstack/' + os.path.basename(repo)

    for series in project.series:
        for milestone in series.all_milestones:
            try:
                show_output = subprocess.check_output([
                    'git', 'show', '--no-patch', '--pretty=%H', milestone.name,
                ], stderr=dev_null)
                sha = show_output.rstrip().splitlines()[-1]
            except subprocess.CalledProcessError:
                print('did not find milestone %s tagged for %s' %
                      (milestone.name, repo_short_name))
                continue
            the_series = series_data.setdefault(series.name, {})
            the_milestone = the_series.setdefault(milestone.name, [])
            the_milestone.append(
                (repo_short_name, sha)
            )

os.chdir(before)

for series, milestones in sorted(series_data.items()):
    # print(series, milestones)
    d = 'deliverables/%s' % series
    if not os.path.exists(d):
        print('creating directory %s' % d)
        os.makedirs(d)
    filename = '%s/%s.yaml' % (d, args.project)
    print('creating %s' % filename)
    with open(filename, 'w') as f:
        f.write('---\n')
        f.write('launchpad: %s\n' % args.project)
        f.write('releases:\n')
        for milestone, milestone_data in sorted(milestones.items()):
            f.write('  - version: %s\n' % milestone)
            f.write('    projects:\n')
            for repo_short_name, sha in milestone_data:
                f.write('      - repo: %s\n' % repo_short_name)
                f.write('        hash: %s\n' % sha)
