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

from __future__ import unicode_literals

import os
import textwrap

import fixtures
import mock
from oslotest import base

from openstack_releases.cmds import validate
from openstack_releases import defaults
from openstack_releases import deliverable
from openstack_releases import gitutils
from openstack_releases import yamlutils


class TestValidateBugTracker(base.BaseTestCase):

    def setUp(self):
        super().setUp()
        self.msg = validate.MessageCollector()

    def test_no_tracker(self):
        validate.validate_bugtracker(
            deliverable.Deliverable(
                team='team',
                series='series',
                name='name',
                data={},
            ),
            self.msg,
        )
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(1, len(self.msg.errors))

    @mock.patch('requests.get')
    def test_launchpad_invalid_name(self, get):
        get.return_value = mock.Mock(status_code=404)
        validate.validate_bugtracker(
            deliverable.Deliverable(
                team='team',
                series='series',
                name='name',
                data={'launchpad': 'nonsense-name'},
            ),
            self.msg,
        )
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(1, len(self.msg.errors))

    @mock.patch('requests.get')
    def test_launchpad_valid_name(self, get):
        get.return_value = mock.Mock(status_code=200)
        validate.validate_bugtracker(
            deliverable.Deliverable(
                team='team',
                series='series',
                name='name',
                data={'launchpad': 'oslo.config'},
            ),
            self.msg,
        )
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(0, len(self.msg.errors))

    @mock.patch('requests.get')
    def test_launchpad_timeout(self, get):
        import requests
        get.side_effect = requests.exceptions.ConnectionError('testing')
        validate.validate_bugtracker(
            deliverable.Deliverable(
                team='team',
                series='series',
                name='name',
                data={'launchpad': 'oslo.config'},
            ),
            self.msg,
        )
        self.assertEqual(1, len(self.msg.warnings))
        self.assertEqual(0, len(self.msg.errors))

    @mock.patch('requests.get')
    def test_storyboard_valid_id(self, get):
        get.return_value = mock.Mock(status_code=200)
        get.return_value.json.return_value = [
            {
                "name": "openstack-infra/storyboard",
                "created_at": "2014-03-12T17:52:19+00:00",
                "is_active": True,
                "updated_at": None,
                "autocreate_branches": False,
                "repo_url": None,
                "id": 456,
                "description": "OpenStack Task Tracking API",
            },
            {
                "name": "openstack-infra/shade",
                "created_at": "2015-01-07T20:56:27+00:00",
                "is_active": True,
                "updated_at": None,
                "autocreate_branches": False,
                "repo_url": None,
                "id": 760,
                "description": "Client library for OpenStack...",
            }
        ]
        validate.validate_bugtracker(
            deliverable.Deliverable(
                team='team',
                series='series',
                name='name',
                data={'storyboard': '760'},
            ),
            self.msg,
        )
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(0, len(self.msg.errors))

    @mock.patch('requests.get')
    def test_storyboard_no_such_project(self, get):
        get.return_value = mock.Mock(status_code=200)
        get.return_value.json.return_value = [
            {
                "name": "openstack-infra/storyboard",
                "created_at": "2014-03-12T17:52:19+00:00",
                "is_active": True,
                "updated_at": None,
                "autocreate_branches": False,
                "repo_url": None,
                "id": 456,
                "description": "OpenStack Task Tracking API",
            },
        ]
        validate.validate_bugtracker(
            deliverable.Deliverable(
                team='team',
                series='series',
                name='name',
                data={'storyboard': '-760'},
            ),
            self.msg,
        )
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(1, len(self.msg.errors))


class TestValidateTeam(base.BaseTestCase):

    def setUp(self):
        super().setUp()
        self.msg = validate.MessageCollector()

    def test_invalid_name(self):
        validate.validate_team(
            deliverable.Deliverable(
                team='nonsense-name',
                series='series',
                name='name',
                data={},
            ),
            {},
            self.msg,
        )
        self.msg.show_summary()
        self.assertEqual(1, len(self.msg.warnings))
        self.assertEqual(0, len(self.msg.errors))

    def test_valid_name(self):
        validate.validate_team(
            deliverable.Deliverable(
                team='oslo',
                series='series',
                name='name',
                data={},
            ),
            {'oslo': None},
            self.msg,
        )
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(0, len(self.msg.errors))


class TestValidateReleaseNotes(base.BaseTestCase):

    def setUp(self):
        super().setUp()
        self.msg = validate.MessageCollector()

    def test_no_link(self):
        validate.validate_release_notes(
            deliverable.Deliverable(
                team='team',
                series='series',
                name='name',
                data={},
            ),
            self.msg,
        )
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(0, len(self.msg.errors))

    def test_invalid_link(self):
        validate.validate_release_notes(
            deliverable.Deliverable(
                team='team',
                series='series',
                name='name',
                data={
                    'release-notes': 'https://docs.openstack.org/no-such-page',
                },
            ),
            self.msg,
        )
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(1, len(self.msg.errors))

    def test_valid_link(self):
        validate.validate_release_notes(
            deliverable.Deliverable(
                team='team',
                series='series',
                name='name',
                data={'release-notes':
                      'https://docs.openstack.org/releasenotes/oslo.config'},
            ),
            self.msg,
        )
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(0, len(self.msg.errors))

    def test_invalid_link_multi(self):
        validate.validate_release_notes(
            deliverable.Deliverable(
                team='team',
                series='series',
                name='name',
                data={
                    'repository-settings': {
                        'openstack/releases': {},
                    },
                    'release-notes': {
                        'openstack/releases':
                        'https://docs.openstack.org/no-such-page',
                    }
                },
            ),
            self.msg,
        )
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(1, len(self.msg.errors))

    def test_unknown_repo(self):
        validate.validate_release_notes(
            deliverable.Deliverable(
                team='team',
                series='series',
                name='name',
                data={
                    'repository-settings': {
                        'openstack/release-test': {},
                    },
                    'release-notes': {
                        'openstack/oslo.config':
                        'https://docs.openstack.org/releasenotes/oslo.config',
                    }
                },
            ),
            self.msg,
        )
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(1, len(self.msg.errors))

    def test_valid_link_multi(self):
        validate.validate_release_notes(
            deliverable.Deliverable(
                team='team',
                series='series',
                name='name',
                data={
                    'repository-settings': {
                        'openstack/releases': {},
                    },
                    'release-notes': {
                        'openstack/releases':
                        'https://docs.openstack.org/releasenotes/oslo.config',
                    },
                },
            ),
            self.msg,
        )
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(0, len(self.msg.errors))


class TestValidateModel(base.BaseTestCase):

    def setUp(self):
        super().setUp()
        self.msg = validate.MessageCollector()

    def test_no_model_series(self):
        validate.validate_model(
            deliverable.Deliverable(
                team='team',
                series='ocata',
                name='name',
                data={},
            ),
            'ocata',
            self.msg,
        )
        self.msg.show_summary()
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(1, len(self.msg.errors))

    def test_no_model_independent(self):
        validate.validate_model(
            deliverable.Deliverable(
                team='team',
                series='independent',
                name='name',
                data={},
            ),
            'independent',
            self.msg,
        )
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(0, len(self.msg.errors))

    def test_with_model_independent_match(self):
        validate.validate_model(
            deliverable.Deliverable(
                team='team',
                series='independent',
                name='name',
                data={'release-model': 'independent'},
            ),
            'independent',
            self.msg,
        )
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(0, len(self.msg.errors))

    def test_with_model_independent_nomatch(self):
        validate.validate_model(
            deliverable.Deliverable(
                team='team',
                series='independent',
                name='name',
                data={'release-model': 'cycle-with-intermediary'},
            ),
            'independent',
            self.msg,
        )
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(1, len(self.msg.errors))

    def test_with_independent_and_model(self):
        validate.validate_model(
            deliverable.Deliverable(
                team='team',
                series='ocata',
                name='name',
                data={'release-model': 'independent'},
            ),
            'ocata',
            self.msg,
        )
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(1, len(self.msg.errors))

    def test_with_model_series(self):
        validate.validate_model(
            deliverable.Deliverable(
                team='team',
                series='ocata',
                name='name',
                data={'release-model': 'cycle-with-intermediary'},
            ),
            'ocata',
            self.msg,
        )
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(0, len(self.msg.errors))


