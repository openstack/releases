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

from openstack_releases import yamlutils

import yaml


def release_notes(args, series, deliverable_info):
    deliverable_info['release-notes'] = args.url


def stable_branch(args, series, deliverable_info):
    name = 'stable/{}'.format(series)
    for b in deliverable_info.get('branches', []):
        if b['name'] == name:
            return
    new_branch = {
        'name': name,
        'location': args.location,
    }
    deliverable_info.setdefault('branches', []).append(new_branch)


def get_deliverable_data(series, deliverable):
    deliverable_filename = 'deliverables/%s/%s.yaml' % (
        series, deliverable)
    with open(deliverable_filename, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'series',
        help='the name of the release series to scan',
    )
    parser.add_argument(
        'deliverable',
        help='the base name of the deliverable file',
    )
    subparsers = parser.add_subparsers(help='commands')

    relnote_parser = subparsers.add_parser(
        'set-release-notes',
        help='set the release-notes field',
    )
    relnote_parser.add_argument(
        'url',
        help='the release-notes URL',
    )
    relnote_parser.set_defaults(func=release_notes)

    stable_branch_parser = subparsers.add_parser(
        'add-stable-branch',
        help='add a branch',
    )
    stable_branch_parser.add_argument(
        'location',
        help='version number',
    )
    stable_branch_parser.set_defaults(func=stable_branch)

    args = parser.parse_args()

    # Allow for independent projects.
    series = args.series
    if series.lstrip('_') == 'independent':
        series = '_independent'

    # Load existing deliverable data.
    try:
        deliverable_info = get_deliverable_data(
            series, args.deliverable)
    except (IOError, OSError) as e:
        parser.error(e)

    args.func(args, series, deliverable_info)

    deliverable_filename = 'deliverables/%s/%s.yaml' % (
        series, args.deliverable)
    with open(deliverable_filename, 'w', encoding='utf-8') as f:
        f.write(yamlutils.dumps(deliverable_info))
