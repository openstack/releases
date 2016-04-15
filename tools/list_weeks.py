#!/usr/bin/env python

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
parser.add_argument(
    'summit',
    help='monday of the week of upcoming summit after the release, YYYY-MM-DD',
)
args = parser.parse_args()


previous_release_date = datetime.datetime.strptime(
    args.previous_release, '%Y-%m-%d')
next_release_date = datetime.datetime.strptime(
    args.next_release, '%Y-%m-%d')
summit_date = datetime.datetime.strptime(
    args.summit, '%Y-%m-%d')

week = datetime.timedelta(weeks=1)
work_week = datetime.timedelta(days=4)

# Build the list of Mondays leading up to the release.
weeks = []
current = previous_release_date
while current < next_release_date:
    current += week
    weeks.append(current)

n_weeks = len(weeks)

# Add the list of Mondays following the release leading up to the
# summit. Increment current before entering the loop because we've
# already used that week.
current += week
while current <= summit_date:
    weeks.append(current)
    current += week

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
