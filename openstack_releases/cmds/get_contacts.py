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

"""Get the PTL and release liaison information.

Grab the PTL and/or Release Liaisons' contact details from the governance repo.
"""

import argparse
import pathlib
import sys

from openstack_governance import governance


class Contact:
    def __init__(self, contact_data):
        self.name = contact_data['name'].strip()
        self.irc = contact_data['irc'].strip()
        self.email = contact_data['email'].strip()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Contact):
            return NotImplemented

        return (
            other.name == self.name and
            other.irc == self.irc and
            other.email == self.email
        )

    def __hash__(self) -> int:
        return hash((self.name, self.irc, self.email))

    def __str__(self):
        return ("Name     : {0.name}\n" +
                "IRC Nick : {0.irc}\n" +
                "Email    : {0.email}").format(self)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('team', nargs='+', help='The team(s) to lookup')
    who_group = parser.add_mutually_exclusive_group()
    who_group.add_argument('--ptl', action='store_true', default=False,
                           help='Find PTL details')
    who_group.add_argument('--liaisons', action='store_true', default=False,
                           help='Find Liaisons details')
    who_group.add_argument('--all', action='store_true', default=False,
                           help='Find both PTL and Liaisons details')
    parser.add_argument('--governance-repo',
                        type=lambda p: pathlib.Path(p).absolute(),
                        help='Path to local governance repo')
    args = parser.parse_args()

    if not (args.ptl or args.liaisons):
        args.all = True

    if args.governance_repo:
        if not args.governance_repo.exists():
            print(f'ERROR: {args.governance_repo} is not a valid directory',
                  file=sys.stderr)
            sys.exit(1)
        gov_data = governance.Governance.from_local_repo(
            str(args.governance_repo))
    else:
        gov_data = governance.Governance.from_remote_repo()

    for team_name in args.team:
        contacts = set()
        if args.ptl or args.all:
            try:
                team_data = gov_data.get_team(team_name)
            except ValueError:
                print('WARNING: Unable to find team [%s] in governance data' %
                      team_name,
                      file=sys.stderr)
            else:
                if team_data.leadership_type == 'ptl':
                    contacts.add(Contact(team_data.ptl))
                else:  # leadership_type == 'distributed'
                    rel_liaisons = team_data.liaisons['release']
                    for liaison in rel_liaisons:
                        contacts.add(Contact(liaison))

        if args.liaisons or args.all:
            for liaison in team_data.liaisons.get('release', []):
                contacts.add(Contact(liaison))

        team_header = '%s Contacts:' % team_name.title()
        print()
        print(team_header)
        print('%s' % ('-' * len(team_header)))
        for contact in contacts:
            print(contact)

    return 0
