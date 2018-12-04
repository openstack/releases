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
import os

from openstack_releases import release_notes


def main():
    parser = argparse.ArgumentParser(
        prog='release_notes',
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("repo", metavar='path', action="store",
                        help="repository directory, for example"
                             " 'openstack/cliff'",
                        )
    parser.add_argument('repo_name', action='store',
                        help='The name of the repository being released',
                        )
    parser.add_argument("start_revision", metavar='revision',
                        action="store",
                        help="start revision, for example '1.8.0'",
                        )
    parser.add_argument("end_revision", metavar='revision',
                        action="store",
                        nargs='?',
                        help="end revision, for example '1.9.0'"
                             " (default: HEAD)",
                        default="HEAD")
    parser.add_argument('--changes-only',
                        action='store_true',
                        default=False,
                        help='List only the change summary, without details',
                        )
    parser.add_argument('--include-pypi-link',
                        action='store_true',
                        default=False,
                        help='include a pypi hyperlink for the library',
                        )
    parser.add_argument('--first-release',
                        action='store_true',
                        default=False,
                        help='this is the first release of the project',
                        )
    parser.add_argument("--skip-requirement-merges",
                        action='store_true', default=False,
                        help="skip requirement update commit messages"
                             " (default: False)")
    parser.add_argument("--show-dates",
                        action='store_true', default=False,
                        help="show dates in the change log")
    parser.add_argument("--series", "-s",
                        default="",
                        help="release series name, such as 'kilo'",
                        )
    parser.add_argument("--stable",
                        default=False,
                        action='store_true',
                        help="this is a stable release",
                        )
    parser.add_argument('--description',
                        action='store',
                        help=('A brief description for the repository being '
                              'released'),
                        )
    parser.add_argument('--publishing-dir-name',
                        action='store',
                        help=('The directory on tarballs.openstack.org '
                              'and docs.openstack.org containing the '
                              'published artifacts for this package'),
                        )

    email_group = parser.add_argument_group('email settings')
    email_group.add_argument(
        "--email", "-e",
        action='store_true', default=False,
        help="output a fully formed email message",
    )
    email_group.add_argument(
        "--email-reply-to",
        default="openstack-discuss@lists.openstack.org",
        help="follow-up for discussions, defaults to %(default)s",
    )
    email_group.add_argument(
        "--email-from", "--from",
        default=os.environ.get('EMAIL', ''),
        help="source of the email, defaults to $EMAIL",
    )
    email_group.add_argument(
        "--email-tags",
        default="",
        help="extra topic tags for email subject, e.g. '[oslo]'",
    )
    args = parser.parse_args()

    repo_path = os.path.abspath(args.repo)

    notes = release_notes.generate_release_notes(
        repo=args.repo,
        repo_path=repo_path,
        start_revision=args.start_revision,
        end_revision=args.end_revision,
        show_dates=args.show_dates,
        skip_requirement_merges=args.skip_requirement_merges,
        is_stable=args.stable,
        series=args.series,
        email=args.email,
        email_from=args.email_from,
        email_reply_to=args.email_reply_to,
        email_tags=args.email_tags,
        include_pypi_link=args.include_pypi_link,
        changes_only=args.changes_only,
        first_release=args.first_release,
        repo_name=args.repo_name,
        description=args.description,
        publishing_dir_name=args.publishing_dir_name or args.repo_name,
    )
    print(notes)
    return 0
