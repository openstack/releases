#!/usr/bin/env python3
# Copyright 2021 Ericsson Software Technology
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

# This script helps deleting stable branches. Requires 'Delete reference'
# access category for 'refs/for/stable/*' for the user who executes it.

import argparse
import getpass
import json
import sys

import requests


GERRIT_URL = 'https://review.opendev.org/'
GITEA_URL = 'https://opendev.org/api/v1'


def delete_branch(username, project_name, branch_id):
    print(f'!!! WARNING: You are about to delete stable/{branch_id} '
          f'from {project_name} !!!')
    gerrit_auth = requests.auth.HTTPBasicAuth(
        username,
        getpass.getpass('Gerrit password: '))
    url = (f'{GERRIT_URL}a/projects/{project_name.replace("/", "%2F")}/'
           f'branches/stable%2F{branch_id}')
    response = requests.delete(url, auth=gerrit_auth)
    if response.status_code == 204:
        print(f'Branch stable/{branch_id} successfully deleted '
              f'from {project_name}!')
        return 0
    elif response.status_code == 401:
        print('401 Unauthorized.')
        return 1
    else:
        # NOTE(elod.illes): other possible errors from gerrit:
        # 404: In case of project or branch is not found
        # 409: Branch has open changes
        print(f'Delete failed ({response.status_code}): {response.text}')
        return 2


def is_branch_open(project_name, branch_id, quiet):
    url = (f'{GITEA_URL}/repos/{project_name.replace("/", "%2F")}/'
           f'branches/stable%2F{branch_id}')
    response = requests.get(url)
    try:
        response_details = response.json()
    except json.decoder.JSONDecodeError as exc:
        print(f'ERROR: JSON decode failed ({exc})')
        print(f'ERROR: ({response.status_code}): {response.text}')
        print('Is the project name correct, like "openstack/nova"?')
        return 4
    if response.status_code == 200:
        if not quiet:
            print(f'stable/{branch_id} exists in {project_name}.')
        return 0
    elif ((response.status_code == 404) and
          (response_details['errors'] == [f'branch does not exist [name: stable/{branch_id}]']) and
          (response_details['message'] == "The target couldn't be found.")):
        if not quiet:
            print(f'stable/{branch_id} does not exist in {project_name}.')
        return 1
    else:
        print(f'ERROR: ({response.status_code}): {response.text}')
        return 2


def main():
    parser = argparse.ArgumentParser(
        description='Deletes stable/<branch> from <project>.')
    subparsers = parser.add_subparsers(required=True, dest='command',
                                       metavar='{delete,check}')

    delete_parser = subparsers.add_parser(
        'delete', help='Delete stable/<branch> from <project>')
    delete_parser.add_argument('username', help='Gerrit Username')
    delete_parser.add_argument('project', help='Project to delete from')
    delete_parser.add_argument('branch', help='Branch to delete')

    check_parser = subparsers.add_parser(
        'check', help='Check if stable/<branch> exists for <project>')
    check_parser.add_argument('project', help='Project to check')
    check_parser.add_argument('branch', help='Branch to check if exists')
    check_parser.add_argument(
        '-q', '--quiet', action='store_true',
        help='Return code only (0 means branch exists)')

    args = parser.parse_args()
    if args.command == 'delete':
        return delete_branch(args.username,
                             args.project,
                             args.branch.replace('stable/', ''))
    elif args.command == 'check':
        return is_branch_open(args.project,
                              args.branch.replace('stable/', ''),
                              args.quiet)


if __name__ == '__main__':
    sys.exit(main())
