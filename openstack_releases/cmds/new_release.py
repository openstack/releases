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
import shutil
import tempfile

from openstack_releases import gitutils

import yaml

RELEASE_TEMPLATE = '''
  - version: {version}
    projects:
'''.lstrip('\n')

PROJECT_TEMPLATE = '''
      - repo: {repo}
        hash: {hash}
'''.lstrip('\n')


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
    deliverable_filename = 'deliverables/%s/%s.yaml' % (
        series, args.deliverable)
    try:
        with open(deliverable_filename, 'r') as f:
            deliverable_info = yaml.safe_load(f)
    except (IOError, OSError) as e:
        parser.error(e)

    # Determine the new version number.
    last_release = deliverable_info['releases'][-1]
    last_version = last_release['version'].split('.')
    increment = {
        'bugfix': (0, 0, 1),
        'feature': (0, 1, 0),
        'major': (1, 0, 0),
    }[args.release_type]
    new_version_parts = []
    for cur, inc in zip(last_version, increment):
        new_version_parts.append(str(int(cur) + inc))
    new_version = '.'.join(new_version_parts)

    print('going from %s to %s' % (last_version, new_version))

    projects = []
    for project in last_release['projects']:
        gitutils.clone_repo(workdir, project['repo'])
        sha = gitutils.sha_for_tag(workdir, project['repo'], 'HEAD')
        projects.append({
            'repo': project['repo'],
            'hash': sha,
        })

    # The YAML dump formatter produces results that aren't very nice
    # to read, so we format the output ourselves.
    with open(deliverable_filename, 'a') as f:
        f.write(RELEASE_TEMPLATE.format(version=new_version))
        for p in projects:
            f.write(PROJECT_TEMPLATE.format(**p))
