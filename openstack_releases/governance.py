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

"""Work with the governance repository.
"""

import weakref

import requests
import yaml

PROJECTS_LIST = "http://git.openstack.org/cgit/openstack/governance/plain/reference/projects.yaml"  # noqa


def get_team_data(url=PROJECTS_LIST):
    """Return the parsed team data from the governance repository.

    :param url: Optional URL to the location of the projects.yaml
        file. Defaults to the most current version in the public git
        repository.

    """
    r = requests.get(url)
    return yaml.load(r.text)


class Team(object):
    def __init__(self, name, data):
        self.name = name
        self.data = data
        self.deliverables = {
            dn: Deliverable(dn, di, self)
            for dn, di in self.data.get('deliverables', {}).items()
        }

    @property
    def tags(self):
        return set(self.data.get('tags', []))


class Deliverable(object):
    def __init__(self, name, data, team):
        self.name = name
        self.data = data
        self.team = weakref.proxy(team)
        self.repositories = {
            rn: Repository(rn, self)
            for rn in self.data.get('repos', [])
        }

    @property
    def tags(self):
        return set(self.data.get('tags', [])).union(self.team.tags)


class Repository(object):
    def __init__(self, name, deliverable):
        self.name = name
        self.deliverable = weakref.proxy(deliverable)

    @property
    def tags(self):
        return self.deliverable.tags

    @property
    def code_related(self):
        return (not (self.name.endswith('-specs') or
                     'cookiecutter' in self.name))
