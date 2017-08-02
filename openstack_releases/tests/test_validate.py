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

from openstack_releases import defaults
from openstack_releases.cmds import validate
from openstack_releases import yamlutils


class TestValidateBugTracker(base.BaseTestCase):

    def test_no_tracker(self):
        warnings = []
        errors = []
        validate.validate_bugtracker(
            {},
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))

    @mock.patch('requests.get')
    def test_launchpad_invalid_name(self, get):
        get.return_value = mock.Mock(status_code=404)
        warnings = []
        errors = []
        validate.validate_bugtracker(
            {'launchpad': 'nonsense-name'},
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))

    @mock.patch('requests.get')
    def test_launchpad_valid_name(self, get):
        get.return_value = mock.Mock(status_code=200)
        warnings = []
        errors = []
        validate.validate_bugtracker(
            {'launchpad': 'oslo.config'},
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(0, len(errors))

    @mock.patch('requests.get')
    def test_launchpad_timeout(self, get):
        import requests
        get.side_effect = requests.exceptions.ConnectionError('testing')
        warnings = []
        errors = []
        validate.validate_bugtracker(
            {'launchpad': 'oslo.config'},
            warnings.append,
            errors.append,
        )
        self.assertEqual(1, len(warnings))
        self.assertEqual(0, len(errors))

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
        warnings = []
        errors = []
        validate.validate_bugtracker(
            {'storyboard': '760'},
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(0, len(errors))

    @mock.patch('requests.get')
    def test_storyboard_invalid_id(self, get):
        get.return_value = mock.Mock(status_code=200)
        warnings = []
        errors = []
        validate.validate_bugtracker(
            {'storyboard': 'name-not-id'},
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))

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
        warnings = []
        errors = []
        validate.validate_bugtracker(
            {'storyboard': '-760'},
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))


class TestValidateTeam(base.BaseTestCase):

    def test_no_name(self):
        warnings = []
        errors = []
        validate.validate_team(
            {},
            {},
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))

    def test_invalid_name(self):
        warnings = []
        errors = []
        validate.validate_team(
            {'team': 'nonsense-name'},
            {},
            warnings.append,
            errors.append,
        )
        self.assertEqual(1, len(warnings))
        self.assertEqual(0, len(errors))

    def test_valid_name(self):
        warnings = []
        errors = []
        validate.validate_team(
            {'team': 'oslo'},
            {'oslo': None},
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(0, len(errors))


class TestValidateReleaseNotes(base.BaseTestCase):

    def test_no_link(self):
        warnings = []
        errors = []
        validate.validate_release_notes(
            {},
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(0, len(errors))

    def test_invalid_link(self):
        warnings = []
        errors = []
        validate.validate_release_notes(
            {'release-notes': 'https://docs.openstack.org/no-such-page'},
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))

    def test_valid_link(self):
        warnings = []
        errors = []
        validate.validate_release_notes(
            {'release-notes':
             'https://docs.openstack.org/releasenotes/oslo.config'},
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(0, len(errors))

    def test_invalid_link_multi(self):
        warnings = []
        errors = []
        validate.validate_release_notes(
            {
                'release-notes': {
                    'openstack/releases': 'https://docs.openstack.org/no-such-page',
                }
            },
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))

    def test_valid_link_multi(self):
        warnings = []
        errors = []
        validate.validate_release_notes(
            {
                'release-notes': {
                    'openstack/releases': 'https://docs.openstack.org/releasenotes/oslo.config',
                }
            },
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(0, len(errors))


class TestValidateDeliverableType(base.BaseTestCase):

    def test_no_type(self):
        warnings = []
        errors = []
        validate.validate_type(
            {},
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))

    def test_invalid_type(self):
        warnings = []
        errors = []
        validate.validate_type(
            {'type': 'not-valid'},
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))

    def test_valid_type(self):
        warnings = []
        errors = []
        validate.validate_type(
            {'type': 'library'},
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(0, len(errors))


class TestGetModel(base.BaseTestCase):

    def test_no_model_series(self):
        self.assertEqual(
            'UNSPECIFIED',
            validate.get_model({}, 'ocata'),
        )

    def test_no_model_independent(self):
        self.assertEqual(
            'independent',
            validate.get_model({}, '_independent'),
        )

    def test_with_model_independent(self):
        self.assertEqual(
            'independent',
            validate.get_model({'release-model': 'set'}, '_independent'),
        )

    def test_with_model_series(self):
        self.assertEqual(
            'set',
            validate.get_model({'release-model': 'set'}, 'ocata'),
        )


class TestValidateModel(base.BaseTestCase):

    def test_no_model_series(self):
        warnings = []
        errors = []
        validate.validate_model(
            {},
            'ocata',
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))

    def test_no_model_independent(self):
        warnings = []
        errors = []
        validate.validate_model(
            {},
            '_independent',
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(0, len(errors))

    def test_with_model_independent_match(self):
        warnings = []
        errors = []
        validate.validate_model(
            {'release-model': 'independent'},
            '_independent',
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(0, len(errors))

    def test_with_model_independent_nomatch(self):
        warnings = []
        errors = []
        validate.validate_model(
            {'release-model': 'cycle-with-intermediary'},
            '_independent',
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))

    def test_with_independent_and_model(self):
        warnings = []
        errors = []
        validate.validate_model(
            {'release-model': 'independent'},
            'ocata',
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))

    def test_with_model_series(self):
        warnings = []
        errors = []
        validate.validate_model(
            {'release-model': 'cycle-with-intermediary'},
            'ocata',
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(0, len(errors))

    def test_with_unknown_model_series(self):
        warnings = []
        errors = []
        validate.validate_model(
            {'release-model': 'not-a-model'},
            'ocata',
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))


