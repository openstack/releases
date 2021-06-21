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

import os
import textwrap
from unittest import mock

import fixtures
from oslotest import base

from openstack_releases.cmds import validate
from openstack_releases import defaults
from openstack_releases import deliverable
from openstack_releases import gitutils
from openstack_releases import series_status
from openstack_releases.tests import fixtures as or_fixtures
from openstack_releases import yamlutils


class TestDecorators(base.BaseTestCase):

    def setUp(self):
        super().setUp()
        self.ctx = validate.ValidationContext()

    def test_applies_to_current_skips(self):
        deliv = deliverable.Deliverable(
            team='team',
            series='austin',
            name='name',
            data={},
        )

        @validate.applies_to_current
        def f(deliv, context):
            self.fail('should not be called')

        f(deliv, self.ctx)

    def test_applies_to_current_runs(self):
        deliv = deliverable.Deliverable(
            team='team',
            series=defaults.RELEASE,
            name='name',
            data={},
        )
        called = []

        @validate.applies_to_current
        def f(deliv, context):
            called.append(1)

        f(deliv, self.ctx)
        self.assertTrue(called)

    def test_applies_to_released_skip(self):
        deliv = deliverable.Deliverable(
            team='team',
            series=defaults.RELEASE,
            name='name',
            data={
                'releases': [
                ],
            },
        )

        @validate.applies_to_released
        def f(deliv, context):
            self.fail('should not be called')

        f(deliv, self.ctx)

    def test_applies_to_released_runs(self):
        deliv = deliverable.Deliverable(
            team='team',
            series=defaults.RELEASE,
            name='name',
            data={
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
        called = []

        @validate.applies_to_released
        def f(deliv, context):
            called.append(1)

        f(deliv, self.ctx)
        self.assertTrue(called)

    def test_applies_to_cycle_skip(self):
        deliv = deliverable.Deliverable(
            team='team',
            series='independent',
            name='name',
            data={},
        )

        @validate.applies_to_cycle
        def f(deliv, context):
            self.fail('should not be called')

        f(deliv, self.ctx)

    def test_applies_to_cycle_runs(self):
        deliv = deliverable.Deliverable(
            team='team',
            series=defaults.RELEASE,
            name='name',
            data={},
        )
        called = []

        @validate.applies_to_cycle
        def f(deliv, context):
            called.append(1)

        f(deliv, self.ctx)
        self.assertTrue(called)


class TestValidateBugTracker(base.BaseTestCase):

    def setUp(self):
        super().setUp()
        self.ctx = validate.ValidationContext()

    def test_no_tracker(self):
        validate.validate_bugtracker(
            deliverable.Deliverable(
                team='team',
                series=defaults.RELEASE,
                name='name',
                data={},
            ),
            self.ctx,
        )
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))

    @mock.patch('requests.get')
    def test_launchpad_invalid_name(self, get):
        get.return_value = mock.Mock(status_code=404)
        validate.validate_bugtracker(
            deliverable.Deliverable(
                team='team',
                series=defaults.RELEASE,
                name='name',
                data={'launchpad': 'nonsense-name'},
            ),
            self.ctx,
        )
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))

    @mock.patch('requests.get')
    def test_launchpad_valid_name(self, get):
        get.return_value = mock.Mock(status_code=200)
        validate.validate_bugtracker(
            deliverable.Deliverable(
                team='team',
                series=defaults.RELEASE,
                name='name',
                data={'launchpad': 'oslo.config'},
            ),
            self.ctx,
        )
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

    @mock.patch('requests.get')
    def test_launchpad_timeout(self, get):
        import requests
        get.side_effect = requests.exceptions.ConnectionError('testing')
        validate.validate_bugtracker(
            deliverable.Deliverable(
                team='team',
                series=defaults.RELEASE,
                name='name',
                data={'launchpad': 'oslo.config'},
            ),
            self.ctx,
        )
        self.assertEqual(1, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

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
                "id": "openstack-infra/shade",
                "description": "Client library for OpenStack...",
            }
        ]
        validate.validate_bugtracker(
            deliverable.Deliverable(
                team='team',
                series=defaults.RELEASE,
                name='name',
                data={'storyboard': 'openstack-infra/shade'},
            ),
            self.ctx,
        )
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

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
                series=defaults.RELEASE,
                name='name',
                data={'storyboard': '-760'},
            ),
            self.ctx,
        )
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))


class TestValidateTeam(base.BaseTestCase):

    def setUp(self):
        super().setUp()
        self.ctx = validate.ValidationContext()

    def test_invalid_name(self):
        self.ctx._team_data = {}
        validate.validate_team(
            deliverable.Deliverable(
                team='nonsense-name',
                series=defaults.RELEASE,
                name='name',
                data={},
            ),
            self.ctx,
        )
        self.ctx.show_summary()
        self.assertEqual(1, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

    def test_valid_name(self):
        self.ctx._team_data = {'oslo': None}
        validate.validate_team(
            deliverable.Deliverable(
                team='oslo',
                series=defaults.RELEASE,
                name='name',
                data={},
            ),
            self.ctx,
        )
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))


class TestValidateReleaseNotes(base.BaseTestCase):

    def setUp(self):
        super().setUp()
        self.ctx = validate.ValidationContext()

    def test_no_link(self):
        validate.validate_release_notes(
            deliverable.Deliverable(
                team='team',
                series=defaults.RELEASE,
                name='name',
                data={},
            ),
            self.ctx,
        )
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

    @mock.patch('requests.get')
    def test_invalid_link(self, get):
        get.return_value = mock.Mock(status_code=404)
        validate.validate_release_notes(
            deliverable.Deliverable(
                team='team',
                series=defaults.RELEASE,
                name='name',
                data={
                    'release-notes': 'https://docs.openstack.org/no-such-page',
                },
            ),
            self.ctx,
        )
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))

    @mock.patch('requests.get')
    def test_valid_link(self, get):
        get.return_value = mock.Mock(status_code=200)
        validate.validate_release_notes(
            deliverable.Deliverable(
                team='team',
                series=defaults.RELEASE,
                name='name',
                data={'release-notes':
                      'https://docs.openstack.org/releasenotes/oslo.config'},
            ),
            self.ctx,
        )
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

    @mock.patch('requests.get')
    def test_invalid_link_multi(self, get):
        get.return_value = mock.Mock(status_code=404)
        validate.validate_release_notes(
            deliverable.Deliverable(
                team='team',
                series=defaults.RELEASE,
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
            self.ctx,
        )
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))

    @mock.patch('requests.get')
    def test_unknown_repo(self, get):
        get.return_value = mock.Mock(status_code=200)
        validate.validate_release_notes(
            deliverable.Deliverable(
                team='team',
                series=defaults.RELEASE,
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
            self.ctx,
        )
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))

    @mock.patch('requests.get')
    def test_valid_link_multi(self, get):
        get.return_value = mock.Mock(status_code=200)
        validate.validate_release_notes(
            deliverable.Deliverable(
                team='team',
                series=defaults.RELEASE,
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
            self.ctx,
        )
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))


