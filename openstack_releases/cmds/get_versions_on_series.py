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
import os

from openstack_releases import deliverable


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'series',
        help='the name of the series, such as "wallaby" or "xena"',
    )
    parser.add_argument(
        'deliverable',
        help='the name of the deliverable, such as "nova" or "oslo.config"',
    )
    args = parser.parse_args()

    # If we've been told the 'deliverable' is infact a yaml file *or* the
    # deliverable contains a '/' just load that file directly
    deliv = deliverable.Deliverable.read_file(
        f"{os.getcwd()}/deliverables/{args.series}/{args.deliverable}.yaml")

    if not deliv.releases:
        print("Not yet released")

    for release in deliv.releases:
        print(release.version)
