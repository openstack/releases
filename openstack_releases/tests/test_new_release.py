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

from oslotest import base

from openstack_releases.cmds import new_release


class TestIncrementVersion(base.BaseTestCase):

    def test_major(self):
        self.assertEqual(
            ['2', '0', '0'],
            new_release.increment_version(
                ['1', '0', '0'],
                (1, 0, 0),
            ),
        )

    def test_major_clear(self):
        self.assertEqual(
            ['2', '0', '0'],
            new_release.increment_version(
                ['1', '1', '1'],
                (1, 0, 0),
            ),
        )

    def test_minor(self):
        self.assertEqual(
            ['1', '1', '0'],
            new_release.increment_version(
                ['1', '0', '0'],
                (0, 1, 0),
            ),
        )

    def test_minor_clear(self):
        self.assertEqual(
            ['1', '2', '0'],
            new_release.increment_version(
                ['1', '1', '1'],
                (0, 1, 0),
            ),
        )

    def test_patch(self):
        self.assertEqual(
            ['1', '0', '1'],
            new_release.increment_version(
                ['1', '0', '0'],
                (0, 0, 1),
            ),
        )


class TestIncrementMilestoneVersion(base.BaseTestCase):

    def test_first_milestone(self):
        self.assertEqual(
            ['2', '0', '0', '0b1'],
            new_release.increment_milestone_version(
                ['1', '0', '0'],
                'milestone',
            ),
        )

    def test_second_milestone(self):
        self.assertEqual(
            ['2', '0', '0', '0b2'],
            new_release.increment_milestone_version(
                ['2', '0', '0', '0b1'],
                'milestone',
            ),
        )

    def test_third_milestone(self):
        self.assertEqual(
            ['2', '0', '0', '0b3'],
            new_release.increment_milestone_version(
                ['2', '0', '0', '0b2'],
                'milestone',
            ),
        )

    def test_first_rc(self):
        self.assertEqual(
            ['2', '0', '0', '0rc1'],
            new_release.increment_milestone_version(
                ['2', '0', '0', '0b3'],
                'rc',
            ),
        )

    def test_second_rc(self):
        self.assertEqual(
            ['2', '0', '0', '0rc2'],
            new_release.increment_milestone_version(
                ['2', '0', '0', '0rc1'],
                'rc',
            ),
        )
