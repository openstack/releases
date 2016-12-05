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

import openstack_releases
from openstack_releases import defaults
from openstack_releases import deliverable


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--team',
        help='the name of the project team, such as "Nova" or "Oslo"',
    )
    parser.add_argument(
        '--deliverable',
        help='the name of the deliverable, such as "nova" or "oslo.config"',
    )
    parser.add_argument(
        '--series',
        default=defaults.RELEASE,
        help='the release series, such as "newton" or "ocata"',
    )
    model = parser.add_mutually_exclusive_group()
    model.add_argument(
        '--model',
        help=('the release model, such as "cycle-with-milestones"'
              ' or "independent"'),
    )
    model.add_argument(
        '--cycle-based',
        action='store_true',
        default=False,
        help='include all cycle-based code repositories',
    )
    parser.add_argument(
        '--type',
        help='deliverable type, such as "library" or "service"',
    )
    parser.add_argument(
        '--deliverables-dir',
        default=openstack_releases.deliverable_dir,
        help='location of deliverable files',
    )
    parser.add_argument(
        '--no-stable-branch',
        default=False,
        action='store_true',
        help='limit the list to deliverables without a stable branch',
    )
    args = parser.parse_args()

    # Deal with the inconsistency of the name for the independent
    # directory.
    series = args.series
    if series == 'independent':
        series = '_independent'

    all_deliv = deliverable.Deliverables(
        root_dir=args.deliverables_dir,
        collapse_history=False,
    )
    for entry in all_deliv.get_deliverables(args.team, series):
        deliv = deliverable.Deliverable(*entry)

        if args.model and deliv.model != args.model:
            continue
        if args.cycle_based and not deliv.is_cycle_based:
            continue
        if args.type and deliv.type != args.type:
            continue
        if args.no_stable_branch:
            if deliv.get_branch_location('stable/' + series) is not None:
                continue

        print(deliv.name)