class TestValidateModel(base.BaseTestCase):

    def setUp(self):
        super().setUp()
        self.ctx = validate.ValidationContext()

    def test_no_model_series(self):
        validate.validate_model(
            deliverable.Deliverable(
                team='team',
                series='ocata',
                name='name',
                data={},
            ),
            self.ctx,
        )
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))

    def test_no_model_independent(self):
        validate.validate_model(
            deliverable.Deliverable(
                team='team',
                series='independent',
                name='name',
                data={},
            ),
            self.ctx,
        )
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

    def test_with_model_independent_match(self):
        validate.validate_model(
            deliverable.Deliverable(
                team='team',
                series='independent',
                name='name',
                data={'release-model': 'independent'},
            ),
            self.ctx,
        )
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

    def test_with_model_independent_nomatch(self):
        validate.validate_model(
            deliverable.Deliverable(
                team='team',
                series='independent',
                name='name',
                data={'release-model': 'cycle-with-intermediary'},
            ),
            self.ctx,
        )
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))

    def test_with_model_abandoned_match(self):
        validate.validate_model(
            deliverable.Deliverable(
                team='team',
                series='independent',
                name='name',
                data={'release-model': 'abandoned'},
            ),
            self.ctx,
        )
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

    def test_with_model_abandoned_nomatch(self):
        validate.validate_model(
            deliverable.Deliverable(
                team='team',
                series='ocata',
                name='name',
                data={'release-model': 'abandoned'},
            ),
            self.ctx,
        )
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))

    def test_with_independent_and_model(self):
        validate.validate_model(
            deliverable.Deliverable(
                team='team',
                series='ocata',
                name='name',
                data={'release-model': 'independent'},
            ),
            self.ctx,
        )
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))

    def test_with_model_series(self):
        validate.validate_model(
            deliverable.Deliverable(
                team='team',
                series='ocata',
                name='name',
                data={'release-model': 'cycle-with-intermediary'},
            ),
            self.ctx,
        )
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

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
        validate.validate_model(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))


class TestValidateNotAbandoned(base.BaseTestCase):

    def setUp(self):
        super().setUp()
        self.ctx = validate.ValidationContext()
        gitutils.clone_repo(self.ctx.workdir, 'openstack/release-test')

    def test_new_release_on_abandoned_deliverable(self):
        deliv = deliverable.Deliverable(
            team='team',
            series='independent',
            name='name',
            data={
                'release-model': 'abandoned',
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
        validate.validate_deliverable_is_not_abandoned(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))


class TestValidateReleaseSHAExists(base.BaseTestCase):

    def setUp(self):
        super().setUp()
        self.ctx = validate.ValidationContext()
        self._make_repo()

    def _make_repo(self):
        self.repo = self.useFixture(
            or_fixtures.GitRepoFixture(
                self.ctx.workdir,
                'openstack/release-test',
            )
        )
        self.commit_1 = self.repo.add_file('testfile.txt')

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
        validate.validate_release_sha_exists(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))

    def test_valid_hash(self):
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
                          'hash': self.commit_1,
                          'tarball-base': 'openstack-release-test'},
                     ]}
                ],
            },
        )
        validate.validate_release_sha_exists(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

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
        validate.validate_release_sha_exists(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))

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
        validate.validate_release_sha_exists(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))


class TestValidateExistingTags(base.BaseTestCase):

    def setUp(self):
        super().setUp()
        self.ctx = validate.ValidationContext()
        self._make_repo()

    def _make_repo(self):
        self.repo = self.useFixture(
            or_fixtures.GitRepoFixture(
                self.ctx.workdir,
                'openstack/release-test',
            )
        )
        self.commit_1 = self.repo.add_file('testfile1.txt')
        self.repo.tag('0.8.0')
        self.commit_2 = self.repo.add_file('testfile2.txt')

    @mock.patch('openstack_releases.gitutils.checkout_ref')
    def test_valid(self, clone):
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
                          'hash': self.commit_1,
                          'tarball-base': 'openstack-release-test'},
                     ]}
                ],
            },
        )
        validate.validate_existing_tags(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

    def test_mismatch(self):
        deliv = deliverable.Deliverable(
            team='team',
            series='newton',
            name='name',
            data={
                'artifact-link-mode': 'none',
                'releases': [
                    {'version': '0.8.0',
                     'projects': [
                         {'repo': 'openstack/release-test',
                          'hash': self.commit_2},
                     ]}
                ],
            },
        )
        validate.validate_existing_tags(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))

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
        validate.validate_existing_tags(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))