class TestValidateReleases(base.BaseTestCase):

    def setUp(self):
        super(TestValidateReleases, self).setUp()
        self.tmpdir = self.useFixture(fixtures.TempDir()).path
        gitutils.clone_repo(self.tmpdir, 'openstack/release-test')
        self.msg = validate.MessageCollector()

    def test_invalid_hash(self):
        deliv = deliverable.Deliverable(
            team='team',
            series='ocata',
            name='name',
            data={
                'artifact-link-mode': 'none',
                'releases': [
                    {'version': '0.1',
                     'projects': [
                         {'repo': 'openstack/release-test',
                          'hash': 'this-is-not-a-hash',
                          'tarball-base': 'openstack-release-test'},
                     ]}
                ],
            },
        )
        validate.validate_releases(
            deliv,
            {'validate-projects-by-name': {}},
            'ocata',
            self.tmpdir,
            self.msg,
        )
        self.msg.show_summary()
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(1, len(self.msg.errors))

    def test_valid_existing(self):
        deliv = deliverable.Deliverable(
            team='team',
            series='ocata',
            name='name',
            data={
                'artifact-link-mode': 'none',
                'releases': [
                    {'version': '0.8.0',
                     'projects': [
                         {'repo': 'openstack/release-test',
                          'hash': 'a26e6a2e8a5e321b2e3517dbb01a7b9a56a8bfd5',
                          'tarball-base': 'openstack-release-test'},
                     ]}
                ],
            },
        )
        validate.validate_releases(
            deliv,
            {'validate-projects-by-name': {}},
            'ocata',
            self.tmpdir,
            self.msg,
        )
        self.msg.show_summary()
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(0, len(self.msg.errors))

    def test_no_such_hash(self):
        deliv = deliverable.Deliverable(
            team='team',
            series='ocata',
            name='name',
            data={
                'artifact-link-mode': 'none',
                'releases': [
                    {'version': '99.0.0',
                     'projects': [
                         {'repo': 'openstack/release-test',
                          'hash': 'de2885f544637e6ee6139df7dc7bf937925804dd',
                          'tarball-base': 'openstack-release-test'},
                     ]}
                ],
            },
        )
        validate.validate_releases(
            deliv,
            {'validate-projects-by-name': {}},
            'ocata',
            self.tmpdir,
            self.msg,
        )
        self.msg.show_summary()
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(1, len(self.msg.errors))

    def test_mismatch_existing(self):
        deliv = deliverable.Deliverable(
            team='team',
            series='ocata',
            name='name',
            data={
                'artifact-link-mode': 'none',
                'releases': [
                    {'version': '0.8.0',
                     'projects': [
                         {'repo': 'openstack/release-test',
                          # hash from the previous release
                          'hash': '88af0f601895d54fb0a45b796cdd045a2b3636a3'},
                     ]}
                ],
            },
        )
        validate.validate_releases(
            deliv,
            {'validate-projects-by-name': {}},
            'newton',
            self.tmpdir,
            self.msg,
        )
        self.msg.show_summary()
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(1, len(self.msg.errors))

    def test_hash_from_master_used_in_stable_release(self):
        deliv = deliverable.Deliverable(
            team='team',
            series='ocata',
            name='name',
            data={
                'artifact-link-mode': 'none',
                'releases': [
                    {'version': '0.8.1',
                     'projects': [
                         {'repo': 'openstack/release-test',
                          # hash from master
                          'hash': '218c9c82f168f1db681b27842b5a829428c6b5e1',
                          'tarball-base': 'openstack-release-test'},
                     ]}
                ],
            }
        )
        validate.validate_releases(
            deliv,
            {'validate-projects-by-name': {}},
            'newton',
            self.tmpdir,
            self.msg,
        )
        self.msg.show_summary()
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(1, len(self.msg.errors))

    def test_hash_from_master_used_in_stable_release2(self):
        deliv = deliverable.Deliverable(
            team='team',
            series='ocata',
            name='name',
            data={
                'artifact-link-mode': 'none',
                'releases': [
                    {'version': '0.8.0',
                     'projects': [
                         {'repo': 'openstack/release-test',
                          'hash': 'a26e6a2e8a5e321b2e3517dbb01a7b9a56a8bfd5',
                          'tarball-base': 'openstack-release-test'},
                     ]},
                    {'version': '0.8.1',
                     'projects': [
                         {'repo': 'openstack/release-test',
                          # hash from master
                          'hash': '218c9c82f168f1db681b27842b5a829428c6b5e1',
                          'tarball-base': 'openstack-release-test'},
                     ]}
                ],
            }
        )
        validate.validate_releases(
            deliv,
            {'validate-projects-by-name': {}},
            'newton',
            self.tmpdir,
            self.msg,
        )
        self.msg.show_summary()
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(1, len(self.msg.errors))

    def test_hash_from_stable_used_in_master_release(self):
        deliv = deliverable.Deliverable(
            team='team',
            series='ocata',
            name='name',
            data={
                'artifact-link-mode': 'none',
                'releases': [
                    {'version': '99.5.0',
                     'projects': [
                         {'repo': 'openstack/release-test',
                          # hash from stable/newton
                          'hash': 'a8185a9a6c934567f2f8b7543136274dda78ddd3',
                          'tarball-base': 'openstack-release-test'},
                     ]}
                ],
            }
        )
        validate.validate_releases(
            deliv,
            {'validate-projects-by-name': {}},
            defaults.RELEASE,
            self.tmpdir,
            self.msg,
        )
        self.msg.show_summary()
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(1, len(self.msg.errors))

    def test_hash_from_master_used_after_default_branch_should_exist_but_does_not(self):
        deliv = deliverable.Deliverable(
            team='team',
            series='ocata',
            name='name',
            data={
                'artifact-link-mode': 'none',
                'releases': [
                    {'version': '1.0.0',
                     'projects': [
                         {'repo': 'openstack/releases',
                          'hash': '8eea82428995b8f3354c0a75351fe95bbbb1135a'},
                     ]}
                ],
            }
        )
        validate.validate_releases(
            deliv,
            {'validate-projects-by-name': {}},
            'austin',
            self.tmpdir,
            self.msg,
        )
        self.msg.show_summary()
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(0, len(self.msg.errors))

    def test_not_descendent(self):
        deliv = deliverable.Deliverable(
            team='team',
            series='ocata',
            name='name',
            data={
                'artifact-link-mode': 'none',
                'releases': [
                    # hash from stable/meiji
                    {'version': '0.0.2',
                     'projects': [
                         {'repo': 'openstack/release-test',
                          'hash': '9f48cae13a7388a6f6d1361634d320d73baef0d3',
                          'tarball-base': 'openstack-release-test'},
                     ]},
                    # hash from stable/newton
                    {'version': '0.0.9',  # 0.0.3 already exists
                     'projects': [
                         {'repo': 'openstack/release-test',
                          'hash': 'a8185a9a6c934567f2f8b7543136274dda78ddd3',
                          'tarball-base': 'openstack-release-test'},
                     ]}
                ],
            }
        )
        validate.validate_releases(
            deliv,
            {'validate-projects-by-name': {}},
            'meiji',
            self.tmpdir,
            self.msg,
        )
        self.msg.show_summary()
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(2, len(self.msg.errors))

    def test_new_not_at_end(self):
        deliv = deliverable.Deliverable(
            team='team',
            series='ocata',
            name='name',
            data={
                'artifact-link-mode': 'none',
                'releases': [
                    {'version': '0.8.1',
                     'projects': [
                         {'repo': 'openstack/release-test',
                          'hash': 'a26e6a2e8a5e321b2e3517dbb01a7b9a56a8bfd5',
                          'tarball-base': 'openstack-release-test'},
                     ]},
                    {'version': '0.7.2',
                     'projects': [
                         {'repo': 'openstack/release-test',
                          'hash': 'a26e6a2e8a5e321b2e3517dbb01a7b9a56a8bfd5',
                          'tarball-base': 'openstack-release-test'},
                     ]},
                ],
            }
        )
        validate.validate_releases(
            deliv,
            {'validate-projects-by-name': {}},
            'ocata',
            self.tmpdir,
            self.msg,
        )
        self.msg.show_summary()
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(1, len(self.msg.errors))

    @mock.patch('openstack_releases.versionutils.validate_version')
    def test_invalid_version(self, validate_version):
        # Set up the nested validation function to produce an error,
        # even though there is nothing else wrong with the
        # inputs. That ensures we only get the 1 error back.
        validate_version.configure_mock(
            return_value=['an error goes here'],
        )
        deliv = deliverable.Deliverable(
            team='team',
            series='ocata',
            name='name',
            data={
                'artifact-link-mode': 'none',
                'releases': [
                    {'version': '99.5.0',
                     'projects': [
                         {'repo': 'openstack/release-test',
                          'hash': 'a26e6a2e8a5e321b2e3517dbb01a7b9a56a8bfd5'},
                     ]}
                ],
            }
        )
        validate.validate_releases(
            deliv,
            {'validate-projects-by-name': {}},
            'ocata',
            self.tmpdir,
            self.msg,
        )
        self.msg.show_summary()
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(1, len(self.msg.errors))

    def test_no_releases(self):
        # When we initialize a new series, we won't have any release
        # data. That's OK.
        deliv = deliverable.Deliverable(
            team='team',
            series='ocata',
            name='name',
            data={
                'artifact-link-mode': 'none',
                'releases': []
            }
        )
        validate.validate_releases(
            deliv,
            {'validate-projects-by-name': {}},
            'ocata',
            self.tmpdir,
            self.msg,
        )
        self.msg.show_summary()
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(0, len(self.msg.errors))

    def test_untagged_with_releases(self):
        deliv = deliverable.Deliverable(
            team='team',
            series='ocata',
            name='name',
            data={
                'release-model': 'untagged',
                'artifact-link-mode': 'none',
                'releases': [
                    {'version': '99.5.0',
                     'projects': [
                         {'repo': 'openstack/release-test',
                          'hash': 'a26e6a2e8a5e321b2e3517dbb01a7b9a56a8bfd5'},
                     ]},
                ]
            }
        )
        validate.validate_releases(
            deliv,
            {'validate-projects-by-name': {}},
            'ocata',
            self.tmpdir,
            self.msg,
        )
        self.msg.show_summary()
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(1, len(self.msg.errors))


