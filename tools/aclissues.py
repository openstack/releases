#!/usr/bin/python3
#
# Tool to generate a patch to remove direct tagging / branch-creating
# rights for official OpenStack deliverables
#
# Copyright 2018 Thierry Carrez <thierry@openstack.org>
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
import os
import sys

import yaml


TEAM_EXCEPTIONS = [
    # Teams that are likely to be moved off TC governance
    'Infrastructure',
]


def is_a_team_exception(team):
    return team in TEAM_EXCEPTIONS


def issues_in_acl(repo, fullfilename, patch):

    newcontent = ""
    with open(fullfilename) as aclfile:
        skip = False
        issues = False
        for line in aclfile:
            # Skip until start of next section if in skip mode
            if skip:
                if line.startswith('['):
                    skip = False
                else:
                    continue

            # Remove [access ref/tags/*] sections
            if line.startswith('[access "refs/tag'):
                skip = True
                issues = True
                continue

            # Remove 'create' lines
            if line.startswith('create ='):
                issues = True
                continue

            # Copy the current line over
            newcontent += line

    if patch:
        with open(fullfilename, 'w') as aclfile:
            aclfile.write(newcontent)

    return issues


def main(args=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('project_config_repo')
    parser.add_argument('governance_repo')
    parser.add_argument(
        '--patch',
        default=False,
        help='patch ACL files in project-config to fix violations',
        action='store_true')
    args = parser.parse_args(args)

    # Load repo/aclfile mapping from Gerrit config
    projectsyaml = os.path.join(args.project_config_repo,
                                'gerrit', 'projects.yaml')
    acl = {}
    config = yaml.safe_load(open(projectsyaml))
    for project in config:
        aclfilename = project.get('acl-config')
        if aclfilename:
            (head, tail) = os.path.split(aclfilename)
            acl[project['project']] = os.path.join(os.path.basename(head),
                                                   tail)
        else:
            acl[project['project']] = project['project'] + '.config'

    aclbase = os.path.join(args.project_config_repo, 'gerrit', 'acls')
    governanceyaml = os.path.join(args.governance_repo,
                                  'reference', 'projects.yaml')
    teams = yaml.safe_load(open(governanceyaml))
    for tname, team in teams.items():
        if is_a_team_exception(tname):
            continue
        for dname, deliverable in team['deliverables'].items():
            if 'release-management' not in deliverable:
                for repo in deliverable.get('repos'):
                    aclpath = os.path.join(aclbase, acl[repo])
                    if issues_in_acl(repo, aclpath, args.patch):
                        print('%s (%s) in %s' % (repo, tname, acl[repo]))


if __name__ == '__main__':
    main()
