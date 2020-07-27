#!/usr/bin/python3
#
# Scan the releases for a series that came after the project's branch
# and verify that they are all on the right branch.
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
import shutil
import tempfile

import openstack_releases
from openstack_releases import defaults
from openstack_releases import deliverable
from openstack_releases import gitutils


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        default=False,
        help='show more than the deliverable name',
    )
    parser.add_argument(
        '--team',
        help='the name of the project team, such as "Nova" or "Oslo"',
    )
    parser.add_argument(
        '--deliverable',
        help='the name of the deliverable, such as "nova" or "oslo.config"',
    )
    parser.add_argument(
        '--series',
        default=defaults.RELEASE,
        help='the release series, such as "newton" or "ocata"',
    )
    model = parser.add_mutually_exclusive_group()
    model.add_argument(
        '--model',
        help=('the release model, such as "cycle-with-milestones"'
              ' or "independent"'),
    )
    model.add_argument(
        '--cycle-based',
        action='store_true',
        default=False,
        help='include all cycle-based code repositories',
    )
    parser.add_argument(
        '--type',
        help='deliverable type, such as "library" or "service"',
    )
    parser.add_argument(
        '--deliverables-dir',
        default=openstack_releases.deliverable_dir,
        help='location of deliverable files',
    )
    parser.add_argument(
        '--branch',
        default=None,
        help='branch name, defaults to stable/$series',
    )
    parser.add_argument(
        '--no-cleanup',
        dest='cleanup',
        default=True,
        action='store_false',
        help='do not remove temporary files',
    )
    args = parser.parse_args()

    if args.verbose:
        def verbose(msg):
            print(msg)
    else:
        def verbose(msg):
            pass

    # Deal with the inconsistency of the name for the independent
    # directory.
    series = args.series
    if series == 'independent':
        series = '_independent'

    branch = args.branch
    if not branch:
        branch = 'stable/{}'.format(series)

    workdir = tempfile.mkdtemp(prefix='releases-')
    verbose('creating temporary files in {}'.format(workdir))

    def cleanup_workdir():
        if args.cleanup:
            verbose('cleaning up temporary files in {}'.format(workdir))
            shutil.rmtree(workdir, True)
        else:
            print('not cleaning up {}'.format(workdir))
    atexit.register(cleanup_workdir)

    # Count any errors for our exit code.
    errors = 0

    all_deliv = deliverable.Deliverables(
        root_dir=args.deliverables_dir,
        collapse_history=False,
    )
    for deliv in all_deliv.get_deliverables(args.team, series):
        branch_loc = deliv.get_branch_location(branch)
        if branch_loc is None:
            verbose('No stable branch for {}'.format(deliv.name))
            continue
        all_versions = deliv.versions
        if all_versions[-1] == branch_loc:
            verbose('Most recent release for {} ({}) is at {}'.format(
                deliv.name, branch_loc, branch))
            continue
        idx = all_versions.index(branch_loc)
        late_releases = all_versions[idx + 1:]
        print('{} releases {} come after {}'.format(
            deliv.name, late_releases, branch))
        for repo in sorted(deliv.repos):
            verbose('cloning {}'.format(repo))
            gitutils.clone_repo(
                workdir,
                repo,
            )
            for version in late_releases:
                containing_br = gitutils.branches_containing(
                    workdir,
                    repo,
                    version,
                )
                for cb in containing_br:
                    if branch in cb:  # allow for remote prefix
                        verbose('{} version {} is on branch {}'.format(
                            repo, version, branch))
                        break
                else:
                    print('{} version {} is not on branch {} ({})'.format(
                        repo, version, branch, containing_br))
                    errors += 1

    return (1 if errors else 0)


if __name__ == '__main__':
    main()
