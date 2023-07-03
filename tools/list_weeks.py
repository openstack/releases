#!/usr/bin/python3

#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

import argparse
import datetime

from openstack_releases import yamlutils


def mk_entry(name, week, cross_project=None, project_specific=None):
    d = {
        'start': '{:%Y-%m-%d}'.format(week),
        'end': '{:%Y-%m-%d}'.format(week + work_week),
    }
    if name:
        d['name'] = name
    if cross_project:
        d['x-project'] = cross_project
    if project_specific:
        d['project-specific'] = project_specific
    return d


def add_cycle(name):
    return '{}-{}'.format(args.prefix_char, name)


parser = argparse.ArgumentParser()
parser.add_argument(
    'prefix_char',
    help='single letter prefix for tags',
)
parser.add_argument(
    'previous_release',
    help='monday of the week of previous release, YYYY-MM-DD',
)
parser.add_argument(
    'next_release',
    help='monday of the week of upcoming release, YYYY-MM-DD',
)
args = parser.parse_args()


previous_release_date = datetime.datetime.strptime(
    args.previous_release, '%Y-%m-%d')
next_release_date = datetime.datetime.strptime(
    args.next_release, '%Y-%m-%d')

week = datetime.timedelta(weeks=1)
work_week = datetime.timedelta(days=4)

# Build the list of Mondays leading up to the release.
weeks = []
current = previous_release_date
while current < next_release_date:
    current += week
    weeks.append(current)

n_weeks = len(weeks)

cycle = [
    # Print the date for the previous release. The event name will
    # need to be replaced manually with the right name.
    mk_entry('', previous_release_date,
             cross_project=['REPLACE-WITH-PREVIOUS-RELEASE-REF']),
]

for n, w in enumerate(weeks, 1):
    name = 'R{:<+d}'.format(n - n_weeks)
    cross_project = []
    if n == n_weeks:
        cross_project.append(add_cycle('final'))
    cycle.append(mk_entry(name, w, cross_project=cross_project))

data = {
    'start-week': '{:%Y-%m-%d}'.format(weeks[0]),
    'release-week': '{:%Y-%m-%d}'.format(next_release_date),
    'cycle': cycle,
}

print(yamlutils.dumps(data))