class TestValidateReleases(base.BaseTestCase):

    def setUp(self):
        super(TestValidateReleases, self).setUp()
        self.tmpdir = self.useFixture(fixtures.TempDir()).path

    @mock.patch('openstack_releases.project_config.require_release_jobs_for_repo')
    def test_check_release_jobs(self, check_jobs):
        deliverable_info = {
            'releases': [
                {'version': '1.5.0',
                 'projects': [
                     {'repo': 'openstack/automaton',
                      'hash': 'be2885f544637e6ee6139df7dc7bf937925804dd'},
                 ]}
            ],
        }
        warnings = []
        errors = []
        validate.validate_releases(
            deliverable_info,
            {'validate-projects-by-name': {}},
            'ocata',
            self.tmpdir,
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(0, len(errors))
        check_jobs.assert_called_once()

    def test_invalid_hash(self):
        deliverable_info = {
            'artifact-link-mode': 'none',
            'releases': [
                {'version': '0.1',
                 'projects': [
                     {'repo': 'openstack/automaton',
                      'hash': 'this-is-not-a-hash'},
                 ]}
            ],
        }
        warnings = []
        errors = []
        validate.validate_releases(
            deliverable_info,
            {'validate-projects-by-name': {}},
            'ocata',
            self.tmpdir,
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))

    def test_valid_existing(self):
        deliverable_info = {
            'artifact-link-mode': 'none',
            'releases': [
                {'version': '1.5.0',
                 'projects': [
                     {'repo': 'openstack/automaton',
                      'hash': 'be2885f544637e6ee6139df7dc7bf937925804dd'},
                 ]}
            ],
        }
        warnings = []
        errors = []
        validate.validate_releases(
            deliverable_info,
            {'validate-projects-by-name': {}},
            'ocata',
            self.tmpdir,
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(0, len(errors))

    def test_no_such_hash(self):
        deliverable_info = {
            'artifact-link-mode': 'none',
            'releases': [
                {'version': '99.0.0',
                 'projects': [
                     {'repo': 'openstack/automaton',
                      'hash': 'de2885f544637e6ee6139df7dc7bf937925804dd'},
                 ]}
            ],
        }
        warnings = []
        errors = []
        validate.validate_releases(
            deliverable_info,
            {'validate-projects-by-name': {}},
            'ocata',
            self.tmpdir,
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))

    def test_mismatch_existing(self):
        deliverable_info = {
            'artifact-link-mode': 'none',
            'releases': [
                {'version': '1.5.0',
                 'projects': [
                     {'repo': 'openstack/automaton',
                      # hash from the previous release
                      'hash': 'c6278ba1a8167447a5f52bdb92c2790abc5d0f87'},
                 ]}
            ],
        }
        warnings = []
        errors = []
        validate.validate_releases(
            deliverable_info,
            {'validate-projects-by-name': {}},
            'ocata',
            self.tmpdir,
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))

    def test_hash_from_master_used_in_stable_release(self):
        deliverable_info = {
            'artifact-link-mode': 'none',
            'releases': [
                {'version': '1.4.1',
                 'projects': [
                     {'repo': 'openstack/automaton',
                      # hash from master
                      'hash': 'ec62e6270dba8f3d6a60600876be8fd99f7c5b08'},
                 ]}
            ],
        }
        warnings = []
        errors = []
        validate.validate_releases(
            deliverable_info,
            {'validate-projects-by-name': {}},
            'newton',
            self.tmpdir,
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))

    def test_hash_from_master_used_in_stable_release2(self):
        deliverable_info = {
            'artifact-link-mode': 'none',
            'releases': [
                {'version': '1.4.0',
                 'projects': [
                     {'repo': 'openstack/automaton',
                      'hash': 'c6278ba1a8167447a5f52bdb92c2790abc5d0f87'},
                 ]},
                {'version': '1.4.1',
                 'projects': [
                     {'repo': 'openstack/automaton',
                      # hash from master
                      'hash': 'ec62e6270dba8f3d6a60600876be8fd99f7c5b08'},
                 ]}
            ],
        }
        warnings = []
        errors = []
        validate.validate_releases(
            deliverable_info,
            {'validate-projects-by-name': {}},
            'newton',
            self.tmpdir,
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))

    def test_hash_from_stable_used_in_master_release(self):
        deliverable_info = {
            'artifact-link-mode': 'none',
            'releases': [
                {'version': '99.5.0',
                 'projects': [
                     {'repo': 'openstack/automaton',
                      # hash from stable/newton
                      'hash': '95db03ed96dcd1a582936b4660b4db55ce606e49'},
                 ]}
            ],
        }
        warnings = []
        errors = []
        validate.validate_releases(
            deliverable_info,
            {'validate-projects-by-name': {}},
            defaults.RELEASE,
            self.tmpdir,
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))

    def test_hash_from_master_used_after_default_branch_should_exist_but_does_not(self):
        deliverable_info = {
            'artifact-link-mode': 'none',
            'releases': [
                {'version': '1.0.0',
                 'projects': [
                     {'repo': 'openstack/releases',
                      'hash': '8eea82428995b8f3354c0a75351fe95bbbb1135a'},
                 ]}
            ],
        }
        warnings = []
        errors = []
        validate.validate_releases(
            deliverable_info,
            {'validate-projects-by-name': {}},
            'austin',
            self.tmpdir,
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(0, len(errors))

    def test_not_descendent(self):
        deliverable_info = {
            'artifact-link-mode': 'none',
            'releases': [
                {'version': '1.4.0',
                 'projects': [
                     {'repo': 'openstack/automaton',
                      'hash': 'c6278ba1a8167447a5f52bdb92c2790abc5d0f87'},
                 ]},
                {'version': '1.4.999',
                 'projects': [
                     {'repo': 'openstack/automaton',
                      # a commit on stable/mitaka instead of stable/newton
                      'hash': 'e92b85ec64ac74598983a90bd2f3e1cf232ba9d5'},
                 ]},
            ],
        }
        warnings = []
        errors = []
        validate.validate_releases(
            deliverable_info,
            {'validate-projects-by-name': {}},
            'ocata',
            self.tmpdir,
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(2, len(errors))

    def test_new_not_at_end(self):
        deliverable_info = {
            'artifact-link-mode': 'none',
            'releases': [
                {'version': '1.3.999',
                 'projects': [
                     {'repo': 'openstack/automaton',
                      'hash': 'e87dc55a48387d2b8b8c46e02a342c27995dacb1'},
                 ]},
                {'version': '1.4.0',
                 'projects': [
                     {'repo': 'openstack/automaton',
                      'hash': 'c6278ba1a8167447a5f52bdb92c2790abc5d0f87'},
                 ]},
            ],
        }
        warnings = []
        errors = []
        validate.validate_releases(
            deliverable_info,
            {'validate-projects-by-name': {}},
            'ocata',
            self.tmpdir,
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))

    @mock.patch('openstack_releases.versionutils.validate_version')
    def test_invalid_version(self, validate_version):
        # Set up the nested validation function to produce an error,
        # even though there is nothing else wrong with the
        # inputs. That ensures we only get the 1 error back.
        validate_version.configure_mock(
            return_value=['an error goes here'],
        )
        deliverable_info = {
            'artifact-link-mode': 'none',
            'releases': [
                {'version': '99.5.0',
                 'projects': [
                     {'repo': 'openstack/automaton',
                      'hash': 'be2885f544637e6ee6139df7dc7bf937925804dd'},
                 ]}
            ],
        }
        warnings = []
        errors = []
        validate.validate_releases(
            deliverable_info,
            {'validate-projects-by-name': {}},
            'ocata',
            self.tmpdir,
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))

    def test_no_releases(self):
        # When we initialize a new series, we won't have any release
        # data. That's OK.
        deliverable_info = {
            'artifact-link-mode': 'none',
            'releases': []
        }
        warnings = []
        errors = []
        validate.validate_releases(
            deliverable_info,
            {'validate-projects-by-name': {}},
            'ocata',
            self.tmpdir,
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(0, len(errors))

    def test_untagged_with_releases(self):
        deliverable_info = {
            'release-model': 'untagged',
            'artifact-link-mode': 'none',
            'releases': [
                {'version': '99.5.0',
                 'projects': [
                     {'repo': 'openstack/automaton',
                      'hash': 'be2885f544637e6ee6139df7dc7bf937925804dd'},
                 ]},
            ]
        }
        warnings = []
        errors = []
        validate.validate_releases(
            deliverable_info,
            {'validate-projects-by-name': {}},
            'ocata',
            self.tmpdir,
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))


