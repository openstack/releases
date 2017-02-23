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

"""Import the history for the project

Use git as the canonical source of version numbers.

"""

from __future__ import print_function
from __future__ import unicode_literals

from openstack_releases.versionutils import canonical_version

import argparse
import datetime
import os
import subprocess
import sys

# From https://wiki.openstack.org/wiki/Releases
RELEASES = [
    ('austin', datetime.datetime(2010, 10, 21)),
    ('bexar', datetime.datetime(2011, 2, 3)),
    ('cactus', datetime.datetime(2011, 4, 15)),
    ('diablo', datetime.datetime(2011, 9, 22)),
    ('essex', datetime.datetime(2012, 4, 5)),
    ('folsom', datetime.datetime(2012, 9, 27)),
    ('grizzly', datetime.datetime(2013, 4, 4)),
    ('havana', datetime.datetime(2013, 10, 17)),
    ('icehouse', datetime.datetime(2014, 4, 17)),
    ('juno', datetime.datetime(2014, 10, 16)),
    ('kilo', datetime.datetime(2015, 4, 30)),
    ('liberty', datetime.datetime(2015, 10, 15)),
    ('mitaka', datetime.datetime(2016, 4, 7)),
    ('newton', datetime.datetime(2016, 10, 6)),
    ('ocata', datetime.datetime(2017, 2, 22)),
]


def abort(code, errmsg):
    print(errmsg, file=sys.stderr)
    sys.exit(code)


def date_to_release(tag_date):
    for release, end_date in RELEASES:
        if tag_date <= end_date:
            return release
    return 'UNKNOWN'


# Argument parsing
parser = argparse.ArgumentParser()
parser.add_argument('project', help='launchpad project name')
parser.add_argument('repo', help='repository directory')
parser.add_argument('--release-type', dest='release_type', default='std',
                    help=('Which release-type to use for this deliverable'
                          '(Default: %(default)s)'))
args = parser.parse_args()

before = os.getcwd()
dev_null = open('/dev/null', 'w')
repo = args.repo
series_data = {}

os.chdir(repo)

# Retrieve the existing tags
tags_out = subprocess.check_output(['git', 'tag'])
tags = [t.strip() for t in tags_out.splitlines() if t.strip()]

repo_namespace = os.path.basename(os.path.dirname(repo))
repo_short_name = repo_namespace + '/' + os.path.basename(repo)

for tag in tags:
    if ('-' in tag) or ('rc' in tag) or ('a' in tag) or ('b' in tag):
        print('ignoring %r' % tag)
        continue
    try:
        show_output = subprocess.check_output([
            'git', 'show', '--no-patch', '--pretty=%H %ct', tag,
        ], stderr=dev_null)
        interesting = show_output.rstrip().splitlines()[-1]
        print(tag + ' ' + interesting)
        sha, ignore, datestr = interesting.partition(' ')
        tag_date = datetime.datetime.utcfromtimestamp(float(datestr))
        series_name = date_to_release(tag_date)
    except subprocess.CalledProcessError:
        print('did not find milestone %s tagged for %s' %
              (tag, repo_short_name))
        continue
    the_series = series_data.setdefault(series_name, {})
    the_milestone = the_series.setdefault(tag, [])
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
    filename = '%s/%s.yaml' % (d, os.path.basename(repo))
    print('creating %s' % filename)
    with open(filename, 'w') as f:
        f.write('---\n')
        f.write('launchpad: %s\n' % args.project)
        f.write('team: %s\n' % args.project)
        f.write('release-type: %s\n' % args.release_type)
        f.write('releases:\n')
        milestones_sorted = \
            sorted(milestones.items(),
                   key=lambda x: canonical_version(x[0], args.release_type))
        for milestone, milestone_data in milestones_sorted:
            f.write('  - version: %s\n' % milestone)
            f.write('    projects:\n')
            for repo_short_name, sha in milestone_data:
                f.write('      - repo: %s\n' % repo_short_name)
                f.write('        hash: %s\n' % sha)
