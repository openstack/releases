#!/usr/bin/python3
#
# List inconsistencies between repositories under governance and
# deliverable files
#
# Copyright 2019 Thierry Carrez <thierry@openstack.org>
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

import argparse
import os.path
import sys
import yaml


TEAM_EXCEPTIONS = [
    'Infrastructure',  # Infra/OpenDev repos escape OpenStack RelMgt
]

DELIVERABLE_EXCEPTIONS = [
    'openstack-governance',  # released for the TC
]


def deliv_in_governance(args):
    deliv = set(DELIVERABLE_EXCEPTIONS)
    with open(args.projects_yaml, 'r') as projects:
        teams = yaml.safe_load(projects)
        for tname, team in teams.items():
            # Skip all deliverables if team is in TEAM_EXCEPTIONS
            if tname in TEAM_EXCEPTIONS:
                continue

            for dname, deliverable in team['deliverables'].items():
                # Skip deliverables if not release-managed by RelMgt team
                if 'release-management' in deliverable:
                    continue
                deliv.add(dname)
    return deliv


def deliv_in_releases(args):
    deliv = set()
    for dirname in [args.series, '_independent']:
        dirpath = os.path.join('./deliverables', dirname)
        for filename in os.listdir(dirpath):
            with open(os.path.join(dirpath, filename), 'r') as deliv_file:
                releases = yaml.safe_load(deliv_file)
            # Skip deliverable if it's abandoned
            if (releases.get('release-model', '') == 'abandoned'):
                continue
            delivname = os.path.splitext(os.path.basename(filename))[0]
            deliv.add(delivname)
    return deliv


def main(args=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'series',
        help='name of the currently-developed series'
    )
    parser.add_argument(
        'projects_yaml',
        help='path to governance reference directory'
    )
    args = parser.parse_args(args)

    print("Defined in governance but not in deliverable files:")
    print(" (excluding deliverables from " + str(TEAM_EXCEPTIONS) + " team(s)")
    print(" and deliverables specifically marked as being externally managed)")
    print()
    delta1 = deliv_in_governance(args) - deliv_in_releases(args)
    for d in sorted(delta1):
        print('- ' + d)

    print()
    print("Defined in deliverable files but not in (active) governance:")
    print()
    delta2 = deliv_in_releases(args) - deliv_in_governance(args)
    for d in sorted(delta2):
        print('- ' + d)


if __name__ == '__main__':
    main()
