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

from oslotest import base

from openstack_releases.cmds import validate


class TestValidateLaunchpad(base.BaseTestCase):

    def test_no_launchpad_name(self):
        warnings = []
        errors = []
        validate.validate_launchpad(
            {},
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))

    def test_invalid_launchpad_name(self):
        warnings = []
        errors = []
        validate.validate_launchpad(
            {'launchpad': 'nonsense-name'},
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))

    def test_valid_launchpad_name(self):
        warnings = []
        errors = []
        validate.validate_launchpad(
            {'launchpad': 'oslo.config'},
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(0, len(errors))


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
            {'release-notes': 'http://docs.openstack.org/no-such-page'},
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
             'http://docs.openstack.org/releasenotes/oslo.config'},
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
                    'openstack/releases': 'http://docs.openstack.org/no-such-page',
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
                    'openstack/releases': 'http://docs.openstack.org/releasenotes/oslo.config',
                }
            },
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(0, len(errors))
