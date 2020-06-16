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
import logging
import os.path
import re
import shutil
import sys
import tempfile

import openstack_releases
from openstack_releases import deliverable
from openstack_releases import gitutils
from openstack_releases import yamlutils

PRE_RELEASE = re.compile('(a|b|rc)')


def get_prior_branch_point(workdir, repo, branch):
    """Return the tag of the base of the branch.

    The diff-start is the old version is the tag on the commit where
    we created the branch. To determine that, we need to clone the
    repo and look at the branch.

    See
    http://lists.openstack.org/pipermail/openstack-dev/2016-October/104901.html
    for a better description of what the desired tag info is.

    """
    gitutils.clone_repo(workdir, repo)
    branch_base = gitutils.get_branch_base(
        workdir, repo, branch,
    )
    if branch_base:
        return gitutils.get_latest_tag(
            workdir, repo, branch_base,
        )
    # Work backwards from the most recent commit looking for the first
    # version that is not a pre-release, and assume that is the
    # previous release on a non-branching repository like for the
    # os-*-config tools.
    start = None
    while True:
        print('  looking for version before {}'.format(start))
        version = gitutils.get_latest_tag(workdir, repo, start)
        if not version:
            return None
        if not PRE_RELEASE.search(version):
            return version
        start = '{}^'.format(version)
    return version


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
        help='process all deliverables, including cycle-trailing ones',
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        default=False,
        help='produce detailed output',
    )
    parser.add_argument(
        '--canary',
        action='store_true',
        default=False,
        help='process only a canary final release on release-test',
    )
    parser.add_argument(
        '--deliverables-dir',
        default=openstack_releases.deliverable_dir,
        help='location of deliverable files',
    )
    parser.add_argument(
        'prior_series',
        help='the name of the previous series',
    )
    parser.add_argument(
        'series',
        help='the name of the release series to work on'
    )
    args = parser.parse_args()

    if args.verbose:
        def verbose(msg):
            print(msg)
    else:
        def verbose(msg):
            pass

    # Set up logging, including making some loggers quiet.
    logging.basicConfig(
        format='%(levelname)7s: %(message)s',
        stream=sys.stdout,
        level=logging.DEBUG if args.verbose else logging.INFO,
    )
    logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)

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

    verbose('Scanning {}/{}'.format(deliverables_dir, args.series))
    all_deliv = deliverable.Deliverables(
        root_dir=args.deliverables_dir,
        collapse_history=False,
    )

    for deliv in all_deliv.get_deliverables(None, args.series):

        if args.canary and deliv.name != "release-test":
            continue

        verbose('\n{} {}'.format(deliv.name, deliv.model))

        if (deliv.model == 'cycle-trailing' or deliv.type == 'trailing'):
            verbose('#  {} is a cycle-trailing project'.format(
                deliv.name))
            if not args.all:
                continue

        if not deliv.releases:
            verbose('#  no releases')
            continue

        latest_release = deliv.releases[-1]
        projects = latest_release.projects
        if not projects:
            verbose('#  no projects in latest release')
            continue
        for pre_rel in ['a', 'b', 'rc']:
            if pre_rel in str(latest_release.version):
                break
        else:  # we did not find any pre_rel
            verbose('#  {} was not a release candidate'.format(
                latest_release.version))
            continue

        # The new version is the same as the latest release version
        # without the pre-release component at the end. Make sure it
        # has 3 sets of digits.
        new_version = '.'.join(
            (latest_release.version.split('.')[:-1] + ['0'])[:3]
        )

        branch = 'stable/{}'.format(args.prior_series)
        diff_start = get_prior_branch_point(
            workdir, projects[0].repo.name, branch,
        )

        deliverable_data = deliv.data
        release_data = {
            'version': new_version,
            'projects': deliv.data['releases'][-1]['projects'],
        }
        if diff_start:
            release_data['diff-start'] = diff_start
        deliverable_data['releases'].append(release_data)
        print('new version for {}: {}'.format(
            deliv.name, new_version))

        filename = os.path.join(deliverables_dir, deliv.filename)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(yamlutils.dumps(deliverable_data))