class TestValidateReleaseBranchMembership(base.BaseTestCase):

    def setUp(self):
        super().setUp()
        self.ctx = validate.ValidationContext()
        gitutils.clone_repo(self.ctx.workdir, 'openstack/release-test')

    def test_hash_from_master_used_in_stable_release(self):
        deliv = deliverable.Deliverable(
            team='team',
            series='newton',
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
        validate.validate_release_branch_membership(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))

    def test_hash_from_master_used_in_stable_release2(self):
        deliv = deliverable.Deliverable(
            team='team',
            series='newton',
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
        validate.validate_release_branch_membership(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))

    def test_hash_from_stable_used_in_master_release(self):
        deliv = deliverable.Deliverable(
            team='team',
            series=defaults.RELEASE,
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
        validate.validate_release_branch_membership(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))

    def test_hash_from_master_used_after_default_branch_should_exist_but_does_not(self):
        gitutils.clone_repo(self.ctx.workdir, 'openstack/releases')
        deliv = deliverable.Deliverable(
            team='team',
            series='austin',
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
        validate.validate_release_branch_membership(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

    def test_not_descendent(self):
        deliv = deliverable.Deliverable(
            team='team',
            series='meiji',
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
        validate.validate_release_branch_membership(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(2, len(self.ctx.errors))

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
        validate.validate_release_branch_membership(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))


class TestValidateNewReleasesAtEnd(base.BaseTestCase):

    def setUp(self):
        super().setUp()
        self.ctx = validate.ValidationContext()
        gitutils.clone_repo(self.ctx.workdir, 'openstack/release-test')

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
        validate.validate_new_releases_at_end(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

    def test_not_at_end(self):
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
        validate.validate_new_releases_at_end(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))


class TestValidateNewReleasesInOpenSeries(base.BaseTestCase):

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
        self.ctx = validate.ValidationContext()
        gitutils.clone_repo(self.ctx.workdir, 'openstack/release-test')
        self.series_status = series_status.SeriesStatus(
            self._series_status_data)
        self.useFixture(fixtures.MockPatch(
            'openstack_releases.deliverable.Deliverable._series_status_data',
            self.series_status,
        ))

    def test_no_releases(self):
        # When we initialize a new series, we won't have any release
        # data. That's OK.
        deliv = deliverable.Deliverable(
            team='team',
            series='rocky',
            name='name',
            data={
                'artifact-link-mode': 'none',
                'releases': []
            }
        )
        validate.validate_new_releases_in_open_series(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

    def test_development(self):
        deliv = deliverable.Deliverable(
            team='team',
            series='rocky',
            name='name',
            data={
                'artifact-link-mode': 'none',
                'releases': [
                    {'version': '10.0.0',
                     'projects': [
                         {'repo': 'openstack/release-test',
                          'hash': 'a26e6a2e8a5e321b2e3517dbb01a7b9a56a8bfd5',
                          'tarball-base': 'openstack-release-test'},
                     ]},
                ],
            }
        )
        validate.validate_new_releases_in_open_series(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

    def test_maintained(self):
        deliv = deliverable.Deliverable(
            team='team',
            series='queens',
            name='name',
            data={
                'artifact-link-mode': 'none',
                'releases': [
                    {'version': '10.0.0',
                     'projects': [
                         {'repo': 'openstack/release-test',
                          'hash': 'a26e6a2e8a5e321b2e3517dbb01a7b9a56a8bfd5',
                          'tarball-base': 'openstack-release-test'},
                     ]},
                ],
            }
        )
        validate.validate_new_releases_in_open_series(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

    def test_extended_maintaintenance(self):
        deliv = deliverable.Deliverable(
            team='team',
            series='ocata',
            name='name',
            data={
                'artifact-link-mode': 'none',
                'releases': [
                    {'version': '10.0.0',
                     'projects': [
                         {'repo': 'openstack/release-test',
                          'hash': 'a26e6a2e8a5e321b2e3517dbb01a7b9a56a8bfd5',
                          'tarball-base': 'openstack-release-test'},
                     ]},
                ],
            }
        )
        validate.validate_new_releases_in_open_series(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))

    def test_end_of_life(self):
        deliv = deliverable.Deliverable(
            team='team',
            series='newton',
            name='name',
            data={
                'artifact-link-mode': 'none',
                'releases': [
                    {'version': '10.0.0',
                     'projects': [
                         {'repo': 'openstack/release-test',
                          'hash': 'a26e6a2e8a5e321b2e3517dbb01a7b9a56a8bfd5',
                          'tarball-base': 'openstack-release-test'},
                     ]},
                ],
            }
        )
        validate.validate_new_releases_in_open_series(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))

    def test_eol_in_end_of_life(self):
        deliv = deliverable.Deliverable(
            team='team',
            series='newton',
            name='name',
            data={
                'artifact-link-mode': 'none',
                'releases': [
                    {'version': 'newton-eol',
                     'projects': [
                         {'repo': 'openstack/release-test',
                          'hash': 'a26e6a2e8a5e321b2e3517dbb01a7b9a56a8bfd5',
                          'tarball-base': 'openstack-release-test'},
                     ]},
                ],
            }
        )
        validate.validate_new_releases_in_open_series(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

    def test_em_in_end_of_life(self):
        deliv = deliverable.Deliverable(
            team='team',
            series='newton',
            name='name',
            data={
                'artifact-link-mode': 'none',
                'releases': [
                    {'version': 'newton-em',
                     'projects': [
                         {'repo': 'openstack/release-test',
                          'hash': 'a26e6a2e8a5e321b2e3517dbb01a7b9a56a8bfd5',
                          'tarball-base': 'openstack-release-test'},
                     ]},
                ],
            }
        )
        validate.validate_new_releases_in_open_series(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))


class TestValidateVersionNumbers(base.BaseTestCase):

    def setUp(self):
        super().setUp()
        self.ctx = validate.ValidationContext()
        gitutils.clone_repo(self.ctx.workdir, 'openstack/release-test')

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
        validate.validate_version_numbers(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))

    @mock.patch('openstack_releases.requirements.find_bad_lower_bound_increases')
    def test_generic_model(self, mock_lower_bound):
        deliv = deliverable.Deliverable(
            team='team',
            series='ocata',
            name='name',
            data={
                'release-type': 'generic',
                'releases': [
                    {'version': '0.9.0',
                     'projects': [
                         {'repo': 'openstack/release-test',
                          'hash': '04ee20f0bfe8774935de33b75e87fb3b858d0733'},
                     ]},
                    {'version': '0.9.1',
                     'projects': [
                         {'repo': 'openstack/release-test',
                          'hash': 'a26e6a2e8a5e321b2e3517dbb01a7b9a56a8bfd5'},
                     ]}
                ],
            }
        )
        validate.validate_version_numbers(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))
        self.assertFalse(mock_lower_bound.called)

    def test_valid_version(self):
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
        validate.validate_version_numbers(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

    def test_eol_valid_version(self):
        deliv = deliverable.Deliverable(
            team='team',
            series='ocata',
            name='name',
            data={
                'artifact-link-mode': 'none',
                'releases': [
                    {'version': 'ocata-eol',
                     'projects': [
                         {'repo': 'openstack/release-test',
                          'hash': 'a26e6a2e8a5e321b2e3517dbb01a7b9a56a8bfd5'},
                     ]}
                ],
            }
        )
        validate.validate_version_numbers(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

    def test_em_valid_version(self):
        deliv = deliverable.Deliverable(
            team='team',
            series='ocata',
            name='name',
            data={
                'artifact-link-mode': 'none',
                'releases': [
                    {'version': 'ocata-em',
                     'projects': [
                         {'repo': 'openstack/release-test',
                          'hash': 'a26e6a2e8a5e321b2e3517dbb01a7b9a56a8bfd5'},
                     ]}
                ],
            }
        )
        validate.validate_version_numbers(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

    def test_eol_wrong_branch(self):
        deliv = deliverable.Deliverable(
            team='team',
            series='ocata',
            name='name',
            data={
                'artifact-link-mode': 'none',
                'releases': [
                    {'version': 'newton-eol',
                     'projects': [
                         {'repo': 'openstack/release-test',
                          'hash': 'a26e6a2e8a5e321b2e3517dbb01a7b9a56a8bfd5'},
                     ]}
                ],
            }
        )
        validate.validate_version_numbers(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))

    def test_em_wrong_branch(self):
        deliv = deliverable.Deliverable(
            team='team',
            series='ocata',
            name='name',
            data={
                'artifact-link-mode': 'none',
                'releases': [
                    {'version': 'newton-em',
                     'projects': [
                         {'repo': 'openstack/release-test',
                          'hash': 'a26e6a2e8a5e321b2e3517dbb01a7b9a56a8bfd5'},
                     ]}
                ],
            }
        )
        validate.validate_version_numbers(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))

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
        validate.validate_version_numbers(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))


class TestGetReleaseType(base.BaseTestCase):

    def setUp(self):
        super().setUp()
        self.tmpdir = self.useFixture(fixtures.TempDir()).path
        self.ctx = validate.ValidationContext()

    def test_explicit(self):
        deliv = deliverable.Deliverable(
            team='team',
            series=defaults.RELEASE,
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
            series=defaults.RELEASE,
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
            series=defaults.RELEASE,
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
            series=defaults.RELEASE,
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
            series=defaults.RELEASE,
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
            series=defaults.RELEASE,
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
            series=defaults.RELEASE,
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
            series=defaults.RELEASE,
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
        super().setUp()
        self.tmpdir = self.useFixture(fixtures.TempDir()).path
        self.ctx = validate.ValidationContext()
        self.useFixture(fixtures.MonkeyPatch(
            'openstack_releases.cmds.validate.includes_new_tag',
            mock.Mock(return_value=True),
        ))

    @mock.patch('openstack_releases.gitutils.check_branch_sha')
    @mock.patch('openstack_releases.puppetutils.get_version')
    @mock.patch('openstack_releases.puppetutils.looks_like_a_module')
    def test_valid_version(self, llam, get_version, cbs):
        llam.return_value = True
        get_version.return_value = '99.1.0'
        cbs.return_value = True
        gitutils.clone_repo(self.ctx.workdir, 'openstack/puppet-watcher')
        deliv = deliverable.Deliverable(
            team='team',
            series='ocata',
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
        validate.validate_version_numbers(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

    @mock.patch('openstack_releases.gitutils.check_branch_sha')
    @mock.patch('openstack_releases.puppetutils.get_version')
    @mock.patch('openstack_releases.puppetutils.looks_like_a_module')
    def test_mismatched_version(self, llam, get_version, cbs):
        llam.return_value = True
        get_version.return_value = '99.1.0'
        cbs.return_value = True
        gitutils.clone_repo(self.ctx.workdir, 'openstack/puppet-watcher')
        deliv = deliverable.Deliverable(
            team='team',
            series=defaults.RELEASE,
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
        validate.validate_version_numbers(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))


class TestValidateTarballBase(base.BaseTestCase):

    def setUp(self):
        super().setUp()
        self.ctx = validate.ValidationContext()

    @mock.patch('openstack_releases.project_config.require_release_jobs_for_repo')
    @mock.patch('openstack_releases.pythonutils.get_sdist_name')
    def test_default_ok(self, gsn, jobs):
        deliv = deliverable.Deliverable(
            team='team',
            series=defaults.RELEASE,
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
        validate.clone_deliverable(deliv, self.ctx)
        validate.validate_tarball_base(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

    @mock.patch('openstack_releases.project_config.require_release_jobs_for_repo')
    @mock.patch('openstack_releases.pythonutils.get_sdist_name')
    def test_ignored_link_mode_none(self, gsn, jobs):
        deliv = deliverable.Deliverable(
            team='team',
            series=defaults.RELEASE,
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
        validate.clone_deliverable(deliv, self.ctx)
        validate.validate_tarball_base(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

    @mock.patch('openstack_releases.project_config.require_release_jobs_for_repo')
    @mock.patch('openstack_releases.pythonutils.get_sdist_name')
    def test_default_invalid(self, gsn, jobs):
        deliv = deliverable.Deliverable(
            team='team',
            series=defaults.RELEASE,
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
        validate.clone_deliverable(deliv, self.ctx)
        validate.validate_tarball_base(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))

    @mock.patch('openstack_releases.project_config.require_release_jobs_for_repo')
    @mock.patch('openstack_releases.pythonutils.get_sdist_name')
    def test_explicit_ok(self, gsn, jobs):
        deliv = deliverable.Deliverable(
            team='team',
            series=defaults.RELEASE,
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
        validate.clone_deliverable(deliv, self.ctx)
        validate.validate_tarball_base(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

    @mock.patch('openstack_releases.project_config.require_release_jobs_for_repo')
    @mock.patch('openstack_releases.pythonutils.get_sdist_name')
    def test_explicit_invalid(self, gsn, jobs):
        deliv = deliverable.Deliverable(
            team='team',
            series=defaults.RELEASE,
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
        validate.clone_deliverable(deliv, self.ctx)
        validate.validate_tarball_base(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))


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
        self.ctx = validate.ValidationContext()
        self.ctx._team_data = self.team_data

    def test_all_repos(self):
        # The repos in the tag, governance, and repository-settings
        # match.
        deliv = deliverable.Deliverable(
            team='team',
            series=defaults.RELEASE,
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
        validate.validate_new_releases(deliv, self.ctx)
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

    def test_extra_repo_gov(self):
        # The tag includes a repo not in governance.
        deliv = deliverable.Deliverable(
            team='team',
            series=defaults.RELEASE,
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
        validate.validate_new_releases(deliv, self.ctx)
        self.assertEqual(1, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

    def test_missing_repo_gov(self):
        # The tag is missing a repo in governance.
        deliv = deliverable.Deliverable(
            team='team',
            series=defaults.RELEASE,
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
        validate.validate_new_releases(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(1, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

    def test_extra_repo_info(self):
        # The tag has a repo not in repository-settings or governance
        # (2 warnings).
        deliv = deliverable.Deliverable(
            team='team',
            series=defaults.RELEASE,
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
        validate.validate_new_releases(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))

    def test_missing_repo_info(self):
        # The tag is missing a repository that is in
        # repository-settings.
        deliv = deliverable.Deliverable(
            team='team',
            series=defaults.RELEASE,
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
        validate.validate_new_releases(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))


class TestValidateBranchPrefixes(base.BaseTestCase):

    def setUp(self):
        super().setUp()
        self.ctx = validate.ValidationContext()

    def test_invalid_prefix(self):
        deliv = deliverable.Deliverable(
            team='team',
            series=defaults.RELEASE,
            name='release-test',
            data={
                'branches': [
                    {'name': 'invalid/branch',
                     'location': ''},
                ],
            }
        )
        validate.validate_branch_prefixes(deliv, self.ctx)
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))

    def test_valid_prefix(self):
        for prefix in validate._VALID_BRANCH_PREFIXES:
            deliv = deliverable.Deliverable(
                team='team',
                series=defaults.RELEASE,
                name='release-test',
                data={
                    'branches': [
                        {'name': '%s/branch' % prefix,
                         'location': ''},
                    ],
                }
            )
            validate.validate_branch_prefixes(deliv, self.ctx)
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))


class TestValidateStableBranches(base.BaseTestCase):

    def setUp(self):
        super().setUp()
        self.ctx = validate.ValidationContext()
        gitutils.clone_repo(self.ctx.workdir, 'openstack/release-test')

    def test_version_in_deliverable(self):
        deliverable_data = textwrap.dedent('''
        releases:
          - version: 99.0.3
            projects:
              - repo: openstack/release-test
                hash: 0cd17d1ee3b9284d36b2a0d370b49a6f0bbb9660
        branches:
          - name: stable/ocata
            location: 99.0.3
        repository-settings:
          openstack/release-test: {}
        ''')
        deliv = deliverable.Deliverable(
            team='team',
            series='ocata',
            name='release-test',
            data=yamlutils.loads(deliverable_data),
        )
        validate.validate_stable_branches(deliv, self.ctx)
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

    def test_badly_formatted_name(self):
        deliverable_data = textwrap.dedent('''
        releases:
          - version: 99.0.3
            projects:
              - repo: openstack/release-test
                hash: 0cd17d1ee3b9284d36b2a0d370b49a6f0bbb9660
        branches:
          - name: ocata
            location: 99.0.3
        repository-settings:
          openstack/release-test: {}
        ''')
        deliv = deliverable.Deliverable(
            team='team',
            series='ocata',
            name='release-test',
            data=yamlutils.loads(deliverable_data),
        )
        validate.validate_stable_branches(deliv, self.ctx)
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))

    def test_version_not_in_deliverable(self):
        deliverable_data = textwrap.dedent('''
        releases:
          - version: 99.0.3
            projects:
              - repo: openstack/release-test
                hash: 0cd17d1ee3b9284d36b2a0d370b49a6f0bbb9660
        branches:
          - name: stable/ocata
            location: 99.0.4
        repository-settings:
          openstack/release-test: {}
        ''')
        deliv = deliverable.Deliverable(
            team='team',
            series='ocata',
            name='release-test',
            data=yamlutils.loads(deliverable_data),
        )
        validate.validate_stable_branches(deliv, self.ctx)
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))

    def test_version_not_last(self):
        deliverable_data = textwrap.dedent('''
        releases:
          - version: 99.0.3
            projects:
              - repo: openstack/release-test
                hash: 0cd17d1ee3b9284d36b2a0d370b49a6f0bbb9660
          - version: 99.0.4
            projects:
              - repo: openstack/release-test
                hash: 0cd17d1ee3b9284d36b2a0d370b49a6f0bbb9660
        branches:
          - name: stable/ocata
            location: 99.0.3
        repository-settings:
          openstack/release-test: {}
        ''')
        deliv = deliverable.Deliverable(
            team='team',
            series='ocata',
            name='release-test',
            data=yamlutils.loads(deliverable_data),
        )
        validate.validate_stable_branches(deliv, self.ctx)
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))

    def test_mismatched_series_cycle(self):
        deliverable_data = textwrap.dedent('''
        releases:
          - version: 99.0.3
            projects:
              - repo: openstack/release-test
                hash: 0cd17d1ee3b9284d36b2a0d370b49a6f0bbb9660
        branches:
          - name: stable/does-not-exist
            location: 99.0.3
        repository-settings:
          openstack/release-test: {}
        ''')
        deliv = deliverable.Deliverable(
            team='team',
            series='series-name-does-not-match',
            name='release-test',
            data=yamlutils.loads(deliverable_data),
        )
        validate.validate_stable_branches(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))

    def test_without_repository_settings(self):
        deliverable_data = textwrap.dedent('''
        releases:
          - version: 99.0.3
            projects:
              - repo: openstack/release-test
                hash: 0cd17d1ee3b9284d36b2a0d370b49a6f0bbb9660
        branches:
          - name: stable/does-not-exist
            location: 99.0.3
        repository-settings:
          openstack/release-test: {}
        ''')
        deliv = deliverable.Deliverable(
            team='team',
            series='series-name-does-not-match',
            name='release-test',
            data=yamlutils.loads(deliverable_data),
        )
        validate.validate_stable_branches(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))

    def test_unknown_series_independent(self):
        deliverable_data = textwrap.dedent('''
        releases:
          - version: 99.0.3
            projects:
              - repo: openstack/release-test
                hash: 0cd17d1ee3b9284d36b2a0d370b49a6f0bbb9660
        branches:
          - name: stable/abc
            location: 99.0.3
        repository-settings:
          openstack/release-test: {}
        ''')
        deliv = deliverable.Deliverable(
            team='team',
            series='independent',
            name='release-test',
            data=yamlutils.loads(deliverable_data),
        )
        validate.validate_stable_branches(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))

    def test_can_have_independent_branches(self):
        deliverable_data = textwrap.dedent('''
        # NOTE(dhellmann): This launchpad setting is required.
        # See validate._NO_STABLE_BRANCH_CHECK.
        launchpad: gnocchi
        releases:
          - version: 99.0.3
            projects:
              - repo: openstack/release-test
                hash: 0cd17d1ee3b9284d36b2a0d370b49a6f0bbb9660
        branches:
          - name: stable/abc
            location: 99.0.3
        repository-settings:
          openstack/release-test: {}
        ''')
        deliv = deliverable.Deliverable(
            team='team',
            series='independent',
            name='release-test',
            data=yamlutils.loads(deliverable_data),
        )
        validate.validate_stable_branches(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

    def test_explicit_stable_branch_type(self):
        deliverable_data = textwrap.dedent('''
        stable-branch-type: std
        releases:
          - version: 99.0.3
            projects:
              - repo: openstack/release-test
                hash: 0cd17d1ee3b9284d36b2a0d370b49a6f0bbb9660
        branches:
          - name: stable/ocata
            location: 99.0.3
        repository-settings:
          openstack/release-test: {}
        ''')
        deliv = deliverable.Deliverable(
            team='team',
            series='ocata',
            name='release-test',
            data=yamlutils.loads(deliverable_data),
        )
        validate.validate_stable_branches(deliv, self.ctx)
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

    def test_explicit_stable_branch_type_invalid(self):
        deliverable_data = textwrap.dedent('''
        stable-branch-type: unknown
        releases:
          - version: 99.0.3
            projects:
              - repo: openstack/release-test
                hash: 0cd17d1ee3b9284d36b2a0d370b49a6f0bbb9660
        branches:
          - name: stable/ocata
            location: 99.0.3
        repository-settings:
          openstack/release-test: {}
        ''')
        deliv = deliverable.Deliverable(
            team='team',
            series='ocata',
            name='release-test',
            data=yamlutils.loads(deliverable_data),
        )
        validate.validate_stable_branches(deliv, self.ctx)
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))

    def test_std_with_versions_stable_branch_type(self):
        deliverable_data = textwrap.dedent('''
        stable-branch-type: std-with-versions
        releases:
          - version: 99.0.3
            projects:
              - repo: openstack/release-test
                hash: 0cd17d1ee3b9284d36b2a0d370b49a6f0bbb9660
        branches:
          - name: stable/99.0
            location: 99.0.3
        repository-settings:
          openstack/release-test: {}
        ''')
        deliv = deliverable.Deliverable(
            team='team',
            series='ocata',
            name='release-test',
            data=yamlutils.loads(deliverable_data),
        )
        validate.validate_stable_branches(deliv, self.ctx)
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

    def test_std_with_versions_normal_stable_branch_type(self):
        deliverable_data = textwrap.dedent('''
        stable-branch-type: std-with-versions
        releases:
          - version: 99.0.3
            projects:
              - repo: openstack/release-test
                hash: 0cd17d1ee3b9284d36b2a0d370b49a6f0bbb9660
        branches:
          - name: stable/ocata
            location: 99.0.3
        repository-settings:
          openstack/release-test: {}
        ''')
        deliv = deliverable.Deliverable(
            team='team',
            series='ocata',
            name='release-test',
            data=yamlutils.loads(deliverable_data),
        )
        validate.validate_stable_branches(deliv, self.ctx)
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

    def test_tagless_stable_branch_type_bad_location_type(self):
        deliverable_data = textwrap.dedent('''
        stable-branch-type: tagless
        releases:
          - version: 99.0.3
            projects:
              - repo: openstack/release-test
                hash: 0cd17d1ee3b9284d36b2a0d370b49a6f0bbb9660
        branches:
          - name: stable/ocata
            location: 99.0.3
        repository-settings:
          openstack/release-test: {}
        ''')
        deliv = deliverable.Deliverable(
            team='team',
            series='ocata',
            name='release-test',
            data=yamlutils.loads(deliverable_data),
        )
        validate.validate_stable_branches(deliv, self.ctx)
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))

    def test_tagless_stable_branch_type_bad_location_value(self):
        deliverable_data = textwrap.dedent('''
        stable-branch-type: tagless
        releases:
          - version: 99.0.3
            projects:
              - repo: openstack/release-test
                hash: 0cd17d1ee3b9284d36b2a0d370b49a6f0bbb9660
        branches:
          - name: stable/ocata
            location:
              openstack/release-test: 99.0.3
        repository-settings:
          openstack/release-test: {}
        ''')
        deliv = deliverable.Deliverable(
            team='team',
            series='ocata',
            name='release-test',
            data=yamlutils.loads(deliverable_data),
        )
        validate.validate_stable_branches(deliv, self.ctx)
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))

    def test_tagless_stable_branch_type(self):
        deliverable_data = textwrap.dedent('''
        stable-branch-type: tagless
        releases:
          - version: 99.0.3
            projects:
              - repo: openstack/release-test
                hash: 0cd17d1ee3b9284d36b2a0d370b49a6f0bbb9660
        branches:
          - name: stable/ocata
            location:
              openstack/release-test: 0cd17d1ee3b9284d36b2a0d370b49a6f0bbb9660
        repository-settings:
          openstack/release-test: {}
        ''')
        deliv = deliverable.Deliverable(
            team='team',
            series='ocata',
            name='release-test',
            data=yamlutils.loads(deliverable_data),
        )
        validate.validate_stable_branches(deliv, self.ctx)
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

    def test_tempest_plugin(self):
        deliverable_data = textwrap.dedent('''
        type: tempest-plugin
        releases:
          - version: 99.0.3
            projects:
              - repo: openstack/release-test
                hash: 0cd17d1ee3b9284d36b2a0d370b49a6f0bbb9660
        branches:
          - name: stable/ocata
            location:
              openstack/release-test: 99.0.3
        repository-settings:
          openstack/release-test: {}
        ''')
        deliv = deliverable.Deliverable(
            team='team',
            series='ocata',
            name='release-test',
            data=yamlutils.loads(deliverable_data),
        )
        validate.validate_stable_branches(deliv, self.ctx)
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))

    def test_none_stable_branch_type(self):
        deliverable_data = textwrap.dedent('''
        type: other
        stable-branch-type: none
        releases:
          - version: 99.0.3
            projects:
              - repo: openstack/release-test
                hash: 0cd17d1ee3b9284d36b2a0d370b49a6f0bbb9660
        branches:
          - name: stable/ocata
            location:
              openstack/release-test: 99.0.3
        repository-settings:
          openstack/release-test: {}
        ''')
        deliv = deliverable.Deliverable(
            team='team',
            series='ocata',
            name='release-test',
            data=yamlutils.loads(deliverable_data),
        )
        validate.validate_stable_branches(deliv, self.ctx)
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))


