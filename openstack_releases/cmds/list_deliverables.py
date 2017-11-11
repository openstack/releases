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
import csv
import operator

import openstack_releases
from openstack_releases import defaults
from openstack_releases import deliverable


def main():
    parser = argparse.ArgumentParser()
    output_mode = parser.add_mutually_exclusive_group()
    output_mode.add_argument(
        '-v', '--verbose',
        action='store_true',
        default=False,
        help='show more than the deliverable name',
    )
    output_mode.add_argument(
        '-r', '--repos',
        action='store_true',
        default=False,
        help='show the repository names not deliverable names',
    )
    parser.add_argument(
        '--group-by',
        dest='group_key',
        default=None,
        choices=['team', 'type', 'model'],
        help='group output by the specified value',
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
    parser.add_argument(
        '--csvfile',
        help='Save results (same as when --verbose) to CSV file',
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
        '--tag',
        default=[],
        action='append',
        help='look for one more more tags on the deliverable or team',
    )
    parser.add_argument(
        '--deliverables-dir',
        default=openstack_releases.deliverable_dir,
        help='location of deliverable files',
    )
    parser.add_argument(
        '--no-stable-branch',
        default=False,
        action='store_true',
        help='limit the list to deliverables without a stable branch',
    )
    grp = parser.add_mutually_exclusive_group()
    grp.add_argument(
        '--unreleased',
        default=False,
        action='store_true',
        help='limit the list to deliverables not released in the cycle',
    )
    grp.add_argument(
        '--missing-milestone',
        help=('deliverables that do not have the specified milestone as '
              'the most current release; for example 2 would look for .0b2 '
              'in the version number (implies --model cycle-with-milestones)'),
    )
    grp.add_argument(
        '--missing-rc',
        action='store_true',
        help=('deliverables that do not have a release candidate, yet '
              '(implies --model cycle-with-milestones)'),
    )
    grp.add_argument(
        '--missing-final',
        action='store_true',
        help='deliverables that have pre-releases but no final releases, yet',
    )
    args = parser.parse_args()

    # Deal with the inconsistency of the name for the independent
    # directory.
    series = args.series
    if series == 'independent':
        series = '_independent'

    if args.missing_milestone:
        model = 'cycle-with-milestones'
        version_ending = '.0b{}'.format(args.missing_milestone)
    elif args.missing_rc:
        model = 'cycle-with-milestones'
        version_ending = None
    elif args.missing_final:
        model = args.model
        version_ending = None
    else:
        model = args.model
        version_ending = None

    verbose_template = '{name:30} {team:20}'
    if not args.unreleased:
        verbose_template += ' {latest_release:15}'
    if not args.type:
        verbose_template += ' {type:15}'
    if not args.model:
        verbose_template += ' {model:15}'
    verbose_template += ' {tags}'

    csvfile = None
    if args.csvfile:
        csvfile = open(args.csvfile, 'w')
        fieldnames = ['name', 'latest_release', 'repo', 'hash',
                      'team', 'type', 'model']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

    all_deliv = deliverable.Deliverables(
        root_dir=args.deliverables_dir,
        collapse_history=False,
    )
    deliv_iter = [
        deliverable.Deliverable(*entry)
        for entry in all_deliv.get_deliverables(args.team, series)
    ]
    if args.group_key:
        deliv_iter = sorted(deliv_iter,
                            key=operator.attrgetter(args.group_key))
        name_fmt = '  {}'
    else:
        name_fmt = '{}'
    cur_group = None
    for deliv in deliv_iter:
        if args.group_key:
            deliv_group = getattr(deliv, args.group_key)

        if args.deliverable and deliv.name != args.deliverable:
            continue

        if model and deliv.model != model:
            continue
        if args.cycle_based and not deliv.is_cycle_based:
            continue
        if args.type and deliv.type != args.type:
            continue
        if args.no_stable_branch:
            if deliv.get_branch_location('stable/' + series) is not None:
                continue
        if args.unreleased and (deliv.versions or not deliv.is_releasable):
            continue
        if version_ending and deliv.latest_release and deliv.latest_release.endswith(version_ending):
            continue
        if args.missing_rc and deliv.latest_release and 'rc' in deliv.latest_release:
            continue
        if args.tag:
            tags = deliv.tags
            for t in args.tag:
                if t not in tags:
                    continue
        tag_str = '(' + ', '.join(deliv.tags) + ')'

        if args.missing_final and deliv.latest_release:
            if not ('rc' in deliv.latest_release or
                    'a' in deliv.latest_release or
                    'b' in deliv.latest_release):
                continue

        if csvfile:
            rel = (deliv.releases or [{}])[-1]
            for prj in rel.get('projects', [{}]):
                writer.writerow({
                    'name': deliv.name,
                    'latest_release': rel.get('version', None),
                    'repo': prj.get('repo', None),
                    'hash': prj.get('hash', None),
                    'team': deliv.team,
                    'type': deliv.type,
                    'model': deliv.model,
                })
        elif args.verbose:
            print(verbose_template.format(
                name=deliv.name,
                latest_release=deliv.latest_release or '',
                team=deliv.team,
                type=deliv.type,
                model=deliv.model,
                tags=tag_str,
            ))
        elif args.repos:
            if args.group_key and cur_group != deliv_group:
                cur_group = deliv_group
                print(cur_group)
            for r in sorted(deliv.repos):
                print(name_fmt.format(r))
        else:
            if args.group_key and cur_group != deliv_group:
                cur_group = deliv_group
                print(cur_group)
            print(name_fmt.format(deliv.name))

    if csvfile:
        csvfile.close()