class TestGetReleaseType(base.BaseTestCase):

    def setUp(self):
        super(TestGetReleaseType, self).setUp()
        self.tmpdir = self.useFixture(fixtures.TempDir()).path
        self.msg = validate.MessageCollector()

    def test_explicit(self):
        deliv = deliverable.Deliverable(
            team='team',
            series='series',
            name='name',
            data={
                'artifact-link-mode': 'none',
                'release-type': 'explicitly-set',
                'releases': [
                    {'version': '99.1.0',
                     'projects': [
                         {'repo': 'openstack/puppet-watcher',
                          'hash': '1e7baef27139f69a83e1fe28686bb72ee7e1d6fa'},
                     ]}
                ],
            },
        )
        release_type, explicit = validate.get_release_type(
            deliv,
            deliv.releases[0].projects[0].repo,
            self.tmpdir,
        )
        self.assertEqual(('explicitly-set', True), (release_type, explicit))

    def test_library(self):
        deliv = deliverable.Deliverable(
            team='team',
            series='series',
            name='name',
            data={
                'artifact-link-mode': 'none',
                'type': 'library',
                'releases': [
                    {'version': '99.1.0',
                     'projects': [
                         {'repo': 'openstack/puppet-watcher',
                          'hash': '1e7baef27139f69a83e1fe28686bb72ee7e1d6fa'},
                     ]}
                ],
            },
        )
        release_type, explicit = validate.get_release_type(
            deliv,
            deliv.releases[0].projects[0].repo,
            self.tmpdir,
        )
        self.assertEqual(('python-pypi', False), (release_type, explicit))

    def test_service(self):
        deliv = deliverable.Deliverable(
            team='team',
            series='series',
            name='name',
            data={
                'artifact-link-mode': 'none',
                'type': 'service',
                'releases': [
                    {'version': '99.1.0',
                     'projects': [
                         {'repo': 'openstack/puppet-watcher',
                          'hash': '1e7baef27139f69a83e1fe28686bb72ee7e1d6fa'},
                     ]}
                ],
            },
        )
        release_type, explicit = validate.get_release_type(
            deliv,
            deliv.releases[0].projects[0].repo,
            self.tmpdir,
        )
        self.assertEqual(('python-service', False), (release_type, explicit))

    def test_implicit_pypi(self):
        deliv = deliverable.Deliverable(
            team='team',
            series='series',
            name='name',
            data={
                'artifact-link-mode': 'none',
                'include-pypi-link': True,
                'releases': [
                    {'version': '99.1.0',
                     'projects': [
                         {'repo': 'openstack/puppet-watcher',
                          'hash': '1e7baef27139f69a83e1fe28686bb72ee7e1d6fa'},
                     ]}
                ],
            },
        )
        release_type, explicit = validate.get_release_type(
            deliv,
            deliv.releases[0].projects[0].repo,
            self.tmpdir,
        )
        self.assertEqual(('python-pypi', False), (release_type, explicit))

    def test_pypi_false(self):
        deliv = deliverable.Deliverable(
            team='team',
            series='series',
            name='name',
            data={
                'artifact-link-mode': 'none',
                'include-pypi-link': False,
                'releases': [
                    {'version': '99.1.0',
                     'projects': [
                         {'repo': 'openstack/puppet-watcher',
                          'hash': '1e7baef27139f69a83e1fe28686bb72ee7e1d6fa'},
                     ]}
                ],
            },
        )
        release_type, explicit = validate.get_release_type(
            deliv,
            deliv.releases[0].projects[0].repo,
            self.tmpdir,
        )
        self.assertEqual(('python-service', False), (release_type, explicit))

    @mock.patch('openstack_releases.puppetutils.looks_like_a_module')
    def test_puppet(self, llam):
        llam.return_value = True
        deliv = deliverable.Deliverable(
            team='team',
            series='series',
            name='name',
            data={
                'artifact-link-mode': 'none',
                'releases': [
                    {'version': '99.1.0',
                     'projects': [
                         {'repo': 'openstack/puppet-watcher',
                          'hash': '1e7baef27139f69a83e1fe28686bb72ee7e1d6fa'},
                     ]}
                ],
            },
        )
        release_type, explicit = validate.get_release_type(
            deliv,
            deliv.releases[0].projects[0].repo,
            self.tmpdir,
        )
        self.assertEqual(('puppet', False), (release_type, explicit))

    @mock.patch('openstack_releases.npmutils.looks_like_a_module')
    def test_nodejs(self, llam):
        llam.return_value = True
        deliv = deliverable.Deliverable(
            team='team',
            series='series',
            name='name',
            data={
                'artifact-link-mode': 'none',
                'releases': [
                    {'version': '99.1.0',
                     'projects': [
                         {'repo': 'openstack/puppet-watcher',
                          'hash': '1e7baef27139f69a83e1fe28686bb72ee7e1d6fa'},
                     ]}
                ],
            },
        )
        release_type, explicit = validate.get_release_type(
            deliv,
            deliv.releases[0].projects[0].repo,
            self.tmpdir,
        )
        self.assertEqual(('nodejs', False), (release_type, explicit))

    @mock.patch('openstack_releases.puppetutils.looks_like_a_module')
    @mock.patch('openstack_releases.npmutils.looks_like_a_module')
    def test_python_server(self, nllam, pllam):
        pllam.return_value = False
        nllam.return_value = False
        deliv = deliverable.Deliverable(
            team='team',
            series='series',
            name='name',
            data={
                'artifact-link-mode': 'none',
                'releases': [
                    {'version': '99.1.0',
                     'projects': [
                         {'repo': 'openstack/puppet-watcher',
                          'hash': '1e7baef27139f69a83e1fe28686bb72ee7e1d6fa'},
                     ]}
                ],
            },
        )
        release_type, explicit = validate.get_release_type(
            deliv,
            deliv.releases[0].projects[0].repo,
            self.tmpdir,
        )
        self.assertEqual(('python-service', False), (release_type, explicit))