class TestPuppetUtils(base.BaseTestCase):

    def setUp(self):
        super(TestPuppetUtils, self).setUp()
        self.tmpdir = self.useFixture(fixtures.TempDir()).path

    @mock.patch('openstack_releases.gitutils.check_branch_sha')
    @mock.patch('openstack_releases.puppetutils.get_version')
    @mock.patch('openstack_releases.puppetutils.looks_like_a_module')
    def test_valid_version(self, llam, get_version, cbs):
        llam.return_value = True
        get_version.return_value = '99.1.0'
        cbs.return_value = True
        deliverable_info = {
            'artifact-link-mode': 'none',
            'releases': [
                {'version': '99.1.0',
                 'projects': [
                     {'repo': 'openstack/puppet-watcher',
                      'hash': '1e7baef27139f69a83e1fe28686bb72ee7e1d6fa'},
                 ]}
            ],
        }
        warnings = []
        errors = []
        validate.validate_releases(
            deliverable_info,
            {'validate-projects-by-name': {}},
            'ocata',
            self.tmpdir,
            warnings.append,
            errors.append,
        )
        print(warnings, errors)
        self.assertEqual(0, len(warnings))
        self.assertEqual(0, len(errors))

    @mock.patch('openstack_releases.gitutils.check_branch_sha')
    @mock.patch('openstack_releases.puppetutils.get_version')
    @mock.patch('openstack_releases.puppetutils.looks_like_a_module')
    def test_mismatched_version(self, llam, get_version, cbs):
        llam.return_value = True
        get_version.return_value = '99.1.0'
        cbs.return_value = True
        deliverable_info = {
            'artifact-link-mode': 'none',
            'releases': [
                {'version': '99.2.0',
                 'projects': [
                     {'repo': 'openstack/puppet-watcher',
                      'hash': '1e7baef27139f69a83e1fe28686bb72ee7e1d6fa'},
                 ]}
            ],
        }
        warnings = []
        errors = []
        validate.validate_releases(
            deliverable_info,
            {'validate-projects-by-name': {}},
            'ocata',
            self.tmpdir,
            warnings.append,
            errors.append,
        )
        print(warnings, errors)
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))


