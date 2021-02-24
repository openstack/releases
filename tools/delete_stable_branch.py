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

import requests


GERRIT_URL = 'https://review.opendev.org/'


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
    elif response.status_code == 401:
        print('401 Unauthorized.')
    else:
        # NOTE(elod.illes): other possible errors from gerrit:
        # 404: In case of project or branch is not found
        # 409: Branch has open changes
        print(f'Delete failed ({response.status_code}): {response.text}')


def main():
    parser = argparse.ArgumentParser(
        description='Deletes stable/<branch> from <project>.')
    parser.add_argument('username', help='Gerrit Username')
    parser.add_argument('project', help='Project to delete from')
    parser.add_argument('branch', help='Branch to delete')
    args = parser.parse_args()
    delete_branch(
        args.username,
        args.project,
        args.branch.replace('stable/', ''))


if __name__ == '__main__':
    main()
