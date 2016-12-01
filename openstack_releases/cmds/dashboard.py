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

import argparse
import csv
import sys

import openstack_releases
from openstack_releases import defaults
from openstack_releases import deliverable
from openstack_releases import governance

MILESTONE = 'cycle-with-milestones'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--deliverables-dir',
        default=openstack_releases.deliverable_dir,
        help='location of deliverable files',
    )
    parser.add_argument(
        '--series',
        default=defaults.RELEASE,
        help='the release series, such as "newton" or "ocata"',
    )
    args = parser.parse_args()

    all_deliv = deliverable.Deliverables(
        root_dir=args.deliverables_dir,
        collapse_history=False,
    )

    interesting_deliverables = [
        d
        for d in (deliverable.Deliverable(t, s, dn, da)
                  for t, s, dn, da in
                  all_deliv.get_deliverables(None, args.series))
        if d.model == MILESTONE
    ]

    team_data = governance.get_team_data()
    teams = {
        n.lower(): governance.Team(n, i)
        for n, i in team_data.items()
    }

    # Dump the dashboard data
    writer = csv.writer(sys.stdout)
    writer.writerow(
        ('Team',
         'Deliverable Type',
         'Deliverable Name',
         'Pre-RC1',
         'RC1',
         'Branched at',
         'Latest RC',
         'Release Notes',
         'Comments',
         'PTL Nick',
         'PTL Email',
         'IRC Channel')
    )

    for deliv in sorted(interesting_deliverables,
                        key=lambda x: (x.team, x.name)):
        team = teams[d.team.lower()]
        writer.writerow(
            (deliv.team.lower(),
             deliv.type,
             deliv.name,
             deliv.latest_release,
             '',  # RC1
             deliv.get_branch_location('stable/' + args.series),  # branched at
             '',  # latest RC
             deliv.release_notes,
             '',  # Comments
             team.data['ptl']['irc'],
             team.data['ptl']['email'],
             team.data.get('irc-channel'))
        )