class TestValidateTarballBase(base.BaseTestCase):

    def setUp(self):
        super(TestValidateTarballBase, self).setUp()
        self.tmpdir = self.useFixture(fixtures.TempDir()).path

    @mock.patch('openstack_releases.project_config.require_release_jobs_for_repo')
    @mock.patch('openstack_releases.pythonutils.get_sdist_name')
    def test_default_ok(self, gsn, jobs):
        deliverable_info = {
            'releases': [
                {'version': '1.5.0',
                 'projects': [
                     {'repo': 'openstack/automaton',
                      'hash': 'be2885f544637e6ee6139df7dc7bf937925804dd'},
                 ]}
            ],
        }
        warnings = []
        errors = []
        gsn.return_value = 'automaton'
        validate.validate_releases(
            deliverable_info,
            {'validate-projects-by-name': {}},
            'ocata',
            self.tmpdir,
            warnings.append,
            errors.append,
        )
        print(warnings, errors)
        self.assertEqual(0, len(warnings))
        self.assertEqual(0, len(errors))

    @mock.patch('openstack_releases.project_config.require_release_jobs_for_repo')
    @mock.patch('openstack_releases.pythonutils.get_sdist_name')
    def test_ignored_link_mode_none(self, gsn, jobs):
        deliverable_info = {
            'artifact-link-mode': 'none',
            'releases': [
                {'version': '1.5.0',
                 'projects': [
                     {'repo': 'openstack/automaton',
                      'hash': 'be2885f544637e6ee6139df7dc7bf937925804dd'},
                 ]}
            ],
        }
        warnings = []
        errors = []
        gsn.return_value = 'this-is-wrong'
        validate.validate_releases(
            deliverable_info,
            {'validate-projects-by-name': {}},
            'ocata',
            self.tmpdir,
            warnings.append,
            errors.append,
        )
        print(warnings, errors)
        self.assertEqual(0, len(warnings))
        self.assertEqual(0, len(errors))

    @mock.patch('openstack_releases.project_config.require_release_jobs_for_repo')
    @mock.patch('openstack_releases.pythonutils.get_sdist_name')
    def test_default_invalid(self, gsn, jobs):
        deliverable_info = {
            'releases': [
                {'version': '1.5.0',
                 'projects': [
                     {'repo': 'openstack/automaton',
                      'hash': 'be2885f544637e6ee6139df7dc7bf937925804dd'},
                 ]}
            ],
        }
        warnings = []
        errors = []
        gsn.return_value = 'automaton1'
        validate.validate_releases(
            deliverable_info,
            {'validate-projects-by-name': {}},
            'ocata',
            self.tmpdir,
            warnings.append,
            errors.append,
        )
        print(warnings, errors)
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))

    @mock.patch('openstack_releases.project_config.require_release_jobs_for_repo')
    @mock.patch('openstack_releases.pythonutils.get_sdist_name')
    def test_explicit_ok(self, gsn, jobs):
        deliverable_info = {
            'releases': [
                {'version': '1.5.0',
                 'projects': [
                     {'repo': 'openstack/automaton',
                      'hash': 'be2885f544637e6ee6139df7dc7bf937925804dd',
                      'tarball-base': 'automaton1'},
                 ]}
            ],
        }
        warnings = []
        errors = []
        gsn.return_value = 'automaton1'
        validate.validate_releases(
            deliverable_info,
            {'validate-projects-by-name': {}},
            'ocata',
            self.tmpdir,
            warnings.append,
            errors.append,
        )
        print(warnings, errors)
        self.assertEqual(0, len(warnings))
        self.assertEqual(0, len(errors))

    @mock.patch('openstack_releases.project_config.require_release_jobs_for_repo')
    @mock.patch('openstack_releases.pythonutils.get_sdist_name')
    def test_explicit_invalid(self, gsn, jobs):
        deliverable_info = {
            'releases': [
                {'version': '1.5.0',
                 'projects': [
                     {'repo': 'openstack/automaton',
                      'hash': 'be2885f544637e6ee6139df7dc7bf937925804dd',
                      'tarball-base': 'does-not-match-sdist'},
                 ]}
            ],
        }
        warnings = []
        errors = []
        gsn.return_value = 'automaton'
        validate.validate_releases(
            deliverable_info,
            {'validate-projects-by-name': {}},
            'ocata',
            self.tmpdir,
            warnings.append,
            errors.append,
        )
        print(warnings, errors)
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))


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

    def test_all_repos(self):
        deliverable_info = {
            'artifact-link-mode': 'none',
            'releases': [
                {'version': '1000.0.0',
                 'projects': [
                     {'repo': 'openstack/release-test',
                      'hash': '685da43147c3bedc24906d5a26839550f2e962b1'},
                 ]}
            ],
        }
        warnings = []
        errors = []
        validate.validate_new_releases(
            deliverable_info,
            'release-test.yaml',
            self.team_data,
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(0, len(errors))

    def test_extra_repo(self):
        deliverable_info = {
            'artifact-link-mode': 'none',
            'releases': [
                {'version': '1000.0.0',
                 'projects': [
                     {'repo': 'openstack/release-test',
                      'hash': '685da43147c3bedc24906d5a26839550f2e962b1'},
                     {'repo': 'openstack-infra/release-tools',
                      'hash': '685da43147c3bedc24906d5a26839550f2e962b1'},
                 ]}
            ],
        }
        warnings = []
        errors = []
        validate.validate_new_releases(
            deliverable_info,
            'release-test.yaml',
            self.team_data,
            warnings.append,
            errors.append,
        )
        self.assertEqual(1, len(warnings))
        self.assertEqual(0, len(errors))

    def test_missing_repo(self):
        deliverable_info = {
            'artifact-link-mode': 'none',
            'releases': [
                {'version': '1000.0.0',
                 'projects': [
                 ]}
            ],
        }
        warnings = []
        errors = []
        validate.validate_new_releases(
            deliverable_info,
            'release-test.yaml',
            self.team_data,
            warnings.append,
            errors.append,
        )
        self.assertEqual(1, len(warnings))
        self.assertEqual(0, len(errors))


class TestValidateBranchPrefixes(base.BaseTestCase):

    def test_invalid_prefix(self):
        deliverable_info = {
            'branches': [
                {'name': 'invalid/branch'},
            ],
        }
        warnings = []
        errors = []
        validate.validate_branch_prefixes(
            deliverable_info,
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))

    def test_valid_prefix(self):
        warnings = []
        errors = []
        for prefix in validate._VALID_BRANCH_PREFIXES:
            deliverable_info = {
                'branches': [
                    {'name': '%s/branch' % prefix},
                ],
            }
            validate.validate_branch_prefixes(
                deliverable_info,
                warnings.append,
                errors.append,
            )
        self.assertEqual(0, len(warnings))
        self.assertEqual(0, len(errors))


