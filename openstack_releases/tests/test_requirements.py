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

import mock
from oslotest import base
import pkg_resources

from openstack_releases import requirements


class TestParseRequirements(base.BaseTestCase):

    def test_empty(self):
        self.assertEqual({}, requirements.parse_requirements(''))
        self.assertEqual({}, requirements.parse_requirements('\n'))

    def test_comments(self):
        self.assertEqual({}, requirements.parse_requirements('#'))
        self.assertEqual({}, requirements.parse_requirements('#\n'))

    def test_simple(self):
        self.assertEqual(
            [('', 'pbr')],
            list(requirements.parse_requirements(textwrap.dedent('''
            pbr>=1.6
            ''')).keys()),
        )

    def test_multiline(self):
        self.assertEqual(
            [('', 'keyring'),
             ('', 'pbr')],
            list(
                sorted(
                    requirements.parse_requirements(
                        textwrap.dedent('''
                        pbr>=1.6
                        keyring==7.3
                        ''')
                    ).keys()
                )
            )
        )


class TestGetMinSpecifier(base.BaseTestCase):

    def test_none(self):
        actual = requirements.get_min_specifier(
            pkg_resources.Requirement.parse('pbr').specifier,
        )
        self.assertIsNone(actual)

    def test_greater(self):
        actual = requirements.get_min_specifier(
            pkg_resources.Requirement.parse('pbr>1.6').specifier,
        )
        self.assertEqual('1.6', actual.version)

    def test_greater_equal(self):
        actual = requirements.get_min_specifier(
            pkg_resources.Requirement.parse('pbr>=1.6').specifier,
        )
        self.assertEqual('1.6', actual.version)


class TestCompareLowerBounds(base.BaseTestCase):

    def test_new_requirement(self):
        warnings = []
        old = {
        }
        new = {
            (None, 'pbr'): pkg_resources.Requirement.parse('pbr'),
        }
        requirements.compare_lower_bounds(
            old, new, warnings.append,
        )
        print(warnings)
        self.assertEqual(1, len(warnings))

    def test_dropped_requirement(self):
        warnings = []
        old = {
            (None, 'pbr'): pkg_resources.Requirement.parse('pbr'),
        }
        new = {
        }
        requirements.compare_lower_bounds(
            old, new, warnings.append,
        )
        print(warnings)
        self.assertEqual(0, len(warnings))

    def test_no_lower(self):
        warnings = []
        old = {
            (None, 'pbr'): pkg_resources.Requirement.parse('pbr'),
        }
        new = {
            (None, 'pbr'): pkg_resources.Requirement.parse('pbr'),
        }
        requirements.compare_lower_bounds(
            old, new, warnings.append,
        )
        print(warnings)
        self.assertEqual(0, len(warnings))

    def test_new_lower(self):
        warnings = []
        old = {
            (None, 'pbr'): pkg_resources.Requirement.parse('pbr'),
        }
        new = {
            (None, 'pbr'): pkg_resources.Requirement.parse('pbr>=1.6'),
        }
        requirements.compare_lower_bounds(
            old, new, warnings.append,
        )
        print(warnings)
        self.assertEqual(1, len(warnings))

    def test_raised_lower(self):
        warnings = []
        old = {
            (None, 'pbr'): pkg_resources.Requirement.parse('pbr>=1.5'),
        }
        new = {
            (None, 'pbr'): pkg_resources.Requirement.parse('pbr>=1.6'),
        }
        requirements.compare_lower_bounds(
            old, new, warnings.append,
        )
        print(warnings)
        self.assertEqual(1, len(warnings))

    def test_new_lower_format(self):
        warnings = []
        old = {
            (None, 'pbr'): pkg_resources.Requirement.parse('pbr>=1.6'),
        }
        new = {
            (None, 'pbr'): pkg_resources.Requirement.parse('pbr>=1.6.0'),
        }
        requirements.compare_lower_bounds(
            old, new, warnings.append,
        )
        print(warnings)
        self.assertEqual(0, len(warnings))

    def test_new_lower_comparator(self):
        warnings = []
        old = {
            (None, 'pbr'): pkg_resources.Requirement.parse('pbr>=1.6'),
        }
        new = {
            (None, 'pbr'): pkg_resources.Requirement.parse('pbr>1.6'),
        }
        requirements.compare_lower_bounds(
            old, new, warnings.append,
        )
        print(warnings)
        self.assertEqual(1, len(warnings))


class TestFindBadLowerBoundsIncreases(base.BaseTestCase):

    @mock.patch('openstack_releases.requirements.get_requirements_at_ref')
    def test_skip_for_beta(self, get_req):
        warnings = []
        get_req.side_effect = AssertionError('should not be called')
        requirements.find_bad_lower_bound_increases(
            None, None, '1.0.0', '2.0.0.0b1', None,
            warnings.append,
        )
        print(warnings)
        self.assertEqual(0, len(warnings))

    @mock.patch('openstack_releases.requirements.get_requirements_at_ref')
    def test_skip_for_rc(self, get_req):
        warnings = []
        get_req.side_effect = AssertionError('should not be called')
        requirements.find_bad_lower_bound_increases(
            None, None, '1.0.0', '2.0.0.0rc1', None,
            warnings.append,
        )
        print(warnings)
        self.assertEqual(0, len(warnings))

    @mock.patch('openstack_releases.requirements.get_requirements_at_ref')
    def test_skip_for_zero_patch_major(self, get_req):
        warnings = []
        get_req.side_effect = AssertionError('should not be called')
        requirements.find_bad_lower_bound_increases(
            None, None, '1.0.0', '2.0.0', None,
            warnings.append,
        )
        print(warnings)
        self.assertEqual(0, len(warnings))

    @mock.patch('openstack_releases.requirements.get_requirements_at_ref')
    def test_skip_for_zero_patch_minor(self, get_req):
        warnings = []
        get_req.side_effect = AssertionError('should not be called')
        requirements.find_bad_lower_bound_increases(
            None, None, '1.0.0', '1.1.0', None,
            warnings.append,
        )
        print(warnings)
        self.assertEqual(0, len(warnings))