class TestPuppetUtils(base.BaseTestCase):

    def setUp(self):
        super(TestPuppetUtils, self).setUp()
        self.tmpdir = self.useFixture(fixtures.TempDir()).path
        self.msg = validate.MessageCollector()

    @mock.patch('openstack_releases.gitutils.check_branch_sha')
    @mock.patch('openstack_releases.puppetutils.get_version')
    @mock.patch('openstack_releases.puppetutils.looks_like_a_module')
    def test_valid_version(self, llam, get_version, cbs):
        llam.return_value = True
        get_version.return_value = '99.1.0'
        cbs.return_value = True
        deliv = deliverable.Deliverable(
            team='team',
            series='series',
            name='name',
            data={
                'artifact-link-mode': 'none',
                'releases': [
                    {'version': '99.1.0',
                     'projects': [
                         {'repo': 'openstack/puppet-watcher',
                          'hash': '1e7baef27139f69a83e1fe28686bb72ee7e1d6fa'},
                     ]}
                ],
            }
        )
        validate.validate_releases(
            deliv,
            {'validate-projects-by-name': {}},
            'ocata',
            self.tmpdir,
            self.msg,
        )
        self.msg.show_summary()
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(0, len(self.msg.errors))

    @mock.patch('openstack_releases.gitutils.check_branch_sha')
    @mock.patch('openstack_releases.puppetutils.get_version')
    @mock.patch('openstack_releases.puppetutils.looks_like_a_module')
    def test_mismatched_version(self, llam, get_version, cbs):
        llam.return_value = True
        get_version.return_value = '99.1.0'
        cbs.return_value = True
        deliv = deliverable.Deliverable(
            team='team',
            series='series',
            name='name',
            data={
                'artifact-link-mode': 'none',
                'releases': [
                    {'version': '99.2.0',
                     'projects': [
                         {'repo': 'openstack/puppet-watcher',
                          'hash': '1e7baef27139f69a83e1fe28686bb72ee7e1d6fa'},
                     ]}
                ],
            }
        )
        validate.validate_releases(
            deliv,
            {'validate-projects-by-name': {}},
            'ocata',
            self.tmpdir,
            self.msg,
        )
        self.msg.show_summary()
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(1, len(self.msg.errors))