class TestValidateFeatureBranches(base.BaseTestCase):

    def setUp(self):
        super().setUp()
        self.ctx = validate.ValidationContext()
        gitutils.clone_repo(self.ctx.workdir, 'openstack/release-test')

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
        deliv = deliverable.Deliverable(
            team='team',
            series='ocata',
            name='release-test',
            data=yamlutils.loads(deliverable_data),
        )
        validate.validate_feature_branches(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))

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
        deliv = deliverable.Deliverable(
            team='team',
            series='ocata',
            name='release-test',
            data=yamlutils.loads(deliverable_data),
        )
        validate.validate_feature_branches(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))

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
        deliv = deliverable.Deliverable(
            team='team',
            series='ocata',
            name='release-test',
            data=yamlutils.loads(deliverable_data),
        )
        validate.validate_feature_branches(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

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
        deliv = deliverable.Deliverable(
            team='team',
            series='ocata',
            name='release-test',
            data=yamlutils.loads(deliverable_data),
        )
        validate.validate_feature_branches(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))

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
        deliv = deliverable.Deliverable(
            team='team',
            series='ocata',
            name='release-test',
            data=yamlutils.loads(deliverable_data),
        )
        validate.validate_feature_branches(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))

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
        deliv = deliverable.Deliverable(
            team='team',
            series='ocata',
            name='release-test',
            data=yamlutils.loads(deliverable_data),
        )
        validate.validate_feature_branches(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))


