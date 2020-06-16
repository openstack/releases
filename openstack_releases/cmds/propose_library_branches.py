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
import atexit
import glob
import os.path
import shutil
import tempfile

import openstack_releases
from openstack_releases import defaults
from openstack_releases import yamlutils


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
        '--include-clients',
        action='append_const',
        const='client-library',
        default=['library'],
        dest='types',
    )
    parser.add_argument(
        '--include-trailing',
        action='append_const',
        const='trailing',
        default=['library'],
        dest='types',
    )
    parser.add_argument(
        '--dry-run', '-n',
        default=False,
        action='store_true',
        help='report what action would be taken but do not take it',
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
    new_branch = 'stable/' + args.series

    for filename in deliverable_files:
        deliverable_name = os.path.basename(filename)[:-5]
        if args.deliverable and deliverable_name not in args.deliverable:
            continue
        with open(filename, 'r', encoding='utf-8') as f:
            deliverable_data = yamlutils.loads(f.read())
        if deliverable_data['type'] not in args.types:
            continue
        if deliverable_data['release-model'] != 'cycle-with-intermediary':
            print('WARNING {} has release model {}, skipping'.format(
                deliverable_name, deliverable_data['release-model']))
            continue
        verbose('\n{}'.format(filename))
        releases = deliverable_data.get('releases')
        if not releases:
            print('{} has no releases, not branching'.format(
                deliverable_name))
            continue
        if 'branches' not in deliverable_data:
            deliverable_data['branches'] = []
        skip = False
        for b in deliverable_data['branches']:
            if b['name'] == new_branch:
                print('{} already has branch {}'.format(
                    deliverable_name, new_branch))
                skip = True
        if skip:
            continue

        latest_release = releases[-1]

        print('{} new branch {} at {}'.format(
            deliverable_name, new_branch, latest_release['version']))
        if not args.dry_run:
            deliverable_data['branches'].append({
                'name': new_branch,
                'location': latest_release['version'],
            })
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(yamlutils.dumps(deliverable_data))
