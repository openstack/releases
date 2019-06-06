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

import openstack_releases
from openstack_releases import deliverable


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'deliverable',
        help='the name of the deliverable, such as "nova" or "oslo.config"',
    )
    parser.add_argument(
        '--deliverables-dir',
        default=openstack_releases.deliverable_dir,
        help='location of deliverable files',
    )
    parser.add_argument(
        '--file',
        default=False,
        action='store_true',
        help='deliverable arg is a file path rather than a std. deliverable'
    )
    args = parser.parse_args()

    # If we've been told the 'deliverable' is infact a yaml file *or* the
    # deliverable contains a '/' just load that file directly
    if args.file or '/' in args.deliverable:
        deliv = deliverable.Deliverable.read_file(args.deliverable)
    else:
        all_deliv = deliverable.Deliverables(
            root_dir=args.deliverables_dir,
            collapse_history=False,
        )
        deliv = next(all_deliv.get_deliverable_history(args.deliverable))

    print(deliv.team)
