#!/usr/bin/python3
#
# List deliverables that appear in governance but not in releases
# in preparation for MemberShipFreeze
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


# Infrastructure/OpenDev repositories escape OpenStack release management
TEAM_EXCEPTIONS = ['Infrastructure']


def deliverable_filename(deliverable, series):
    return os.path.join('./deliverables', series, deliverable + '.yaml')


def in_governance_but_not_released(args):
    missing = []
    dirs = [args.series, '_independent']

    with open(args.projects_yaml, 'r') as projects:
        teams = yaml.safe_load(projects)
        for tname, team in teams.items():
            if tname in TEAM_EXCEPTIONS:
                continue

            for dname, deliverable in team['deliverables'].items():
                if 'release-management' in deliverable:
                    continue
                for fname in [deliverable_filename(dname, s) for s in dirs]:
                    if os.path.isfile(fname):
                        break
                else:
                    url = ''
                    if len(deliverable['repos']) == 1:
                        url = deliverable['repos'][0]
                    missing.append((tname, dname, url))
    return missing


def main(args=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'series',
        help='name of the currently-developed series'
    )
    parser.add_argument(
        'projects_yaml',
        help='path to governance projects.yaml file'
    )
    parser.add_argument(
        '--yaml',
        action="store_true",
        help='display results to yaml format'
    )
    parser.add_argument(
        '--url',
        action='store_true',
        help='generate url for the given results found'
    )
    parser.add_argument(
        '--distgit',
        default='https://git.openstack.org/cgit/',
        required=False,
        help='deliverable git repository url to use'
    )
    args = parser.parse_args(args)
    last_team = ''
    missing = in_governance_but_not_released(args)
    for team, deliverable, url in missing:
        if last_team != team:
            print('\n' + team + ':')
            last_team = team
        output_format = "- " if args.yaml else ""
        output = "{}{}".format(output_format, deliverable)
        if args.url:
            output = "{} ({}{})".format(output, args.distgit, url)
        print(output)

    if missing:
        print("-" * 50)
        print("{} project(s) missing".format(len(missing)))
        print("-" * 50)


if __name__ == '__main__':
    main()