class TestValidateSeriesOpen(base.BaseTestCase):

    def setUp(self):
        super().setUp()
        self.tmpdir = self.useFixture(fixtures.TempDir()).path
        self.ctx = validate.ValidationContext()
        self.useFixture(fixtures.MonkeyPatch(
            'openstack_releases.cmds.validate.includes_new_tag',
            mock.Mock(return_value=True),
        ))

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
        self.ctx.set_filename(series_b_filename)
        validate.validate_series_open(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

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
        self.ctx.set_filename(series_b_filename)
        validate.validate_series_open(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

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
        self.ctx.set_filename('filename')  # not used
        validate.validate_series_open(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

    def test_no_stable_branch(self):
        series_a_dir = self.tmpdir + '/a'
        series_a_filename = series_a_dir + '/automaton.yaml'
        series_b_dir = self.tmpdir + '/' + defaults.RELEASE
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
            series=defaults.RELEASE,
            name='name',
            data=yamlutils.loads(deliverable_data),
        )
        self.ctx.set_filename(series_b_filename)
        validate.validate_series_open(deliv, self.ctx)
        self.ctx.show_summary()
        self.assertEqual(1, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))


class TestValidateSeriesFirst(base.BaseTestCase):

    def setUp(self):
        super().setUp()
        self.tmpdir = self.useFixture(fixtures.TempDir()).path
        self.ctx = validate.ValidationContext()
        self.useFixture(fixtures.MonkeyPatch(
            'openstack_releases.cmds.validate.includes_new_tag',
            mock.Mock(return_value=True),
        ))

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
        deliv = deliverable.Deliverable(
            team='team',
            series='a',
            name='name',
            data=yamlutils.loads(deliverable_data),
        )
        validate.validate_series_first(
            deliv,
            self.ctx,
        )
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

    def test_version_ko(self):
        series_a_dir = self.tmpdir + '/a'
        series_a_filename = series_a_dir + '/automaton.yaml'
        os.makedirs(series_a_dir)
        deliverable_data = textwrap.dedent('''
        ---
        releases:
          - version: 1.1.1
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
        ''')
        with open(series_a_filename, 'w') as f:
            f.write(deliverable_data)
        deliv = deliverable.Deliverable(
            team='team',
            series='a',
            name='name',
            data=yamlutils.loads(deliverable_data),
        )
        validate.validate_series_first(
            deliv,
            self.ctx,
        )
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        # Starting a cycle with a bugfix version (1.1.1) isn't allowed,
        # so, in this case our validation should fail accordingly to that
        # rule.
        self.assertEqual(1, len(self.ctx.errors))

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
        deliv = deliverable.Deliverable(
            team='team',
            series='a',
            name='name',
            data=yamlutils.loads(deliverable_data),
        )
        validate.validate_series_first(
            deliv,
            self.ctx,
        )
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

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
        deliv = deliverable.Deliverable(
            team='team',
            series='a',
            name='name',
            data=yamlutils.loads(deliverable_data),
        )
        validate.validate_series_first(
            deliv,
            self.ctx,
        )
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

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
        deliv = deliverable.Deliverable(
            team='team',
            series='a',
            name='name',
            data=yamlutils.loads(deliverable_data),
        )
        validate.validate_series_first(
            deliv,
            self.ctx,
        )
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))

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
        deliv = deliverable.Deliverable(
            team='team',
            series='a',
            name='name',
            data=yamlutils.loads(deliverable_data),
        )
        validate.validate_series_first(
            deliv,
            self.ctx,
        )
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

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
        deliv = deliverable.Deliverable(
            team='team',
            series='a',
            name='name',
            data=yamlutils.loads(deliverable_data),
        )
        validate.validate_series_first(
            deliv,
            self.ctx,
        )
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

    def test_branchless(self):
        series_a_dir = self.tmpdir + '/a'
        series_a_filename = series_a_dir + '/sahara-tests.yaml'
        os.makedirs(series_a_dir)
        deliverable_data = textwrap.dedent('''
        ---
        type: tempest-plugin
        releases:
          - version: 0.9.1
            projects:
              - repo: openstack/sahara-tests
                hash: 1e016405f8dbdf265374700d2fb8f8e2a9460805
        ''')
        with open(series_a_filename, 'w') as f:
            f.write(deliverable_data)
        deliv = deliverable.Deliverable(
            team='team',
            series='a',
            name='name',
            data=yamlutils.loads(deliverable_data),
        )
        validate.validate_series_first(
            deliv,
            self.ctx,
        )
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))


