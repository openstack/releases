#!/usr/bin/env python

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

from __future__ import print_function

import argparse
import datetime


parser = argparse.ArgumentParser()
parser.add_argument(
    '--etherpad',
    default=False,
    action='store_true',
    help='output in etherpad format for building the release planning doc',
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

# Add weeks for the cycle-trailing deadline.
for i in range(2):
    current += week
    weeks.append(current)

HEADER = '''
+-------------------+---------------------------+-----------------------------+
| Week              | Cross-project events      | Project-specific events     |
+============+======+===========================+=============================+
'''

if not args.etherpad:
    print(HEADER, end='')

TABLE_FORMAT = '''
| {:<10} | {:<4} |{:<27}|{:<29}|
+------------+------+---------------------------+-----------------------------+
'''.strip()

ETHERPAD_FORMAT = '{} ({})'


def show_week(week, name):
    date_range = '{:%b %d}-{:%d}'.format(
        week,
        week + work_week,
    )
    if not args.etherpad:
        print(TABLE_FORMAT.format(date_range, name, '', ''))
    else:
        print(ETHERPAD_FORMAT.format(name, date_range))


# Print the date for the previous release
show_week(previous_release_date, '')

for n, week in enumerate(weeks, 1):
    show_week(week, 'R{:<+3d}'.format(n - n_weeks))
