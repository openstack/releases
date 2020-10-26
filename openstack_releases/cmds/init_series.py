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

import openstack_releases
from openstack_releases import deliverable
from openstack_releases import yamlutils

IGNORE = [
    'releases',
    'branches',
    'release-notes',
    'cycle-highlights',
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'old_series',
        help='the previous release series, such as "newton"',
    )
    parser.add_argument(
        'new_series',
        help='the new release series, such as "ocata"',
    )
    parser.add_argument(
        '--deliverables-dir',
        default=openstack_releases.deliverable_dir,
        help='location of deliverable files',
    )
    args = parser.parse_args()

    all_deliv = deliverable.Deliverables(
        root_dir=args.deliverables_dir,
        collapse_history=False,
    )

    new_deliverables = set(
        deliv.name
        for deliv in
        all_deliv.get_deliverables(None, args.new_series)
    )

    outdir = os.path.join(args.deliverables_dir, args.new_series)
    if not os.path.exists(outdir):
        print('creating output directory {}'.format(outdir))
        os.mkdir(outdir)

    warn = '# Note: deliverable was not released in %s\n' % args.old_series
    old_deliverables = all_deliv.get_deliverables(None, args.old_series)
    for deliv in old_deliverables:
        if deliv.name in new_deliverables:
            continue
        # Clean up some series-specific data that should not be copied
        # over.
        raw_data = deliv.data
        for key in IGNORE:
            if key in raw_data:
                del raw_data[key]
        outfilename = os.path.abspath(
            os.path.join(outdir, deliv.name + '.yaml')
        )
        with open(outfilename, 'w', encoding='utf-8') as f:
            print('{} created'.format(outfilename))
            f.write(yamlutils.dumps(raw_data))
            if (not deliv.is_released and not deliv.branches and
                    deliv.type != 'trailing'):
                # There were no releases for the deliverable in the
                # previous series, add a comment in the file.
                f.write(warn)