class TestValidateSeriesFinal(base.BaseTestCase):

    def setUp(self):
        super().setUp()
        self.tmpdir = self.useFixture(fixtures.TempDir()).path
        self.ctx = validate.ValidationContext()
        self.useFixture(fixtures.MonkeyPatch(
            'openstack_releases.cmds.validate.includes_new_tag',
            mock.Mock(return_value=True),
        ))

    def test_no_releases(self):
        deliverable_data = yamlutils.loads(textwrap.dedent('''
        ---
        team: Release Management
        '''))
        deliv = deliverable.Deliverable(
            None,
            defaults.RELEASE,
            'test',
            deliverable_data,
        )
        validate.validate_series_final(
            deliv,
            self.ctx,
        )
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

    def test_only_rc(self):
        deliverable_data = yamlutils.loads(textwrap.dedent('''
        ---
        team: Release Management
        releases:
          - version: 1.5.1.0rc1
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
        '''))
        deliv = deliverable.Deliverable(
            None,
            defaults.RELEASE,
            'test',
            deliverable_data,
        )
        validate.validate_series_final(
            deliv,
            self.ctx,
        )
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

    def test_no_rc(self):
        deliverable_data = yamlutils.loads(textwrap.dedent('''
        ---
        team: Release Management
        releases:
          - version: 1.5.1
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
          - version: 1.5.2
            projects:
              - repo: openstack/automaton
                hash: ce2885f544637e6ee6139df7dc7bf937925804dd
        '''))
        deliv = deliverable.Deliverable(
            None,
            defaults.RELEASE,
            'test',
            deliverable_data,
        )
        validate.validate_series_final(
            deliv,
            self.ctx,
        )
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

    def test_rc_with_final_match(self):
        deliverable_data = yamlutils.loads(textwrap.dedent('''
        ---
        team: Release Management
        releases:
          - version: 1.5.1.0rc1
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
          - version: 1.5.1
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
        '''))
        deliv = deliverable.Deliverable(
            None,
            defaults.RELEASE,
            'test',
            deliverable_data,
        )
        validate.validate_series_final(
            deliv,
            self.ctx,
        )
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

    def test_rc_with_final_mismatch(self):
        deliverable_data = yamlutils.loads(textwrap.dedent('''
        ---
        team: Release Management
        releases:
          - version: 1.5.1.0rc1
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
          - version: 1.5.1
            projects:
              - repo: openstack/automaton
                hash: ce2885f544637e6ee6139df7dc7bf937925804dd
        '''))
        deliv = deliverable.Deliverable(
            None,
            defaults.RELEASE,
            'test',
            deliverable_data,
        )
        validate.validate_series_final(
            deliv,
            self.ctx,
        )
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))

    def test_rc_with_final_mismatch_many_rcs(self):
        deliverable_data = yamlutils.loads(textwrap.dedent('''
        ---
        team: Release Management
        releases:
          - version: 1.5.1.0rc1
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
          - version: 1.5.1.0rc2
            projects:
              - repo: openstack/automaton
                hash: ce2885f544637e6ee6139df7dc7bf937925804dd
          - version: 1.5.1
            projects:
              - repo: openstack/automaton
                hash: de2885f544637e6ee6139df7dc7bf937925804dd
        '''))
        deliv = deliverable.Deliverable(
            None,
            defaults.RELEASE,
            'test',
            deliverable_data,
        )
        validate.validate_series_final(
            deliv,
            self.ctx,
        )
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))

    def test_match_wrong_rc(self):
        deliverable_data = yamlutils.loads(textwrap.dedent('''
        ---
        team: Release Management
        releases:
          - version: 1.5.1.0rc1
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
          - version: 1.5.1.0rc2
            projects:
              - repo: openstack/automaton
                hash: ce2885f544637e6ee6139df7dc7bf937925804dd
          - version: 1.5.1
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
        '''))
        deliv = deliverable.Deliverable(
            None,
            defaults.RELEASE,
            'test',
            deliverable_data,
        )
        validate.validate_series_final(
            deliv,
            self.ctx,
        )
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))