class TestValidateTarballBase(base.BaseTestCase):

    def setUp(self):
        super(TestValidateTarballBase, self).setUp()
        self.tmpdir = self.useFixture(fixtures.TempDir()).path
        self.msg = validate.MessageCollector()

    @mock.patch('openstack_releases.project_config.require_release_jobs_for_repo')
    @mock.patch('openstack_releases.pythonutils.get_sdist_name')
    def test_default_ok(self, gsn, jobs):
        deliv = deliverable.Deliverable(
            team='team',
            series='series',
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
        gsn.return_value = 'release-test'
        validate.clone_deliverable(
            deliv,
            self.tmpdir,
            self.msg,
        )
        validate.validate_tarball_base(
            deliv,
            self.tmpdir,
            self.msg,
        )
        self.msg.show_summary()
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(0, len(self.msg.errors))

    @mock.patch('openstack_releases.project_config.require_release_jobs_for_repo')
    @mock.patch('openstack_releases.pythonutils.get_sdist_name')
    def test_ignored_link_mode_none(self, gsn, jobs):
        deliv = deliverable.Deliverable(
            team='team',
            series='series',
            name='name',
            data={
                'artifact-link-mode': 'none',
                'releases': [
                    {'version': '1.5.0',
                     'projects': [
                         {'repo': 'openstack/release-test',
                          'hash': 'a26e6a2e8a5e321b2e3517dbb01a7b9a56a8bfd5'},
                     ]}
                ],
            }
        )
        gsn.return_value = 'this-is-wrong'
        validate.clone_deliverable(
            deliv,
            self.tmpdir,
            self.msg,
        )
        validate.validate_tarball_base(
            deliv,
            self.tmpdir,
            self.msg,
        )
        self.msg.show_summary()
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(0, len(self.msg.errors))

    @mock.patch('openstack_releases.project_config.require_release_jobs_for_repo')
    @mock.patch('openstack_releases.pythonutils.get_sdist_name')
    def test_default_invalid(self, gsn, jobs):
        deliv = deliverable.Deliverable(
            team='team',
            series='series',
            name='name',
            data={
                'releases': [
                    {'version': '1.5.0',
                     'projects': [
                         {'repo': 'openstack/release-test',
                          'hash': 'a26e6a2e8a5e321b2e3517dbb01a7b9a56a8bfd5'},
                     ]}
                ],
            }
        )
        gsn.return_value = 'openstack-release-test'
        validate.clone_deliverable(
            deliv,
            self.tmpdir,
            self.msg,
        )
        validate.validate_tarball_base(
            deliv,
            self.tmpdir,
            self.msg,
        )
        self.msg.show_summary()
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(1, len(self.msg.errors))

    @mock.patch('openstack_releases.project_config.require_release_jobs_for_repo')
    @mock.patch('openstack_releases.pythonutils.get_sdist_name')
    def test_explicit_ok(self, gsn, jobs):
        deliv = deliverable.Deliverable(
            team='team',
            series='series',
            name='name',
            data={
                'releases': [
                    {'version': '1.5.0',
                     'projects': [
                         {'repo': 'openstack/release-test',
                          'hash': 'a26e6a2e8a5e321b2e3517dbb01a7b9a56a8bfd5',
                          'tarball-base': 'openstack-release-test'},
                     ]}
                ],
            }
        )
        gsn.return_value = 'openstack-release-test'
        validate.clone_deliverable(
            deliv,
            self.tmpdir,
            self.msg,
        )
        validate.validate_tarball_base(
            deliv,
            self.tmpdir,
            self.msg,
        )
        self.msg.show_summary()
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(0, len(self.msg.errors))

    @mock.patch('openstack_releases.project_config.require_release_jobs_for_repo')
    @mock.patch('openstack_releases.pythonutils.get_sdist_name')
    def test_explicit_invalid(self, gsn, jobs):
        deliv = deliverable.Deliverable(
            team='team',
            series='series',
            name='name',
            data={
                'releases': [
                    {'version': '1.5.0',
                     'projects': [
                         {'repo': 'openstack/release-test',
                          'hash': 'a26e6a2e8a5e321b2e3517dbb01a7b9a56a8bfd5',
                          'tarball-base': 'does-not-match-sdist'},
                     ]}
                ],
            }
        )
        gsn.return_value = 'openstack-release-test'
        validate.clone_deliverable(
            deliv,
            self.tmpdir,
            self.msg,
        )
        validate.validate_tarball_base(
            deliv,
            self.tmpdir,
            self.msg,
        )
        self.msg.show_summary()
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(1, len(self.msg.errors))


class TestValidateNewReleases(base.BaseTestCase):

    team_data_yaml = textwrap.dedent("""
    Release Management:
      ptl:
        name: Doug Hellmann
        irc: dhellmann
        email: doug@doughellmann.com
      irc-channel: openstack-release
      mission: >
        Coordinating the release of OpenStack deliverables, by defining the
        overall development cycle, release models, publication processes,
        versioning rules and tools, then enabling project teams to produce
        their own releases.
      url: https://wiki.openstack.org/wiki/Release_Management
      tags:
        - team:diverse-affiliation
      deliverables:
        release-schedule-generator:
          repos:
            - openstack/release-schedule-generator
        release-test:
          repos:
            - openstack/release-test
        release-tools:
          repos:
            - openstack-infra/release-tools
        releases:
          repos:
            - openstack/releases
        reno:
          repos:
            - openstack/reno
          docs:
            contributor: https://docs.openstack.org/developer/reno/
        specs-cookiecutter:
          repos:
            - openstack-dev/specs-cookiecutter
    """)

    team_data = yamlutils.loads(team_data_yaml)

    def setUp(self):
        super().setUp()
        self.msg = validate.MessageCollector()

    def test_all_repos(self):
        # The repos in the tag, governance, and repository-settings
        # match.
        deliv = deliverable.Deliverable(
            team='team',
            series='series',
            name='release-test',
            data={
                'artifact-link-mode': 'none',
                'repository-settings': {
                    'openstack/release-test': {},
                },
                'releases': [
                    {'version': '1000.0.0',
                     'projects': [
                         {'repo': 'openstack/release-test',
                          'hash': '685da43147c3bedc24906d5a26839550f2e962b1',
                          'tarball-base': 'openstack-release-test'},
                     ]}
                ],
            }
        )
        validate.validate_new_releases(
            deliv,
            self.team_data,
            self.msg,
        )
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(0, len(self.msg.errors))

    def test_extra_repo_gov(self):
        # The tag includes a repo not in governance.
        deliv = deliverable.Deliverable(
            team='team',
            series='series',
            name='release-test',
            data={
                'artifact-link-mode': 'none',
                'repository-settings': {
                    'openstack/release-test': {},
                    'openstack-infra/release-tools': {},
                },
                'releases': [
                    {'version': '1000.0.0',
                     'projects': [
                         {'repo': 'openstack/release-test',
                          'hash': '685da43147c3bedc24906d5a26839550f2e962b1',
                          'tarball-base': 'openstack-release-test'},
                         {'repo': 'openstack-infra/release-tools',
                          'hash': '685da43147c3bedc24906d5a26839550f2e962b1',
                          'tarball-base': 'openstack-release-test'},
                     ]}
                ],
            }
        )
        validate.validate_new_releases(
            deliv,
            self.team_data,
            self.msg,
        )
        self.assertEqual(1, len(self.msg.warnings))
        self.assertEqual(0, len(self.msg.errors))

    def test_missing_repo_gov(self):
        # The tag is missing a repo in governance.
        deliv = deliverable.Deliverable(
            team='team',
            series='series',
            name='release-test',
            data={
                'artifact-link-mode': 'none',
                'repository-settings': {
                    'openstack/release-test': {},
                    'openstack/made-up-name': {},
                },
                'releases': [
                    {'version': '1000.0.0',
                     'projects': [
                         {'repo': 'openstack/release-test',
                          'hash': '685da43147c3bedc24906d5a26839550f2e962b1',
                          'tarball-base': 'openstack-release-test'},
                         {'repo': 'openstack/made-up-name',
                          'hash': '685da43147c3bedc24906d5a26839550f2e962b1',
                          'tarball-base': 'openstack-release-test'},
                     ]}
                ],
            }
        )
        validate.validate_new_releases(
            deliv,
            self.team_data,
            self.msg,
        )
        self.msg.show_summary()
        self.assertEqual(1, len(self.msg.warnings))
        self.assertEqual(0, len(self.msg.errors))

    def test_extra_repo_info(self):
        # The tag has a repo not in repository-settings or governance
        # (2 warnings).
        deliv = deliverable.Deliverable(
            team='team',
            series='series',
            name='release-test',
            data={
                'artifact-link-mode': 'none',
                'repository-settings': {
                },
                'releases': [
                    {'version': '1000.0.0',
                     'projects': [
                         {'repo': 'openstack/release-test',
                          'hash': '685da43147c3bedc24906d5a26839550f2e962b1',
                          'tarball-base': 'openstack-release-test'},
                     ]}
                ],
            }
        )
        validate.validate_new_releases(
            deliv,
            self.team_data,
            self.msg,
        )
        self.msg.show_summary()
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(1, len(self.msg.errors))

    def test_missing_repo_info(self):
        # The tag is missing a repository that is in
        # repository-settings.
        deliv = deliverable.Deliverable(
            team='team',
            series='series',
            name='release-test',
            data={
                'artifact-link-mode': 'none',
                'repository-settings': {
                    'openstack/release-test': {},
                    'openstack-infra/release-tools': {},
                },
                'releases': [
                    {'version': '1000.0.0',
                     'projects': [
                         {'repo': 'openstack/release-test',
                          'hash': '685da43147c3bedc24906d5a26839550f2e962b1',
                          'tarball-base': 'openstack-release-test'},
                     ]}
                ],
            }
        )
        validate.validate_new_releases(
            deliv,
            self.team_data,
            self.msg,
        )
        self.msg.show_summary()
        self.assertEqual(1, len(self.msg.warnings))
        self.assertEqual(0, len(self.msg.errors))


class TestValidateBranchPrefixes(base.BaseTestCase):

    def setUp(self):
        super().setUp()
        self.msg = validate.MessageCollector()

    def test_invalid_prefix(self):
        deliverable_info = {
            'branches': [
                {'name': 'invalid/branch'},
            ],
        }
        validate.validate_branch_prefixes(
            deliverable_info,
            self.msg,
        )
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(1, len(self.msg.errors))

    def test_valid_prefix(self):
        for prefix in validate._VALID_BRANCH_PREFIXES:
            deliverable_info = {
                'branches': [
                    {'name': '%s/branch' % prefix},
                ],
            }
            validate.validate_branch_prefixes(
                deliverable_info,
                self.msg,
            )
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(0, len(self.msg.errors))


class TestValidateStableBranches(base.BaseTestCase):

    def setUp(self):
        super(TestValidateStableBranches, self).setUp()
        self.tmpdir = self.useFixture(fixtures.TempDir()).path
        gitutils.clone_repo(self.tmpdir, 'openstack/release-test')
        self.msg = validate.MessageCollector()

    def test_version_in_deliverable(self):
        deliverable_data = textwrap.dedent('''
        releases:
          - version: 0.0.3
            projects:
              - repo: openstack/release-test
                hash: 0cd17d1ee3b9284d36b2a0d370b49a6f0bbb9660
        branches:
          - name: stable/ocata
            location: 0.0.3
        ''')
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_stable_branches(
            deliverable_info,
            'name',
            self.tmpdir,
            'ocata',
            self.msg,
        )
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(0, len(self.msg.errors))

    def test_badly_formatted_name(self):
        deliverable_data = textwrap.dedent('''
        releases:
          - version: 0.0.3
            projects:
              - repo: openstack/release-test
                hash: 0cd17d1ee3b9284d36b2a0d370b49a6f0bbb9660
        branches:
          - name: ocata
            location: 0.0.3
        ''')
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_stable_branches(
            deliverable_info,
            'name',
            self.tmpdir,
            'ocata',
            self.msg,
        )
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(1, len(self.msg.errors))

    def test_version_not_in_deliverable(self):
        deliverable_data = textwrap.dedent('''
        releases:
          - version: 0.0.3
            projects:
              - repo: openstack/release-test
                hash: 0cd17d1ee3b9284d36b2a0d370b49a6f0bbb9660
        branches:
          - name: stable/ocata
            location: 0.0.4
        ''')
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_stable_branches(
            deliverable_info,
            'name',
            self.tmpdir,
            'ocata',
            self.msg,
        )
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(1, len(self.msg.errors))

    def test_unknown_series_cycle(self):
        deliverable_data = textwrap.dedent('''
        releases:
          - version: 0.0.3
            projects:
              - repo: openstack/release-test
                hash: 0cd17d1ee3b9284d36b2a0d370b49a6f0bbb9660
        branches:
          - name: stable/abc
            location: 0.0.3
        ''')
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_stable_branches(
            deliverable_info,
            'name',
            self.tmpdir,
            'ocata',
            self.msg,
        )
        self.msg.show_summary()
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(1, len(self.msg.errors))

    def test_unknown_series_independent(self):
        deliverable_data = textwrap.dedent('''
        releases:
          - version: 0.0.3
            projects:
              - repo: openstack/release-test
                hash: 0cd17d1ee3b9284d36b2a0d370b49a6f0bbb9660
        branches:
          - name: stable/abc
            location: 0.0.3
        ''')
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_stable_branches(
            deliverable_info,
            'name',
            self.tmpdir,
            '_independent',
            self.msg,
        )
        self.msg.show_summary()
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(1, len(self.msg.errors))

    def test_can_have_independent_branches(self):
        deliverable_data = textwrap.dedent('''
        # NOTE(dhellmann): This launchpad setting is required.
        # See validate._NO_STABLE_BRANCH_CHECK.
        launchpad: gnocchi
        releases:
          - version: 0.0.3
            projects:
              - repo: openstack/release-test
                hash: 0cd17d1ee3b9284d36b2a0d370b49a6f0bbb9660
        branches:
          - name: stable/abc
            location: 0.0.3
        ''')
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_stable_branches(
            deliverable_info,
            'name',
            self.tmpdir,
            '_independent',
            self.msg,
        )
        self.msg.show_summary()
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(0, len(self.msg.errors))

    def test_explicit_stable_branch_type(self):
        deliverable_data = textwrap.dedent('''
        stable-branch-type: std
        releases:
          - version: 0.0.3
            projects:
              - repo: openstack/release-test
                hash: 0cd17d1ee3b9284d36b2a0d370b49a6f0bbb9660
        branches:
          - name: stable/ocata
            location: 0.0.3
        ''')
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_stable_branches(
            deliverable_info,
            'name',
            self.tmpdir,
            'ocata',
            self.msg,
        )
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(0, len(self.msg.errors))

    def test_explicit_stable_branch_type_invalid(self):
        deliverable_data = textwrap.dedent('''
        stable-branch-type: unknown
        releases:
          - version: 0.0.3
            projects:
              - repo: openstack/release-test
                hash: 0cd17d1ee3b9284d36b2a0d370b49a6f0bbb9660
        branches:
          - name: stable/ocata
            location: 0.0.3
        ''')
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_stable_branches(
            deliverable_info,
            'name',
            self.tmpdir,
            'ocata',
            self.msg,
        )
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(1, len(self.msg.errors))

    def test_tagless_stable_branch_type_bad_location_type(self):
        deliverable_data = textwrap.dedent('''
        stable-branch-type: tagless
        releases:
          - version: 0.0.3
            projects:
              - repo: openstack/release-test
                hash: 0cd17d1ee3b9284d36b2a0d370b49a6f0bbb9660
        branches:
          - name: stable/ocata
            location: 0.0.3
        ''')
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_stable_branches(
            deliverable_info,
            'name',
            self.tmpdir,
            'ocata',
            self.msg,
        )
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(1, len(self.msg.errors))

    def test_tagless_stable_branch_type_bad_location_value(self):
        deliverable_data = textwrap.dedent('''
        stable-branch-type: tagless
        releases:
          - version: 0.0.3
            projects:
              - repo: openstack/release-test
                hash: 0cd17d1ee3b9284d36b2a0d370b49a6f0bbb9660
        branches:
          - name: stable/ocata
            location:
              openstack/release-test: 0.0.3
        ''')
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_stable_branches(
            deliverable_info,
            'name',
            self.tmpdir,
            'ocata',
            self.msg,
        )
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(1, len(self.msg.errors))

    def test_tagless_stable_branch_type(self):
        deliverable_data = textwrap.dedent('''
        stable-branch-type: tagless
        releases:
          - version: 0.0.3
            projects:
              - repo: openstack/release-test
                hash: 0cd17d1ee3b9284d36b2a0d370b49a6f0bbb9660
        branches:
          - name: stable/ocata
            location:
              openstack/release-test: 0cd17d1ee3b9284d36b2a0d370b49a6f0bbb9660
        ''')
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_stable_branches(
            deliverable_info,
            'name',
            self.tmpdir,
            'ocata',
            self.msg,
        )
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(0, len(self.msg.errors))

    def test_tempest_plugin(self):
        deliverable_data = textwrap.dedent('''
        type: tempest-plugin
        releases:
          - version: 0.0.3
            projects:
              - repo: openstack/release-test
                hash: 0cd17d1ee3b9284d36b2a0d370b49a6f0bbb9660
        branches:
          - name: stable/ocata
            location:
              openstack/release-test: 0.0.3
        ''')
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_stable_branches(
            deliverable_info,
            'name',
            self.tmpdir,
            'ocata',
            self.msg,
        )
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(1, len(self.msg.errors))


class TestValidateFeatureBranches(base.BaseTestCase):

    def setUp(self):
        super(TestValidateFeatureBranches, self).setUp()
        self.tmpdir = self.useFixture(fixtures.TempDir()).path
        gitutils.clone_repo(self.tmpdir, 'openstack/release-test')
        self.msg = validate.MessageCollector()

    def test_location_not_a_dict(self):
        deliverable_data = textwrap.dedent('''
        releases:
          - version: 0.0.3
            projects:
              - repo: openstack/release-test
                hash: 0cd17d1ee3b9284d36b2a0d370b49a6f0bbb9660
        branches:
          - name: feature/abc
            location: 0.0.3
        ''')
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_feature_branches(
            deliverable_info,
            'name',
            self.tmpdir,
            self.msg,
        )
        self.msg.show_summary()
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(1, len(self.msg.errors))

    def test_location_not_a_sha(self):
        deliverable_data = textwrap.dedent('''
        releases:
          - version: 0.0.3
            projects:
              - repo: openstack/release-test
                hash: 0cd17d1ee3b9284d36b2a0d370b49a6f0bbb9660
        branches:
          - name: feature/abc
            location:
               openstack/release-test: 0.0.3
        ''')
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_feature_branches(
            deliverable_info,
            'name',
            self.tmpdir,
            self.msg,
        )
        self.msg.show_summary()
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(1, len(self.msg.errors))

    def test_location_a_sha(self):
        deliverable_data = textwrap.dedent('''
        releases:
          - version: 0.0.3
            projects:
              - repo: openstack/release-test
                hash: 0cd17d1ee3b9284d36b2a0d370b49a6f0bbb9660
        branches:
          - name: feature/abc
            location:
               openstack/release-test: 0cd17d1ee3b9284d36b2a0d370b49a6f0bbb9660
        ''')
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_feature_branches(
            deliverable_info,
            'name',
            self.tmpdir,
            self.msg,
        )
        self.msg.show_summary()
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(0, len(self.msg.errors))

    def test_badly_formatted_name(self):
        deliverable_data = textwrap.dedent('''
        releases:
          - version: 0.0.3
            projects:
              - repo: openstack/release-test
                hash: 0cd17d1ee3b9284d36b2a0d370b49a6f0bbb9660
        branches:
          - name: abc
            location:
               openstack/release-test: 0cd17d1ee3b9284d36b2a0d370b49a6f0bbb9660
        ''')
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_feature_branches(
            deliverable_info,
            'name',
            self.tmpdir,
            self.msg,
        )
        self.msg.show_summary()
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(1, len(self.msg.errors))

    def test_location_no_such_sha(self):
        deliverable_data = textwrap.dedent('''
        releases:
          - version: 0.0.3
            projects:
              - repo: openstack/release-test
                hash: 0cd17d1ee3b9284d36b2a0d370b49a6f0bbb9660
        branches:
          - name: feature/abc
            location:
               openstack/release-test: de2885f544637e6ee6139df7dc7bf937925804dd
        ''')
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_feature_branches(
            deliverable_info,
            'name',
            self.tmpdir,
            self.msg,
        )
        self.msg.show_summary()
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(1, len(self.msg.errors))

    def test_tempest_plugin(self):
        deliverable_data = textwrap.dedent('''
        type: tempest-plugin
        releases:
          - version: 0.0.3
            projects:
              - repo: openstack/release-test
                hash: 0cd17d1ee3b9284d36b2a0d370b49a6f0bbb9660
        branches:
          - name: feature/abc
            location:
               openstack/release-test: 0cd17d1ee3b9284d36b2a0d370b49a6f0bbb9660
        ''')
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_feature_branches(
            deliverable_info,
            'name',
            self.tmpdir,
            self.msg,
        )
        self.msg.show_summary()
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(1, len(self.msg.errors))


class TestValidateDriverfixesBranches(base.BaseTestCase):

    def setUp(self):
        super(TestValidateDriverfixesBranches, self).setUp()
        self.tmpdir = self.useFixture(fixtures.TempDir()).path
        gitutils.clone_repo(self.tmpdir, 'openstack/automaton')
        self.msg = validate.MessageCollector()

    def test_unknown_series(self):
        deliverable_data = textwrap.dedent('''
        releases:
          - version: 1.5.0
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
        branches:
          - name: driverfixes/abc
            location:
               openstack/automaton: be2885f544637e6ee6139df7dc7bf937925804dd
        ''')
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_driverfixes_branches(
            deliverable_info,
            'name',
            self.tmpdir,
            self.msg,
        )
        self.msg.show_summary()
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(1, len(self.msg.errors))

    def test_location_not_a_dict(self):
        deliverable_data = textwrap.dedent('''
        releases:
          - version: 1.5.0
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
        branches:
          - name: driverfixes/austin
            location: 1.5.0
        ''')
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_driverfixes_branches(
            deliverable_info,
            'name',
            self.tmpdir,
            self.msg,
        )
        self.msg.show_summary()
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(1, len(self.msg.errors))

    def test_location_not_a_sha(self):
        deliverable_data = textwrap.dedent('''
        releases:
          - version: 1.5.0
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
        branches:
          - name: driverfixes/austin
            location:
               openstack/automaton: 1.5.0
        ''')
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_driverfixes_branches(
            deliverable_info,
            'name',
            self.tmpdir,
            self.msg,
        )
        self.msg.show_summary()
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(1, len(self.msg.errors))

    def test_location_a_sha(self):
        deliverable_data = textwrap.dedent('''
        releases:
          - version: 1.5.0
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
        branches:
          - name: driverfixes/austin
            location:
               openstack/automaton: be2885f544637e6ee6139df7dc7bf937925804dd
        ''')
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_driverfixes_branches(
            deliverable_info,
            'name',
            self.tmpdir,
            self.msg,
        )
        self.msg.show_summary()
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(0, len(self.msg.errors))

    def test_badly_formatted_name(self):
        deliverable_data = textwrap.dedent('''
        releases:
          - version: 1.5.0
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
        branches:
          - name: austin
            location:
               openstack/automaton: be2885f544637e6ee6139df7dc7bf937925804dd
        ''')
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_driverfixes_branches(
            deliverable_info,
            'name',
            self.tmpdir,
            self.msg,
        )
        self.msg.show_summary()
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(1, len(self.msg.errors))

    def test_location_no_such_sha(self):
        deliverable_data = textwrap.dedent('''
        releases:
          - version: 1.5.0
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
        branches:
          - name: driverfixes/austin
            location:
               openstack/automaton: de2885f544637e6ee6139df7dc7bf937925804dd
        ''')
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_driverfixes_branches(
            deliverable_info,
            'name',
            self.tmpdir,
            self.msg,
        )
        self.msg.show_summary()
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(1, len(self.msg.errors))

    def test_tempest_plugin(self):
        deliverable_data = textwrap.dedent('''
        type: tempest-plugin
        releases:
          - version: 1.5.0
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
        branches:
          - name: driverfixes/austin
            location:
               openstack/automaton: be2885f544637e6ee6139df7dc7bf937925804dd
        ''')
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_driverfixes_branches(
            deliverable_info,
            'name',
            self.tmpdir,
            self.msg,
        )
        self.msg.show_summary()
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(1, len(self.msg.errors))


class TestValidateSeriesOpen(base.BaseTestCase):

    def setUp(self):
        super(TestValidateSeriesOpen, self).setUp()
        self.tmpdir = self.useFixture(fixtures.TempDir()).path
        self.msg = validate.MessageCollector()

    def test_series_is_open(self):
        series_a_dir = self.tmpdir + '/a'
        series_a_filename = series_a_dir + '/automaton.yaml'
        series_b_dir = self.tmpdir + '/b'
        series_b_filename = series_b_dir + '/automaton.yaml'
        os.makedirs(series_a_dir)
        os.makedirs(series_b_dir)
        branch_data = textwrap.dedent('''
        ---
        branches:
          - name: stable/a
            location: 1.4.0
        ''')
        deliverable_data = textwrap.dedent('''
        ---
        releases:
          - version: 1.5.0
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
        ''')
        with open(series_a_filename, 'w') as f:
            f.write(branch_data)
        with open(series_b_filename, 'w') as f:
            f.write(deliverable_data)
        deliv = deliverable.Deliverable(
            team='team',
            series='b',
            name='name',
            data=yamlutils.loads(deliverable_data),
        )
        validate.validate_series_open(
            deliv,
            series_b_filename,
            self.msg,
        )
        self.msg.show_summary()
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(0, len(self.msg.errors))

    def test_no_earlier_series(self):
        series_b_dir = self.tmpdir + '/b'
        series_b_filename = series_b_dir + '/automaton.yaml'
        os.makedirs(series_b_dir)
        deliverable_data = textwrap.dedent('''
        ---
        releases:
          - version: 1.5.0
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
        ''')
        with open(series_b_filename, 'w') as f:
            f.write(deliverable_data)
        deliv = deliverable.Deliverable(
            team='team',
            series='b',
            name='name',
            data=yamlutils.loads(deliverable_data),
        )
        validate.validate_series_open(
            deliv,
            series_b_filename,
            self.msg,
        )
        self.msg.show_summary()
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(0, len(self.msg.errors))

    def test_independent(self):
        deliverable_data = textwrap.dedent('''
        ---
        releases:
          - version: 1.5.0
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
        ''')
        deliv = deliverable.Deliverable(
            team='team',
            series='independent',
            name='name',
            data=yamlutils.loads(deliverable_data),
        )
        validate.validate_series_open(
            deliv,
            'filename',  # not used
            self.msg,
        )
        self.msg.show_summary()
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(0, len(self.msg.errors))

    def test_no_stable_branch(self):
        series_a_dir = self.tmpdir + '/a'
        series_a_filename = series_a_dir + '/automaton.yaml'
        series_b_dir = self.tmpdir + '/b'
        series_b_filename = series_b_dir + '/automaton.yaml'
        os.makedirs(series_a_dir)
        os.makedirs(series_b_dir)
        branch_data = textwrap.dedent('''
        ---
        ''')
        deliverable_data = textwrap.dedent('''
        ---
        releases:
          - version: 1.5.0
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
        ''')
        with open(series_a_filename, 'w') as f:
            f.write(branch_data)
        with open(series_b_filename, 'w') as f:
            f.write(deliverable_data)
        deliv = deliverable.Deliverable(
            team='team',
            series='b',
            name='name',
            data=yamlutils.loads(deliverable_data),
        )
        validate.validate_series_open(
            deliv,
            series_b_filename,
            self.msg,
        )
        self.msg.show_summary()
        self.assertEqual(1, len(self.msg.warnings))
        self.assertEqual(0, len(self.msg.errors))


class TestValidateSeriesFirst(base.BaseTestCase):

    def setUp(self):
        super(TestValidateSeriesFirst, self).setUp()
        self.tmpdir = self.useFixture(fixtures.TempDir()).path
        self.msg = validate.MessageCollector()

    def test_version_ok(self):
        series_a_dir = self.tmpdir + '/a'
        series_a_filename = series_a_dir + '/automaton.yaml'
        os.makedirs(series_a_dir)
        deliverable_data = textwrap.dedent('''
        ---
        releases:
          - version: 1.5.0
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
        ''')
        with open(series_a_filename, 'w') as f:
            f.write(deliverable_data)
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_series_first(
            deliverable_info,
            'a',
            self.msg,
        )
        self.msg.show_summary()
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(0, len(self.msg.errors))

    def test_ignore_if_second_release(self):
        series_a_dir = self.tmpdir + '/a'
        series_a_filename = series_a_dir + '/automaton.yaml'
        os.makedirs(series_a_dir)
        deliverable_data = textwrap.dedent('''
        ---
        releases:
          - version: 1.5.1
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
          - version: 1.5.2
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
        ''')
        with open(series_a_filename, 'w') as f:
            f.write(deliverable_data)
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_series_first(
            deliverable_info,
            'a',
            self.msg,
        )
        self.msg.show_summary()
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(0, len(self.msg.errors))

    def test_ignore_if_no_releases(self):
        series_a_dir = self.tmpdir + '/a'
        series_a_filename = series_a_dir + '/automaton.yaml'
        os.makedirs(series_a_dir)
        deliverable_data = textwrap.dedent('''
        ---
        releases:
        ''')
        with open(series_a_filename, 'w') as f:
            f.write(deliverable_data)
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_series_first(
            deliverable_info,
            'a',
            self.msg,
        )
        self.msg.show_summary()
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(0, len(self.msg.errors))

    def test_version_bad(self):
        series_a_dir = self.tmpdir + '/a'
        series_a_filename = series_a_dir + '/automaton.yaml'
        os.makedirs(series_a_dir)
        deliverable_data = textwrap.dedent('''
        ---
        releases:
          - version: 1.5.1
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
        ''')
        with open(series_a_filename, 'w') as f:
            f.write(deliverable_data)
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_series_first(
            deliverable_info,
            'a',
            self.msg,
        )
        self.msg.show_summary()
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(1, len(self.msg.errors))

    def test_beta_1(self):
        series_a_dir = self.tmpdir + '/a'
        series_a_filename = series_a_dir + '/automaton.yaml'
        os.makedirs(series_a_dir)
        deliverable_data = textwrap.dedent('''
        ---
        releases:
          - version: 1.5.1.0b1
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
        ''')
        with open(series_a_filename, 'w') as f:
            f.write(deliverable_data)
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_series_first(
            deliverable_info,
            'a',
            self.msg,
        )
        self.msg.show_summary()
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(0, len(self.msg.errors))

    def test_beta_2(self):
        series_a_dir = self.tmpdir + '/a'
        series_a_filename = series_a_dir + '/automaton.yaml'
        os.makedirs(series_a_dir)
        deliverable_data = textwrap.dedent('''
        ---
        releases:
          - version: 1.5.1.0b2
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
        ''')
        with open(series_a_filename, 'w') as f:
            f.write(deliverable_data)
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_series_first(
            deliverable_info,
            'a',
            self.msg,
        )
        self.msg.show_summary()
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(0, len(self.msg.errors))


class TestGuessDeliverableType(base.BaseTestCase):

    def setUp(self):
        super().setUp()
        self.msg = validate.MessageCollector()

    def test_explicit(self):
        self.assertEqual(
            'the-type',
            validate._guess_deliverable_type(
                'name',
                {'type': 'the-type'},
            ),
        )

    def test_implicit_tempest_plugin(self):
        self.assertEqual(
            'tempest-plugin',
            validate._guess_deliverable_type(
                'foo-tempest-plugin',
                {},
            ),
        )

    def test_default_other(self):
        self.assertEqual(
            'other',
            validate._guess_deliverable_type(
                'name',
                {},
            ),
        )


class TestValidateBranchPoints(base.BaseTestCase):

    def setUp(self):
        super(TestValidateBranchPoints, self).setUp()
        self.tmpdir = self.useFixture(fixtures.TempDir()).path
        gitutils.clone_repo(self.tmpdir, 'openstack/release-test')
        self.msg = validate.MessageCollector()

    def test_branch_does_not_exist(self):
        deliverable_data = textwrap.dedent('''
        releases:
          - version: 0.0.3
            projects:
              - repo: openstack/release-test
                hash: 0cd17d1ee3b9284d36b2a0d370b49a6f0bbb9660
        branches:
          - name: stable/ocata
            location: 0.0.3
        ''')
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_branch_points(
            deliverable_info,
            'name',
            self.tmpdir,
            self.msg,
        )
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(0, len(self.msg.errors))

    def test_branch_is_correct(self):
        deliverable_data = textwrap.dedent('''
        releases:
          - version: 0.8.0
            projects:
              - repo: openstack/release-test
                hash: a26e6a2e8a5e321b2e3517dbb01a7b9a56a8bfd5
        branches:
          - name: stable/newton
            location: 0.8.0
        ''')
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_branch_points(
            deliverable_info,
            'name',
            self.tmpdir,
            self.msg,
        )
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(0, len(self.msg.errors))

    def test_branch_moved(self):
        deliverable_data = textwrap.dedent('''
        releases:
          - version: 0.12.0
            projects:
              - repo: openstack/release-test
                hash: a26e6a2e8a5e321b2e3517dbb01a7b9a56a8bfd5
        branches:
          - name: stable/meiji
            location: 0.12.0  # this comes after the meiji branch
                              # was created at 0.0.2
        ''')
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_branch_points(
            deliverable_info,
            'name',
            self.tmpdir,
            self.msg,
        )
        self.assertEqual(0, len(self.msg.warnings))
        self.assertEqual(1, len(self.msg.errors))
