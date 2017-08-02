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

"""Show the most current versions of everything in a given branch.
"""

from __future__ import print_function

import argparse
import glob
import os
import os.path

from openstack_releases import yamlutils


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'series',
        help='the name of the release series to scan',
    )
    args = parser.parse_args()

    filenames = sorted(glob.glob('deliverables/' + args.series + '/*.yaml'))
    if not filenames:
        print('no deliverable files found under {}'.format(args.series))
        return 1

    for filename in filenames:
        with open(filename, 'r', encoding='utf-8') as f:
            deliverable_info = yamlutils.loads(f.read())

        deliverable_name = os.path.splitext(os.path.basename(filename))[0]

        # assume the releases are in order and take the last one
        new_release = deliverable_info['releases'][-1]
        print('{}==={}'.format(deliverable_name, new_release['version']))

    return 0