class TestValidateSeriesEOL(base.BaseTestCase):

    def setUp(self):
        super().setUp()
        self.tmpdir = self.useFixture(fixtures.TempDir()).path
        self.ctx = validate.ValidationContext()
        self.useFixture(fixtures.MonkeyPatch(
            'openstack_releases.cmds.validate.includes_new_tag',
            mock.Mock(return_value=True),
        ))

    def test_no_releases(self):
        deliverable_data = yamlutils.loads(textwrap.dedent('''
        ---
        team: Release Management
        '''))
        deliv = deliverable.Deliverable(
            None,
            defaults.RELEASE,
            'test',
            deliverable_data,
        )
        validate.validate_series_eol(
            deliv,
            self.ctx,
        )
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

    def test_only_normal(self):
        deliverable_data = yamlutils.loads(textwrap.dedent('''
        ---
        team: Release Management
        releases:
          - version: 1.5.1
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
        '''))
        deliv = deliverable.Deliverable(
            None,
            defaults.RELEASE,
            'test',
            deliverable_data,
        )
        validate.validate_series_eol(
            deliv,
            self.ctx,
        )
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

    def test_no_eol(self):
        deliverable_data = yamlutils.loads(textwrap.dedent('''
        ---
        team: Release Management
        releases:
          - version: 1.5.1
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
          - version: 1.5.2
            projects:
              - repo: openstack/automaton
                hash: ce2885f544637e6ee6139df7dc7bf937925804dd
        '''))
        deliv = deliverable.Deliverable(
            None,
            defaults.RELEASE,
            'test',
            deliverable_data,
        )
        validate.validate_series_eol(
            deliv,
            self.ctx,
        )
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

    def test_eol_ok(self):
        deliverable_data = yamlutils.loads(textwrap.dedent('''
        ---
        team: Release Management
        releases:
          - version: 1.5.2
            projects:
              - repo: openstack/automaton
                hash: ce2885f544637e6ee6139df7dc7bf937925804dd
          - version: newton-eol
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
        branches:
          - name: stable/newton
            location: 1.5.2
        '''))
        deliv = deliverable.Deliverable(
            None,
            'newton',
            'test',
            deliverable_data,
        )
        validate.validate_series_eol(
            deliv,
            self.ctx,
        )
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

    def test_eol_missing_repo(self):
        deliverable_data = yamlutils.loads(textwrap.dedent('''
        ---
        team: Release Management
        releases:
          - version: newton-eol
            projects:
              - repo: openstack/automaton
                hash: ce2885f544637e6ee6139df7dc7bf937925804dd
        branches:
          - name: stable/newton
            location: 1.2.3
        repository-settings:
          openstack/automaton: {}
          openstack/release-test: {}
        '''))
        deliv = deliverable.Deliverable(
            None,
            'newton',
            'test',
            deliverable_data,
        )
        validate.validate_series_eol(
            deliv,
            self.ctx,
        )
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))

    def test_eol_branchless(self):
        deliverable_data = yamlutils.loads(textwrap.dedent('''
        ---
        team: Release Management
        releases:
          - version: newton-eol
            projects:
              - repo: openstack/automaton
                hash: ce2885f544637e6ee6139df7dc7bf937925804dd
        repository-settings:
          openstack/automaton: {}
        '''))
        deliv = deliverable.Deliverable(
            None,
            'newton',
            'test',
            deliverable_data,
        )
        validate.validate_series_eol(
            deliv,
            self.ctx,
        )
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))


class TestValidateSeriesEM(base.BaseTestCase):

    def setUp(self):
        super().setUp()
        self.tmpdir = self.useFixture(fixtures.TempDir()).path
        self.ctx = validate.ValidationContext()
        self.useFixture(fixtures.MonkeyPatch(
            'openstack_releases.cmds.validate.includes_new_tag',
            mock.Mock(return_value=True),
        ))

    def test_no_releases(self):
        deliverable_data = yamlutils.loads(textwrap.dedent('''
        ---
        team: Release Management
        '''))
        deliv = deliverable.Deliverable(
            None,
            defaults.RELEASE,
            'test',
            deliverable_data,
        )
        validate.validate_series_em(
            deliv,
            self.ctx,
        )
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

    def test_only_normal(self):
        deliverable_data = yamlutils.loads(textwrap.dedent('''
        ---
        team: Release Management
        releases:
          - version: 1.5.1
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
        '''))
        deliv = deliverable.Deliverable(
            None,
            defaults.RELEASE,
            'test',
            deliverable_data,
        )
        validate.validate_series_em(
            deliv,
            self.ctx,
        )
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

    def test_no_em(self):
        deliverable_data = yamlutils.loads(textwrap.dedent('''
        ---
        team: Release Management
        releases:
          - version: 1.5.1
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
          - version: 1.5.2
            projects:
              - repo: openstack/automaton
                hash: ce2885f544637e6ee6139df7dc7bf937925804dd
        '''))
        deliv = deliverable.Deliverable(
            None,
            defaults.RELEASE,
            'test',
            deliverable_data,
        )
        validate.validate_series_em(
            deliv,
            self.ctx,
        )
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

    def test_em_ok(self):
        deliverable_data = yamlutils.loads(textwrap.dedent('''
        ---
        team: Release Management
        releases:
          - version: 1.2.3
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
          - version: newton-em
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
        branches:
          - name: stable/newton
            location: 1.2.3
        '''))
        deliv = deliverable.Deliverable(
            None,
            'newton',
            'test',
            deliverable_data,
        )
        validate.validate_series_em(
            deliv,
            self.ctx,
        )
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

    def test_em_no_releases(self):
        deliverable_data = yamlutils.loads(textwrap.dedent('''
        ---
        team: Release Management
        releases:
          - version: newton-em
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
        '''))
        deliv = deliverable.Deliverable(
            None,
            'newton',
            'test',
            deliverable_data,
        )
        validate.validate_series_em(
            deliv,
            self.ctx,
        )
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))

    def test_em_not_matching_last_release(self):
        deliverable_data = yamlutils.loads(textwrap.dedent('''
        ---
        team: Release Management
        releases:
          - version: 1.2.3
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
          - version: 1.2.4
            projects:
              - repo: openstack/automaton
                hash: beef85f544637e6ee6139df7dc7bf937925804dd
          - version: newton-em
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
        branches:
          - name: stable/newton
            location: 1.2.3
        repository-settings:
          openstack/automaton: {}
        '''))
        deliv = deliverable.Deliverable(
            None,
            'newton',
            'test',
            deliverable_data,
        )
        validate.validate_series_em(
            deliv,
            self.ctx,
        )
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))

    def test_em_matches_last_release(self):
        deliverable_data = yamlutils.loads(textwrap.dedent('''
        ---
        team: Release Management
        releases:
          - version: 1.2.3
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
          - version: 1.2.4
            projects:
              - repo: openstack/automaton
                hash: beef85f544637e6ee6139df7dc7bf937925804dd
          - version: newton-em
            projects:
              - repo: openstack/automaton
                hash: beef85f544637e6ee6139df7dc7bf937925804dd
        branches:
          - name: stable/newton
            location: 1.2.3
        repository-settings:
          openstack/automaton: {}
        '''))
        deliv = deliverable.Deliverable(
            None,
            'newton',
            'test',
            deliverable_data,
        )
        validate.validate_series_em(
            deliv,
            self.ctx,
        )
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

    def test_em_missing_repo(self):
        deliverable_data = yamlutils.loads(textwrap.dedent('''
        ---
        team: Release Management
        releases:
          - version: 1.2.3
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
          - version: newton-em
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
        branches:
          - name: stable/newton
            location: 1.2.3
        repository-settings:
          openstack/automaton: {}
          openstack/release-test: {}
        '''))
        deliv = deliverable.Deliverable(
            None,
            'newton',
            'test',
            deliverable_data,
        )
        validate.validate_series_em(
            deliv,
            self.ctx,
        )
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))

    def test_em_branchless(self):
        deliverable_data = yamlutils.loads(textwrap.dedent('''
        ---
        team: Release Management
        releases:
          - version: 1.2.3
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
          - version: newton-em
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
        '''))
        deliv = deliverable.Deliverable(
            None,
            'newton',
            'test',
            deliverable_data,
        )
        validate.validate_series_em(
            deliv,
            self.ctx,
        )
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))


