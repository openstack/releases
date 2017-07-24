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
import atexit
import glob
import os.path
import shutil
import tempfile

import yaml

import openstack_releases
from openstack_releases import defaults


BRANCH_TEMPLATE = """
branches:
  - name: stable/{series}
    location: {version}
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--no-cleanup',
        dest='cleanup',
        default=True,
        action='store_false',
        help='do not remove temporary files',
    )
    parser.add_argument(
        '--all',
        default=False,
        action='store_true',
        help='process all deliverables, including release:cycle-trailing',
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        default=False,
        help='produce detailed output',
    )
    parser.add_argument(
        '--deliverables-dir',
        default=openstack_releases.deliverable_dir,
        help='location of deliverable files',
    )
    parser.add_argument(
        '--series',
        default=defaults.RELEASE,
        help='the name of the release series to work on (%(default)s)'
    )
    parser.add_argument(
        'deliverable',
        nargs='*',
        default=[],
        help='the name(s) of the deliverable(s) to modify',
    )
    args = parser.parse_args()

    if args.verbose:
        def verbose(msg):
            print(msg)
    else:
        def verbose(msg):
            pass

    deliverables_dir = args.deliverables_dir

    workdir = tempfile.mkdtemp(prefix='releases-')
    print('creating temporary files in %s' % workdir)

    def cleanup_workdir():
        if args.cleanup:
            try:
                shutil.rmtree(workdir)
            except Exception:
                pass
        else:
            print('not cleaning up %s' % workdir)
    atexit.register(cleanup_workdir)

    pattern = os.path.join(deliverables_dir,
                           args.series, '*.yaml')
    verbose('Scanning {}'.format(pattern))
    deliverable_files = sorted(glob.glob(pattern))

    for filename in deliverable_files:
        deliverable_name = os.path.basename(filename)[:-5]
        if args.deliverable and deliverable_name not in args.deliverable:
            continue
        with open(filename, 'r') as f:
            deliverable_data = yaml.safe_load(f)
        if deliverable_data['type'] != 'library':
            continue
        verbose('\n{}'.format(filename))
        releases = deliverable_data.get('releases')
        if not releases:
            print('{} has no releases, not branching'.format(
                deliverable_name))
            continue
        if 'branches' in deliverable_data:
            print('{} already has branches'.format(deliverable_name))
            continue
        latest_release = releases[-1]

        # NOTE(dhellmann): PyYAML doesn't preserve layout when you
        # write the data back out, so do the formatting ourselves.
        new_block = BRANCH_TEMPLATE.format(
            version=latest_release['version'],
            series=args.series,
        ).strip() + '\n'
        with open(filename, 'a') as f:
            f.write(new_block)
