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
import os
import shutil
import tempfile

from openstack_releases import gitutils
from openstack_releases import yamlutils


def get_deliverable_data(series, deliverable):
    deliverable_filename = 'deliverables/%s/%s.yaml' % (
        series, deliverable)
    with open(deliverable_filename, 'r', encoding='utf-8') as f:
        return yamlutils.loads(f.read())


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
    # FIXME(dhellmann): Add milestone and rc types.
    parser.add_argument(
        'release_type',
        choices=('bugfix', 'feature', 'major'),
        help='the type of release to generate',
    )
    parser.add_argument(
        '--no-cleanup',
        dest='cleanup',
        default=True,
        action='store_false',
        help='do not remove temporary files',
    )
    args = parser.parse_args()

    workdir = tempfile.mkdtemp(prefix='releases-')
    print('creating temporary files in %s' % workdir)

    def cleanup_workdir():
        if args.cleanup:
            try:
                shutil.rmtree(workdir)
            except:
                pass
        else:
            print('not cleaning up %s' % workdir)
    atexit.register(cleanup_workdir)

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

    # Determine the new version number.
    try:
        last_release = deliverable_info['releases'][-1]
    except KeyError:
        print('No releases for %s in %s, yet.' % (
            args.deliverable, series))
        if args.release_type == 'bugfix':
            parser.error(
                'The first release for a series must '
                'be at least a feature release to allow '
                'for stable releases from the previous series.')
        # Look for the version of the previous series.
        all_series = sorted(os.listdir('deliverables'))
        prev_series = all_series[all_series.index(series) - 1]
        try:
            prev_info = get_deliverable_data(
                prev_series, args.deliverable)
            last_release = prev_info['releases'][-1]
            deliverable_info['releases'] = []
        except (IOError, OSError, KeyError) as e:
            parser.error('Could not determine previous version: %s' % (e,))
    last_version = last_release['version'].split('.')
    increment = {
        'bugfix': (0, 0, 1),
        'feature': (0, 1, 0),
        'major': (1, 0, 0),
    }[args.release_type]
    new_version_parts = []
    clear = False
    for cur, inc in zip(last_version, increment):
        if clear:
            new_version_parts.append('0')
        else:
            new_version_parts.append(str(int(cur) + inc))
            if inc:
                clear = True
    new_version = '.'.join(new_version_parts)

    print('going from %s to %s' % (last_version, new_version))

    projects = []
    changes = 0
    for project in last_release['projects']:
        gitutils.clone_repo(workdir, project['repo'])

        branches = gitutils.get_branches(workdir, project['repo'])
        version = 'origin/stable/%s' % series
        if not any(branch for branch in branches
                   if branch.endswith(version)):
            version = 'master'

        sha = gitutils.sha_for_tag(workdir, project['repo'], version)
        if project['hash'] != sha:
            changes += 1
            print('advancing %s from %s to %s' % (project['repo'],
                                                  project['hash'],
                                                  sha))
            projects.append({
                'repo': project['repo'],
                'hash': sha,
            })

    deliverable_info['releases'].append({
        'version': new_version,
        'projects': projects,
    })

    if changes > 0:
        deliverable_filename = 'deliverables/%s/%s.yaml' % (
            series, args.deliverable)
        with open(deliverable_filename, 'w', encoding='utf-8') as f:
            f.write(yamlutils.dumps(deliverable_info))
