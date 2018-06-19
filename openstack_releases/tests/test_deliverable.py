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

import fixtures
from oslotest import base

from openstack_releases import deliverable
from openstack_releases import series_status
from openstack_releases import yamlutils


class TestStableStatus(base.BaseTestCase):

    _series_status_data = yamlutils.loads(textwrap.dedent('''
    - name: rocky
      status: development
      initial-release: 2018-08-30
    - name: queens
      status: maintained
      initial-release: 2018-02-28
    - name: ocata
      status: extended maintenance
      initial-release: 2017-02-22
    - name: newton
      status: end of life
      initial-release: 2016-10-06
      eol-date: 2017-10-25
    '''))

    def setUp(self):
        super().setUp()
        self.series_status = series_status.SeriesStatus(
            self._series_status_data)
        self.useFixture(fixtures.MockPatch(
            'openstack_releases.deliverable.Deliverable._series_status_data',
            self.series_status,
        ))

    def test_default_to_series(self):
        d = deliverable.Deliverable(
            team='team',
            series='ocata',
            name='name',
            data={},
        )
        self.assertEqual('extended maintenance', d.stable_status)

    def test_override_series(self):
        d = deliverable.Deliverable(
            team='team',
            series='newton',
            name='name',
            data={
                'stable-status': 'extended maintenance',
            },
        )
        self.assertEqual('extended maintenance', d.stable_status)


class TestReleaseWasForced(base.BaseTestCase):

    def test_false(self):
        r = deliverable.Release('version', [], {'flags': []}, None)
        self.assertFalse(r.was_forced)

    def test_true(self):
        r = deliverable.Release('version', [], {'flags': ['forced']}, None)
        self.assertTrue(r.was_forced)


class TestEOLTags(base.BaseTestCase):

    def setUp(self):
        super().setUp()

    def test_is_eol_tag_true(self):
        deliverable_data = textwrap.dedent('''
        releases:
          - version: newton-eol
            projects:
              - repo: openstack/release-test
                hash: a26e6a2e8a5e321b2e3517dbb01a7b9a56a8bfd5
        ''')
        deliv = deliverable.Deliverable(
            team='team',
            series='newton',
            name='name',
            data=yamlutils.loads(deliverable_data),
        )
        self.assertTrue(deliv.releases[-1].is_eol)

    def test_is_eol_tag_false(self):
        deliverable_data = textwrap.dedent('''
        releases:
          - version: 0.3.0
            projects:
              - repo: openstack/release-test
                hash: a26e6a2e8a5e321b2e3517dbb01a7b9a56a8bfd5
        ''')
        deliv = deliverable.Deliverable(
            team='team',
            series='newton',
            name='name',
            data=yamlutils.loads(deliverable_data),
        )
        self.assertFalse(deliv.releases[-1].is_eol)

    def test_is_eol_tag_false_typo(self):
        deliverable_data = textwrap.dedent('''
        releases:
          - version: newton-dol
            projects:
              - repo: openstack/release-test
                hash: a26e6a2e8a5e321b2e3517dbb01a7b9a56a8bfd5
        ''')
        deliv = deliverable.Deliverable(
            team='team',
            series='newton',
            name='name',
            data=yamlutils.loads(deliverable_data),
        )
        self.assertFalse(deliv.releases[-1].is_eol)

    def test_eol_series_for_eol_tag(self):
        deliverable_data = textwrap.dedent('''
        releases:
          - version: newton-eol
            projects:
              - repo: openstack/release-test
                hash: a26e6a2e8a5e321b2e3517dbb01a7b9a56a8bfd5
        ''')
        deliv = deliverable.Deliverable(
            team='team',
            series='newton',
            name='name',
            data=yamlutils.loads(deliverable_data),
        )
        self.assertEqual(
            'newton',
            deliv.releases[-1].eol_series,
        )

    def test_eol_series_for_version_tag(self):
        deliverable_data = textwrap.dedent('''
        releases:
          - version: 0.3.0
            projects:
              - repo: openstack/release-test
                hash: a26e6a2e8a5e321b2e3517dbb01a7b9a56a8bfd5
        ''')
        deliv = deliverable.Deliverable(
            team='team',
            series='newton',
            name='name',
            data=yamlutils.loads(deliverable_data),
        )
        self.assertEqual(
            '',
            deliv.releases[-1].eol_series,
        )


class TestTarballBase(base.BaseTestCase):

    def test_not_set(self):
        deliv = deliverable.Deliverable(
            team='team',
            series='newton',
            name='name',
            data={
                'releases': [
                    {'version': '1.5.0',
                     'projects': [
                         {'repo': 'openstack/release-test',
                          'hash': 'a26e6a2e8a5e321b2e3517dbb01a7b9a56a8bfd5'},
                     ]}
                ],
            },
        )
        project = deliv.releases[-1].projects[0]
        self.assertIsNone(project.tarball_base)

    def test_set_project(self):
        deliv = deliverable.Deliverable(
            team='team',
            series='newton',
            name='name',
            data={
                'releases': [
                    {'version': '1.5.0',
                     'projects': [
                         {'repo': 'openstack/release-test',
                          'hash': 'a26e6a2e8a5e321b2e3517dbb01a7b9a56a8bfd5',
                          'tarball-base': 'foo'},
                     ]}
                ],
            },
        )
        project = deliv.releases[-1].projects[0]
        self.assertEqual('foo', project.tarball_base)

    def test_set_repo(self):
        deliv = deliverable.Deliverable(
            team='team',
            series='newton',
            name='name',
            data={
                'releases': [
                    {'version': '1.5.0',
                     'projects': [
                         {'repo': 'openstack/release-test',
                          'hash': 'a26e6a2e8a5e321b2e3517dbb01a7b9a56a8bfd5'},
                     ]}
                ],
                'repository-settings': {
                    'openstack/release-test': {
                        'tarball-base': 'bar',
                    },
                },
            },
        )
        project = deliv.releases[-1].projects[0]
        self.assertEqual('bar', project.tarball_base)

    def test_project_overrides(self):
        deliv = deliverable.Deliverable(
            team='team',
            series='newton',
            name='name',
            data={
                'releases': [
                    {'version': '1.5.0',
                     'projects': [
                         {'repo': 'openstack/release-test',
                          'hash': 'a26e6a2e8a5e321b2e3517dbb01a7b9a56a8bfd5',
                          'tarball-base': 'foo'},
                     ]}
                ],
                'repository-settings': {
                    'openstack/release-test': {
                        'tarball-base': 'bar',
                    },
                },
            },
        )
        project = deliv.releases[-1].projects[0]
        self.assertEqual('foo', project.tarball_base)