class TestValidatePreReleaseProgression(base.BaseTestCase):

    def setUp(self):
        super().setUp()
        self.tmpdir = self.useFixture(fixtures.TempDir()).path
        self.ctx = validate.ValidationContext()
        self.useFixture(fixtures.MonkeyPatch(
            'openstack_releases.cmds.validate.includes_new_tag',
            mock.Mock(return_value=True),
        ))

    def test_no_releases(self):
        deliverable_data = yamlutils.loads(textwrap.dedent('''
        ---
        team: Release Management
        release-model: cycle-with-rc
        '''))
        deliv = deliverable.Deliverable(
            None,
            defaults.RELEASE,
            'test',
            deliverable_data,
        )
        validate.validate_pre_release_progression(
            deliv,
            self.ctx,
        )
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

    def test_only_rc(self):
        deliverable_data = yamlutils.loads(textwrap.dedent('''
        ---
        team: Release Management
        release-model: cycle-with-rc
        releases:
          - version: 1.5.1.0rc1
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
        '''))
        deliv = deliverable.Deliverable(
            None,
            defaults.RELEASE,
            'test',
            deliverable_data,
        )
        validate.validate_pre_release_progression(
            deliv,
            self.ctx,
        )
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

    def test_missing_rc(self):
        deliverable_data = yamlutils.loads(textwrap.dedent('''
        ---
        team: Release Management
        release-model: cycle-with-rc
        releases:
          - version: 1.5.2
            projects:
              - repo: openstack/automaton
                hash: ce2885f544637e6ee6139df7dc7bf937925804dd
        '''))
        deliv = deliverable.Deliverable(
            None,
            defaults.RELEASE,
            'test',
            deliverable_data,
        )
        validate.validate_pre_release_progression(
            deliv,
            self.ctx,
        )
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))

    def test_final_follows_rc(self):
        deliverable_data = yamlutils.loads(textwrap.dedent('''
        ---
        team: Release Management
        release-model: cycle-with-rc
        releases:
          - version: 1.5.0.0rc1
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
          - version: 1.5.0
            projects:
              - repo: openstack/automaton
                hash: ce2885f544637e6ee6139df7dc7bf937925804dd
        '''))
        deliv = deliverable.Deliverable(
            None,
            defaults.RELEASE,
            'test',
            deliverable_data,
        )
        validate.validate_pre_release_progression(
            deliv,
            self.ctx,
        )
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

    def test_final_follows_multiple_rc(self):
        deliverable_data = yamlutils.loads(textwrap.dedent('''
        ---
        team: Release Management
        release-model: cycle-with-rc
        releases:
          - version: 1.5.0.0rc1
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
          - version: 1.5.0.0rc2
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
          - version: 1.5.0
            projects:
              - repo: openstack/automaton
                hash: ce2885f544637e6ee6139df7dc7bf937925804dd
        '''))
        deliv = deliverable.Deliverable(
            None,
            defaults.RELEASE,
            'test',
            deliverable_data,
        )
        validate.validate_pre_release_progression(
            deliv,
            self.ctx,
        )
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

    def test_rc_follows_final(self):
        deliverable_data = yamlutils.loads(textwrap.dedent('''
        ---
        team: Release Management
        release-model: cycle-with-rc
        releases:
          - version: 1.5.0
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
          - version: 1.5.0.0rc1
            projects:
              - repo: openstack/automaton
                hash: ce2885f544637e6ee6139df7dc7bf937925804dd
        '''))
        deliv = deliverable.Deliverable(
            None,
            defaults.RELEASE,
            'test',
            deliverable_data,
        )
        validate.validate_pre_release_progression(
            deliv,
            self.ctx,
        )
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))

    def test_rc_follows_beta(self):
        deliverable_data = yamlutils.loads(textwrap.dedent('''
        ---
        team: Release Management
        release-model: cycle-with-rc
        releases:
          - version: 1.5.0.0b1
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
          - version: 1.5.0.0rc1
            projects:
              - repo: openstack/automaton
                hash: ce2885f544637e6ee6139df7dc7bf937925804dd
        '''))
        deliv = deliverable.Deliverable(
            None,
            defaults.RELEASE,
            'test',
            deliverable_data,
        )
        validate.validate_pre_release_progression(
            deliv,
            self.ctx,
        )
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

    def test_final_follows_beta(self):
        deliverable_data = yamlutils.loads(textwrap.dedent('''
        ---
        team: Release Management
        release-model: cycle-with-rc
        releases:
          - version: 1.5.0.0b1
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
          - version: 1.5.0
            projects:
              - repo: openstack/automaton
                hash: ce2885f544637e6ee6139df7dc7bf937925804dd
        '''))
        deliv = deliverable.Deliverable(
            None,
            defaults.RELEASE,
            'test',
            deliverable_data,
        )
        validate.validate_pre_release_progression(
            deliv,
            self.ctx,
        )
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))


class TestValidateBranchPoints(base.BaseTestCase):

    def setUp(self):
        super().setUp()
        self.ctx = validate.ValidationContext()
        gitutils.clone_repo(self.ctx.workdir, 'openstack/release-test')

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
        deliv = deliverable.Deliverable(
            team='team',
            series='ocata',
            name='name',
            data=yamlutils.loads(deliverable_data),
        )
        validate.validate_branch_points(
            deliv,
            self.ctx,
        )
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

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
        deliv = deliverable.Deliverable(
            team='team',
            series='newton',
            name='name',
            data=yamlutils.loads(deliverable_data),
        )
        validate.validate_branch_points(
            deliv,
            self.ctx,
        )
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

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
        deliv = deliverable.Deliverable(
            team='team',
            series='meiji',
            name='name',
            data=yamlutils.loads(deliverable_data),
        )
        validate.validate_branch_points(
            deliv,
            self.ctx,
        )
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))
