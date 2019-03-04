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

import textwrap

from oslotest import base

from openstack_releases._redirections import generate_constraints_redirections
from openstack_releases import deliverable
from openstack_releases import yamlutils


# Create a Fake Deliverables class we really only need an object with
# get_deliverable_history that returns an iterable.  Using the main real class
# seems like overkill and would subject us to testing chnages as the actual
# deliverables change over time.
class FakeDeliverables(object):
    def __init__(self, deliverables=[]):
        self._deliverables = deliverables

    def get_deliverable_history(self, name):
        return self._deliverables


class TestRedirections(base.BaseTestCase):
    # Deliverable that looks like an open development series with no branches
    # or releases.
    OPEN_DEVELOPMENT = deliverable.Deliverable(
        team='requirements',
        series='stein',
        name='requirements',
        data={}
    )
    # Deliverable that looks like an open development series with no branches
    # but has a single release
    DEVELOPMENT_RELEASE = deliverable.Deliverable(
        team='requirements',
        series='stein',
        name='requirements',
        data=yamlutils.loads(textwrap.dedent('''
        releases:
          - projects:
              - hash: not_used
                repo: openstack/requirements
            version: 1.0.0
        '''))
    )
    # Deliverable that looks like an open stable series with no releases
    OPEN_STABLE = deliverable.Deliverable(
        team='requirements',
        series='rocky',
        name='requirements',
        data=yamlutils.loads(textwrap.dedent('''
        branches:
          - name: stable/rocky
            location:
              openstack/requirements: not_used
        '''))
    )
    # Deliverable that looks like an open stable series with no releases but
    # also has an open 'feature' branch
    OPEN_UNSTABLE = deliverable.Deliverable(
        team='requirements',
        series='rocky',
        name='requirements',
        data=yamlutils.loads(textwrap.dedent('''
        branches:
          - name: unstable/rocky
            location:
              openstack/requirements: not_used
          - name: stable/rocky
            location:
              openstack/requirements: not_used
        '''))
    )
    # Deliverable that looks like an open stable series with a release
    STABLE_RELEASE = deliverable.Deliverable(
        team='requirements',
        series='rocky',
        name='requirements',
        data=yamlutils.loads(textwrap.dedent('''
        branches:
          - name: stable/rocky
            location:
              openstack/requirements: not_used
        releases:
          - projects:
              - hash: not_used
                repo: openstack/requirements
            version: 1.0.0
        '''))
    )
    # Deliverable that looks like a closed stable series
    STABLE_EOL = deliverable.Deliverable(
        team='requirements',
        series='mitaka',
        name='requirements',
        data=yamlutils.loads(textwrap.dedent('''
        releases:
          - projects:
              - hash: not_used
                repo: openstack/requirements
            version: mitaka-eol
        '''))
    )

    def setUp(self):
        super().setUp()

    def test_open_development(self):
        deliverables = FakeDeliverables([
            self.OPEN_DEVELOPMENT,
        ])
        self.assertEqual([dict(code=301, src='stein', dst='master')],
                         generate_constraints_redirections(deliverables))

    def test_development_release(self):
        deliverables = FakeDeliverables([
            self.DEVELOPMENT_RELEASE,
        ])
        self.assertEqual([dict(code=301, src='stein', dst='master')],
                         generate_constraints_redirections(deliverables))

    def test_open_stable(self):
        deliverables = FakeDeliverables([
            self.OPEN_STABLE,
        ])
        self.assertEqual([dict(code=301, src='rocky', dst='stable/rocky')],
                         generate_constraints_redirections(deliverables))

    def test_open_unstable(self):
        deliverables = FakeDeliverables([
            self.OPEN_UNSTABLE,
        ])
        self.assertEqual([dict(code=301, src='rocky', dst='stable/rocky')],
                         generate_constraints_redirections(deliverables))

    def test_stable_release(self):
        deliverables = FakeDeliverables([
            self.STABLE_RELEASE,
        ])
        self.assertEqual([dict(code=301, src='rocky', dst='stable/rocky')],
                         generate_constraints_redirections(deliverables))

    def test_stable_eol(self):
        deliverables = FakeDeliverables([
            self.STABLE_EOL,
        ])
        self.assertEqual([dict(code=301, src='mitaka', dst='mitaka-eol')],
                         generate_constraints_redirections(deliverables))

    def test_all(self):
        deliverables = FakeDeliverables([
            self.STABLE_EOL,
            self.STABLE_RELEASE,
            self.DEVELOPMENT_RELEASE,
        ])
        self.assertEqual([dict(code=301, src='stein', dst='master'),
                          dict(code=301, src='rocky', dst='stable/rocky'),
                          dict(code=301, src='mitaka', dst='mitaka-eol')],
                         generate_constraints_redirections(deliverables))

    def test_empty(self):
        deliverables = FakeDeliverables([])
        self.assertEqual([],
                         generate_constraints_redirections(deliverables))
