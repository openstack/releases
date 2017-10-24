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

"""Look for releases listed in a series but not actually tagged.

"""

from __future__ import print_function

import argparse
import glob
import os
import os.path

# Disable warnings about insecure connections.
from requests.packages import urllib3

from openstack_releases import defaults
from openstack_releases import gitutils
from openstack_releases import links
from openstack_releases import yamlutils

urllib3.disable_warnings()


def check_url(type, url):
    if links.link_exists(url):
        print('  found {}'.format(type))
    else:
        print('  did not find {} {}'.format(type, url))
        yield 'missing {} {}'.format(type, url)


def check_signed_file(type, url):
    for item_type, item in [(type, url), (type + ' signature', url + '.asc')]:
        yield from check_url(item_type, item)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--series', '-s',
        help='release series to scan',
    )
    parser.add_argument(
        '--artifacts',
        default=False,
        action='store_true',
        help='only scan the build artifacts',
    )
    parser.add_argument(
        '--all',
        default=False,
        action='store_true',
        help='scan all releases, not just most recent',
    )
    parser.add_argument(
        'input',
        nargs='*',
        help=('YAML files to validate, defaults to '
              'files changed in the latest commit'),
    )
    args = parser.parse_args()

    if args.input:
        filenames = args.input
    elif args.series:
        filenames = sorted(glob.glob('deliverables/%s/*.yaml' % args.series))
    else:
        filenames = sorted(gitutils.find_modified_deliverable_files())
    if not filenames:
        print('no modified deliverable files, validating all releases from %s'
              % defaults.RELEASE)
        filenames = glob.glob('deliverables/' + defaults.RELEASE + '/*.yaml')

    errors = []

    for filename in filenames:
        print('\nChecking %s' % filename)
        if not os.path.exists(filename):
            print("File was deleted, skipping.")
            continue
        with open(filename, 'r', encoding='utf-8') as f:
            deliverable_info = yamlutils.loads(f.read())

        link_mode = deliverable_info.get('artifact-link-mode', 'tarball')

        releases = deliverable_info.get('releases', [])
        if not args.all:
            releases = releases[-1:]

        for release in releases:

            for project in release['projects']:
                # Report if the version has already been
                # tagged. We expect it to not exist, but neither
                # case is an error because sometimes we want to
                # import history and sometimes we want to make new
                # releases.
                print('%s %s' % (project['repo'], release['version']))

                if not args.artifacts:
                    version_exists = gitutils.tag_exists(
                        project['repo'], release['version'],
                    )
                    if version_exists:
                        print('  tag:found')
                    else:
                        print('  tag:MISSING')
                        errors.append('%s missing tag %s' %
                                      (project['repo'], release['version']))

                # Look for the tarball associated with the tag and
                # report if that exists.
                if link_mode == 'tarball':
                    tb_url = links.tarball_url(release['version'], project)
                    errors.extend(check_signed_file('tarball', tb_url))
                    wheel_2_errors = list(
                        check_url(
                            'python 2 wheel',
                            links.wheel_py2_url(release['version'], project)
                        )
                    )
                    wheel_both_errors = list(
                        check_url(
                            'python 2/3 wheel',
                            links.wheel_both_url(release['version'], project)
                        )
                    )
                    # We only expect to find one wheel. Look for both,
                    # and minimize what we report as errors.
                    if wheel_2_errors and wheel_both_errors:
                        # We have neither wheel.
                        errors.extend(wheel_2_errors)
                        errors.extend(wheel_both_errors)
                    elif not wheel_both_errors:
                        # We have the "both" wheel, so check for the
                        # signature file.
                        errors.extend(
                            check_url(
                                'python 2/3 wheel signature',
                                links.wheel_both_url(release['version'],
                                                     project) + '.asc',
                            )
                        )
                    elif not wheel_2_errors:
                        # We have the py2 wheel, so check for the
                        # signature file.
                        errors.extend(
                            check_url(
                                'python 2 wheel signature',
                                links.wheel_py2_url(release['version'],
                                                    project) + '.asc',
                            )
                        )
                print()

    if errors:
        print('\n\n%s errors found' % len(errors))
        for e in errors:
            print(e)

    return 1 if errors else 0