class TestValidateStableBranches(base.BaseTestCase):

    def test_version_in_deliverable(self):
        deliverable_data = textwrap.dedent('''
        releases:
          - version: 1.5.0
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
        branches:
          - name: stable/ocata
            location: 1.5.0
        ''')
        warnings = []
        errors = []
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_stable_branches(
            deliverable_info,
            'ocata',
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(0, len(errors))

    def test_badly_formatted_name(self):
        deliverable_data = textwrap.dedent('''
        releases:
          - version: 1.5.0
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
        branches:
          - name: ocata
            location: 1.5.0
        ''')
        warnings = []
        errors = []
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_stable_branches(
            deliverable_info,
            'ocata',
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))

    def test_version_not_in_deliverable(self):
        deliverable_data = textwrap.dedent('''
        releases:
          - version: 1.5.0
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
        branches:
          - name: stable/ocata
            location: 1.5.1
        ''')
        warnings = []
        errors = []
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_stable_branches(
            deliverable_info,
            'ocata',
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))

    def test_unknown_series_cycle(self):
        deliverable_data = textwrap.dedent('''
        releases:
          - version: 1.5.0
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
        branches:
          - name: stable/abc
            location: 1.5.0
        ''')
        warnings = []
        errors = []
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_stable_branches(
            deliverable_info,
            'ocata',
            warnings.append,
            errors.append,
        )
        print(warnings, errors)
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))

    def test_unknown_series_independent(self):
        deliverable_data = textwrap.dedent('''
        releases:
          - version: 1.5.0
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
        branches:
          - name: stable/abc
            location: 1.5.0
        ''')
        warnings = []
        errors = []
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_stable_branches(
            deliverable_info,
            '_independent',
            warnings.append,
            errors.append,
        )
        print(warnings, errors)
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))

    def test_can_have_independent_branches(self):
        deliverable_data = textwrap.dedent('''
        launchpad: gnocchi
        releases:
          - version: 1.5.0
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
        branches:
          - name: stable/abc
            location: 1.5.0
        ''')
        warnings = []
        errors = []
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_stable_branches(
            deliverable_info,
            '_independent',
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(0, len(errors))

    def test_explicit_stable_branch_type(self):
        deliverable_data = textwrap.dedent('''
        stable-branch-type: std
        releases:
          - version: 1.5.0
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
        branches:
          - name: stable/ocata
            location: 1.5.0
        ''')
        warnings = []
        errors = []
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_stable_branches(
            deliverable_info,
            'ocata',
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(0, len(errors))

    def test_explicit_stable_branch_type_invalid(self):
        deliverable_data = textwrap.dedent('''
        stable-branch-type: unknown
        releases:
          - version: 1.5.0
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
        branches:
          - name: stable/ocata
            location: 1.5.0
        ''')
        warnings = []
        errors = []
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_stable_branches(
            deliverable_info,
            'ocata',
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))

    def test_tagless_stable_branch_type_bad_location_type(self):
        deliverable_data = textwrap.dedent('''
        stable-branch-type: tagless
        releases:
          - version: 1.5.0
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
        branches:
          - name: stable/ocata
            location: 1.5.0
        ''')
        warnings = []
        errors = []
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_stable_branches(
            deliverable_info,
            'ocata',
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))

    def test_tagless_stable_branch_type_bad_location_value(self):
        deliverable_data = textwrap.dedent('''
        stable-branch-type: tagless
        releases:
          - version: 1.5.0
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
        branches:
          - name: stable/ocata
            location:
              openstack/automaton: 1.5.0
        ''')
        warnings = []
        errors = []
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_stable_branches(
            deliverable_info,
            'ocata',
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))

    def test_tagless_stable_branch_type(self):
        deliverable_data = textwrap.dedent('''
        stable-branch-type: tagless
        releases:
          - version: 1.5.0
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
        branches:
          - name: stable/ocata
            location:
              openstack/automaton: be2885f544637e6ee6139df7dc7bf937925804dd
        ''')
        warnings = []
        errors = []
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_stable_branches(
            deliverable_info,
            'ocata',
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(0, len(errors))


class TestValidateFeatureBranches(base.BaseTestCase):

    def setUp(self):
        super(TestValidateFeatureBranches, self).setUp()
        self.tmpdir = self.useFixture(fixtures.TempDir()).path

    def test_location_not_a_dict(self):
        deliverable_data = textwrap.dedent('''
        releases:
          - version: 1.5.0
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
        branches:
          - name: feature/abc
            location: 1.5.0
        ''')
        warnings = []
        errors = []
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_feature_branches(
            deliverable_info,
            self.tmpdir,
            warnings.append,
            errors.append,
        )
        print(warnings, errors)
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))

    def test_location_not_a_sha(self):
        deliverable_data = textwrap.dedent('''
        releases:
          - version: 1.5.0
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
        branches:
          - name: feature/abc
            location:
               openstack/automaton: 1.5.0
        ''')
        warnings = []
        errors = []
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_feature_branches(
            deliverable_info,
            self.tmpdir,
            warnings.append,
            errors.append,
        )
        print(warnings, errors)
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))

    def test_location_a_sha(self):
        deliverable_data = textwrap.dedent('''
        releases:
          - version: 1.5.0
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
        branches:
          - name: feature/abc
            location:
               openstack/automaton: be2885f544637e6ee6139df7dc7bf937925804dd
        ''')
        warnings = []
        errors = []
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_feature_branches(
            deliverable_info,
            self.tmpdir,
            warnings.append,
            errors.append,
        )
        print(warnings, errors)
        self.assertEqual(0, len(warnings))
        self.assertEqual(0, len(errors))

    def test_badly_formatted_name(self):
        deliverable_data = textwrap.dedent('''
        releases:
          - version: 1.5.0
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
        branches:
          - name: abc
            location:
               openstack/automaton: be2885f544637e6ee6139df7dc7bf937925804dd
        ''')
        warnings = []
        errors = []
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_feature_branches(
            deliverable_info,
            self.tmpdir,
            warnings.append,
            errors.append,
        )
        print(warnings, errors)
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))

    def test_location_no_such_sha(self):
        deliverable_data = textwrap.dedent('''
        releases:
          - version: 1.5.0
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
        branches:
          - name: feature/abc
            location:
               openstack/automaton: de2885f544637e6ee6139df7dc7bf937925804dd
        ''')
        warnings = []
        errors = []
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_feature_branches(
            deliverable_info,
            self.tmpdir,
            warnings.append,
            errors.append,
        )
        print(warnings, errors)
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))


