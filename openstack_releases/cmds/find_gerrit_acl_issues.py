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

"""Look for governed projects that have their tagging ACLs misconfigured.

"""

import argparse
import configparser
import json
import os.path
import urllib

import appdirs
from openstack_governance import governance
import requests
from requests.packages import urllib3

import openstack_releases
from openstack_releases import defaults
from openstack_releases import deliverable

# Disable warnings about insecure connections.
urllib3.disable_warnings()


IGNORED_TEAMS = [
    'Infrastructure',
    'OpenStack Charms',
]

ALLOWED = [
    'library-release',
    'Release Managers',
    'openstack-chef-release',
    'xstatic-release',
    'release-tools-core',
    'releases-core',
]


class GerritClient(object):

    BASE = 'https://review.openstack.org:443/a/'

    def __init__(self, user, password):
        self._user = user
        self._password = password
        self._auth = requests.auth.HTTPDigestAuth(
            self._user,
            self._password,
        )
        self._groups = {}

    def _mk_url(self, api, *args):
        encoded = [
            urllib.parse.quote_plus(a)
            for a in args
        ]
        return self.BASE + api.format(*encoded)

    def _get(self, url):
        response = requests.get(url, auth=self._auth)
        if response.status_code == 404:
            raise ValueError(404)

        # strip off first few chars because 'the JSON response body starts with
        # a magic prefix line that must be stripped before feeding the rest of
        # the response body to a JSON parser'
        # https://review.openstack.org/Documentation/rest-api.html
        # print(response.text)
        return json.loads(response.text[5:])

    def get_access(self, repo):
        url = self._mk_url('projects/{}/access', repo)
        return self._get(url)

    def get_group(self, group_id):
        if group_id in self._groups:
            return self._groups[group_id]
        url = self._mk_url('groups/{}', group_id)
        data = self._get(url)
        self._groups[group_id] = data
        return data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        default=False,
    )
    parser.add_argument(
        '--deliverables-dir',
        default=openstack_releases.deliverable_dir,
        help='location of deliverable files',
    )
    args = parser.parse_args()

    config_filename = os.path.join(
        appdirs.user_config_dir('openstack-release', 'openstack'),
        'gerrit.ini',
    )
    config = configparser.ConfigParser()
    config.read(config_filename, encoding='utf-8')

    if not config.has_option('DEFAULT', 'username'):
        parser.error('No username set in {}'.format(config_filename))
    if not config.has_option('DEFAULT', 'password'):
        parser.error('No password set in {}'.format(config_filename))

    gov_data = governance.Governance.from_remote_repo()

    # Some deliverables were independent at one time but might not be
    # any more, so compare the independent list with the current
    # release series.
    all_independent_deliverables = set(
        name
        for team, series, name, deliv in deliverable.Deliverables(
            root_dir=args.deliverables_dir,
            collapse_history=True,
        ).get_deliverables(None, None)
    )
    current_deliverables = set(
        name
        for team, series, name, deliv in deliverable.Deliverables(
            root_dir=args.deliverables_dir,
            collapse_history=True,
        ).get_deliverables(None, defaults.RELEASE)
    )
    independent_deliverables = all_independent_deliverables.difference(
        current_deliverables)

    gerrit = GerritClient(
        config['DEFAULT']['username'],
        config['DEFAULT']['password'],
    )

    for repo in gov_data.get_repositories():

        if repo.name.endswith('-specs'):
            continue
        if 'cookiecutter' in repo.name:
            continue

        if repo.deliverable.team.name in IGNORED_TEAMS:
            if args.verbose:
                print('{}: ignoring {} team'.format(
                    repo.name, repo.deliverable.team.name))
            continue

        if repo.deliverable.name in independent_deliverables:
            if args.verbose:
                print('{}: ignoring independent deliverable'.format(
                    repo.name))
            continue

        acls = gerrit.get_access(repo.name)
        local_tag_acls = acls.get('local', {}).get('refs/tags/*', {})
        if local_tag_acls:
            rules = local_tag_acls.get('permissions', {}).get(
                'pushSignedTag', {}).get('rules', {})
            if not rules and args.verbose:
                print('{}: OK'.format(repo.name))

            for group_id, permissions in rules.items():
                group_details = gerrit.get_group(group_id)
                group_name = group_details['name']
                if group_name in ALLOWED:
                    if args.verbose:
                        print('{}: {} pushSignedTag OK'.format(
                            repo.name, group_name))
                    continue
                if args.verbose:
                    print('{}: {} pushSignedTag WARNING'.format(
                        repo.name, group_name))
                else:
                    print('{}: {} pushSignedTag'.format(
                        repo.name, group_name))
