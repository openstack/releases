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

Grab the PTL's contact details from the governance repo; and Liaisons
data from release_liaisons.yaml
"""

import argparse
import sys

from openstack_governance import governance

from openstack_releases import liaisons


class Contact(object):
    def __init__(self, contact_data):
        self.name = contact_data['name']
        self.irc = contact_data['irc']
        self.email = contact_data['email']


def print_contact(contact):
    print('Name     : %s' % contact.name)
    print('IRC Nick : %s' % contact.irc)
    print('Email    : %s' % contact.email)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('team', nargs='+', help='The team(s) to lookup')
    who_group = parser.add_mutually_exclusive_group()
    who_group.add_argument('--ptl', action='store_true', default=False,
                           help='Find PTL details')
    who_group.add_argument('--liaisons', action='store_true', default=False,
                           help='Find Liaisons details')
    who_group.add_argument('--all', action='store_true', default=True,
                           help='Find Liaisons details')
    args = parser.parse_args()

    gov_data = governance.Governance.from_remote_repo()
    liaison_data = liaisons.get_liaisons()

    for team_name in args.team:
        contacts = set()
        if args.ptl or args.all:
            team_data = gov_data.get_team(team_name)
            if not team_data:
                print('Unable to find team [%s] in governance data' %
                      (args.team),
                      file=sys.stderr)
                return 1

            contacts.add(Contact(team_data.ptl))

        if args.liaisons or args.all:
            for liaison in liaison_data.get(team_name.lower(), []):
                contacts.add(Contact(liaison))

        team_header = '%s Contacts:' % team_name.title()
        print()
        print(team_header)
        print('%s' % ('-' * len(team_header)))
        for contact in contacts:
            print_contact(contact)

    return 0
