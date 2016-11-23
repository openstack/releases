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