class TestValidateDriverfixesBranches(base.BaseTestCase):

    def setUp(self):
        super(TestValidateDriverfixesBranches, self).setUp()
        self.tmpdir = self.useFixture(fixtures.TempDir()).path

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
        warnings = []
        errors = []
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_driverfixes_branches(
            deliverable_info,
            self.tmpdir,
            warnings.append,
            errors.append,
        )
        print(warnings, errors)
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))

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
        warnings = []
        errors = []
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_driverfixes_branches(
            deliverable_info,
            self.tmpdir,
            warnings.append,
            errors.append,
        )
        print(warnings, errors)
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))

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
        warnings = []
        errors = []
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_driverfixes_branches(
            deliverable_info,
            self.tmpdir,
            warnings.append,
            errors.append,
        )
        print(warnings, errors)
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))

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
        warnings = []
        errors = []
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_driverfixes_branches(
            deliverable_info,
            self.tmpdir,
            warnings.append,
            errors.append,
        )
        print(warnings, errors)
        self.assertEqual(0, len(warnings))
        self.assertEqual(0, len(errors))

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
        warnings = []
        errors = []
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_driverfixes_branches(
            deliverable_info,
            self.tmpdir,
            warnings.append,
            errors.append,
        )
        print(warnings, errors)
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))

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
        warnings = []
        errors = []
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_driverfixes_branches(
            deliverable_info,
            self.tmpdir,
            warnings.append,
            errors.append,
        )
        print(warnings, errors)
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))


