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


def get_deliverable_data(series, deliverable):
    deliverable_filename = 'deliverables/%s/%s.yaml' % (
        series, deliverable)
    with open(deliverable_filename, 'r') as f:
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
    parser.add_argument(
        '--release-notes',
        help='the release-notes URL',
    )
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

    changes = 0

    if args.release_notes:
        deliverable_info['release-notes'] = args.release_notes
        changes += 1

    if changes > 0:
        deliverable_filename = 'deliverables/%s/%s.yaml' % (
            series, args.deliverable)
        with open(deliverable_filename, 'w', encoding='utf-8') as f:
            f.write(yamlutils.dumps(deliverable_info))
