#!/usr/bin/env python

from __future__ import print_function

import argparse
import datetime


parser = argparse.ArgumentParser()
parser.add_argument(
    'previous_release',
    help='date of previous release, YYYY-MM-DD',
)
parser.add_argument(
    'next_release',
    help='date of upcoming release, YYYY-MM-DD',
)
parser.add_argument(
    'summit',
    help='date of upcoming summit after the release, YYYY-MM-DD',
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

print('''
+-------------------+---------------------------+-----------------------------+
| Week              | Cross-project events      | Project-specific events     |
+============+======+===========================+=============================+
''', end='')

week_fmt = '''
| {:<10} | {:<4} |{:<27}|{:<29}|
+------------+------+---------------------------+-----------------------------+
'''.strip()


def show_week(week, name):
    date_range = '{:%b %d}-{:%d}'.format(
        week,
        week + work_week,
    )
    print(week_fmt.format(date_range, name, '', ''))


# Print the date for the previous release
show_week(previous_release_date, '')

for n, week in enumerate(weeks, 1):
    show_week(week, 'R{:<+3d}'.format(n - n_weeks))