class TestValidateSeriesOpen(base.BaseTestCase):

    def setUp(self):
        super(TestValidateSeriesOpen, self).setUp()
        self.tmpdir = self.useFixture(fixtures.TempDir()).path

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
        warnings = []
        errors = []
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_series_open(
            deliverable_info,
            'a',
            series_b_filename,
            warnings.append,
            errors.append,
        )
        print(warnings, errors)
        self.assertEqual(0, len(warnings))
        self.assertEqual(0, len(errors))

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
        warnings = []
        errors = []
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_series_open(
            deliverable_info,
            'a',
            series_b_filename,
            warnings.append,
            errors.append,
        )
        print(warnings, errors)
        self.assertEqual(0, len(warnings))
        self.assertEqual(0, len(errors))

    def test_independent(self):
        deliverable_data = textwrap.dedent('''
        ---
        releases:
          - version: 1.5.0
            projects:
              - repo: openstack/automaton
                hash: be2885f544637e6ee6139df7dc7bf937925804dd
        ''')
        warnings = []
        errors = []
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_series_open(
            deliverable_info,
            '_independent',
            'filename',  # not used
            warnings.append,
            errors.append,
        )
        print(warnings, errors)
        self.assertEqual(0, len(warnings))
        self.assertEqual(0, len(errors))

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
        warnings = []
        errors = []
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_series_open(
            deliverable_info,
            'a',
            series_b_filename,
            warnings.append,
            errors.append,
        )
        print(warnings, errors)
        self.assertEqual(1, len(warnings))
        self.assertEqual(0, len(errors))


