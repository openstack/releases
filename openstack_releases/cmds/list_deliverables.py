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
import csv
import operator
import requests

import openstack_releases
from openstack_releases import defaults
from openstack_releases import deliverable
from openstack_releases import schema


def main():
    deliverable_schema = schema.Schema()

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
    output_mode.add_argument(
        '-a', '--all-releases',
        action='store_true',
        default=False,
        help='show all of the releases for each deliverable',
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
    parser.add_argument(
        '--show-dates',
        action='store_true',
        default=False,
        help='Show last release date (in verbose mode)',
    )
    parser.add_argument(
        '--show-tags',
        action='store_true',
        default=False,
        help='Show tags associated with deliverable (in verbose mode)',
    )
    model = parser.add_mutually_exclusive_group()
    model.add_argument(
        '--model',
        help=('the release model, such as "cycle-with-rc"'
              ' or "independent"'),
        choices=sorted(deliverable_schema.release_models + ['independent']),
    )
    model.add_argument(
        '--cycle-based',
        action='store_true',
        default=False,
        help='include all cycle-based deliverables',
    )
    model.add_argument(
        '--cycle-based-no-trailing',
        action='store_true',
        default=False,
        help='include all cycle-based deliverables, except trailing ones',
    )
    parser.add_argument(
        '--type',
        default=[],
        action='append',
        choices=sorted(deliverable_schema.release_types),
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
        '--unreleased-since',
        help=('limit the list to deliverables not released in the cycle '
              'since a given YYYY-MM-DD date'),
    )
    grp.add_argument(
        '--missing-rc',
        action='store_true',
        help=('deliverables that do not have a release candidate, yet '
              '(implies --model cycle-with-rc)'),
    )
    grp.add_argument(
        '--is-eol',
        action='store_true',
        help='limit the list to deliverables EOL in the cycle',
    )
    grp.add_argument(
        '--missing-final',
        action='store_true',
        help='deliverables that have pre-releases but no final releases, yet',
    )
    grp.add_argument(
        '--forced',
        action='store_true',
        help=('releases that have the "forced" flag applied '
              '(implies --all-releases)'),
    )
    args = parser.parse_args()

    series = args.series
    GET_REFS_API = 'https://opendev.org/api/v1/repos/{}/git/{}'
    GET_COMMIT_API = 'https://opendev.org/api/v1/repos/{}/git/commits/{}'

    if args.missing_rc:
        model = 'cycle-with-rc'
        version_ending = None
    elif args.missing_final:
        model = args.model
        version_ending = None
    else:
        model = args.model
        version_ending = None

    if args.unreleased_since:
        args.show_dates = True

    verbose_template = '{name:30} {team:20}'
    if not args.unreleased:
        verbose_template += ' {latest_release:12}'
    if args.show_dates:
        verbose_template += ' {last_release_date:11}'
    if len(args.type) != 1:
        verbose_template += ' {type:15}'
    if not args.model:
        verbose_template += ' {model:15}'
    if args.show_tags:
        verbose_template += ' {tags}'

    if args.forced:
        args.all_releases = True

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
    deliv_iter = list(all_deliv.get_deliverables(args.team, series))
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
        if args.cycle_based_no_trailing and (not deliv.is_cycle_based or
                                             deliv.type == 'trailing'):
            continue
        if args.type and deliv.type not in args.type:
            continue
        if args.no_stable_branch:
            if deliv.is_branchless:
                continue
            if deliv.name == 'release-test':
                continue
            if deliv.stable_branch_type is None:
                continue
            if deliv.get_branch_location('stable/' + series) is not None:
                continue
        if args.unreleased and (deliv.is_released or not deliv.is_releasable):
            continue
        if args.is_eol and 'eol' not in deliv.latest_release:
            continue
        if version_ending and deliv.is_released:
            found = False
            for release in deliv.releases:
                if release.version.endswith(version_ending):
                    found = True
                    break
            if found:
                continue
        if args.missing_rc and deliv.is_released and 'rc' in deliv.latest_release:
            continue
        if args.tag:
            tags = deliv.tags
            ignore = False
            for t in args.tag:
                if t not in tags:
                    ignore = True
                    break
            if ignore:
                continue

        tag_str = '(' + ', '.join(deliv.tags) + ')'

        if args.missing_final and deliv.latest_release:
            if not ('rc' in deliv.latest_release or
                    'a' in deliv.latest_release or
                    'b' in deliv.latest_release):
                continue

        release_date = {}
        if (args.show_dates or args.unreleased_since) and deliv.is_released:
            if args.all_releases:
                versions = [a.version for a in deliv.releases]
            else:
                versions = [deliv.releases[-1].version]
            for ver in versions:
                ref = "refs/tags/{}".format(ver)
                api = GET_REFS_API.format(deliv.repos[0], ref)
                tagsjson = requests.get(api).json()

                # Gitea returns either a single tag object, or a list of
                # tag objects containing the provided string. So we need to
                # filter the list for the exact match.
                if isinstance(tagsjson, list):
                    for release_tag in tagsjson:
                        if release_tag['ref'] == ref:
                            break
                else:
                    release_tag = tagsjson

                release_sha = release_tag['object']['sha']
                api = GET_COMMIT_API.format(deliv.repos[0], release_sha)
                release_commit = requests.get(api).json()['commit']
                release_date[ver] = release_commit['author']['date'][0:10]

        if args.unreleased_since and deliv.is_released:
            if release_date[ver] >= args.unreleased_since:
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
        elif args.all_releases:
            for r in deliv.releases:
                if args.forced and not r.was_forced:
                    continue
                print(verbose_template.format(
                    name=deliv.name,
                    latest_release=r.version,
                    last_release_date=release_date.get(r.version, ''),
                    team=deliv.team,
                    type=deliv.type,
                    model=deliv.model,
                    tags=tag_str,
                ))
        elif args.verbose:
            print(verbose_template.format(
                name=deliv.name,
                latest_release=deliv.latest_release or '',
                last_release_date=release_date.get(deliv.latest_release, ''),
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