class TestValidateSeriesFirst(base.BaseTestCase):

    def setUp(self):
        super(TestValidateSeriesFirst, self).setUp()
        self.tmpdir = self.useFixture(fixtures.TempDir()).path

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
        warnings = []
        errors = []
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_series_first(
            deliverable_info,
            'a',
            warnings.append,
            errors.append,
        )
        print(warnings, errors)
        self.assertEqual(0, len(warnings))
        self.assertEqual(0, len(errors))

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
        warnings = []
        errors = []
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_series_first(
            deliverable_info,
            'a',
            warnings.append,
            errors.append,
        )
        print(warnings, errors)
        self.assertEqual(0, len(warnings))
        self.assertEqual(0, len(errors))

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
        warnings = []
        errors = []
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_series_first(
            deliverable_info,
            'a',
            warnings.append,
            errors.append,
        )
        print(warnings, errors)
        self.assertEqual(0, len(warnings))
        self.assertEqual(0, len(errors))

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
        warnings = []
        errors = []
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_series_first(
            deliverable_info,
            'a',
            warnings.append,
            errors.append,
        )
        print(warnings, errors)
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))

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
        warnings = []
        errors = []
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_series_first(
            deliverable_info,
            'a',
            warnings.append,
            errors.append,
        )
        print(warnings, errors)
        self.assertEqual(0, len(warnings))
        self.assertEqual(0, len(errors))

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
        warnings = []
        errors = []
        deliverable_info = yamlutils.loads(deliverable_data)
        validate.validate_series_first(
            deliverable_info,
            'a',
            warnings.append,
            errors.append,
        )
        print(warnings, errors)
        self.assertEqual(0, len(warnings))
        self.assertEqual(0, len(errors))
