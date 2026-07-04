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

from unittest import mock

from oslotest import base

from openstack_releases import gitutils


@mock.patch.object(gitutils, 'branch_exists')
@mock.patch.object(gitutils, 'get_full_branch_name')
class TestStableBranchExists(base.BaseTestCase):

    def test_series_name_resolves_to_stable_branch(
            self, mock_full_name, mock_exists):
        mock_full_name.return_value = 'stable/2026.1'
        mock_exists.return_value = True
        result = gitutils.stable_branch_exists('/tmp', 'openstack/nova',
                                               'gazpacho')
        self.assertEqual('stable/2026.1', result)
        mock_full_name.assert_called_once_with('gazpacho')
        mock_exists.assert_called_once_with('/tmp', 'openstack/nova',
                                            'stable', '2026.1')

    def test_series_name_branch_does_not_exist(
            self, mock_full_name, mock_exists):
        mock_full_name.return_value = 'stable/2026.1'
        mock_exists.return_value = False
        result = gitutils.stable_branch_exists('/tmp', 'openstack/nova',
                                               'gazpacho')
        self.assertEqual('', result)

    def test_eom_series_resolves_to_unmaintained(
            self, mock_full_name, mock_exists):
        mock_full_name.return_value = 'unmaintained/2024.1'
        mock_exists.return_value = True
        result = gitutils.stable_branch_exists('/tmp', 'openstack/nova',
                                               'caracal')
        self.assertEqual('unmaintained/2024.1', result)
        mock_exists.assert_called_once_with('/tmp', 'openstack/nova',
                                            'unmaintained', '2024.1')

    def test_release_id_falls_back_to_direct_check(
            self, mock_full_name, mock_exists):
        mock_full_name.side_effect = KeyError('2026.1')
        mock_exists.return_value = True
        result = gitutils.stable_branch_exists('/tmp', 'openstack/nova',
                                               '2026.1')
        self.assertEqual('stable/2026.1', result)
        mock_exists.assert_called_once_with('/tmp', 'openstack/nova',
                                            'stable', '2026.1')

    def test_release_id_branch_does_not_exist(
            self, mock_full_name, mock_exists):
        mock_full_name.side_effect = KeyError('2026.1')
        mock_exists.return_value = False
        result = gitutils.stable_branch_exists('/tmp', 'openstack/nova',
                                               '2026.1')
        self.assertEqual('', result)

    def test_unknown_series_returns_empty(
            self, mock_full_name, mock_exists):
        mock_full_name.side_effect = KeyError('nonexistent')
        mock_exists.return_value = False
        result = gitutils.stable_branch_exists('/tmp', 'openstack/nova',
                                               'nonexistent')
        self.assertEqual('', result)

    def test_independent_returns_empty(
            self, mock_full_name, mock_exists):
        mock_full_name.side_effect = KeyError('independent')
        mock_exists.return_value = False
        result = gitutils.stable_branch_exists('/tmp', 'openstack/nova',
                                               'independent')
        self.assertEqual('', result)

    def test_old_series_name_as_release_id(
            self, mock_full_name, mock_exists):
        """Old series without release-id falls back to series name.

        get_full_branch_name returns stable/<series-name>
        (e.g. stable/zed) since release_id falls back to the
        series name.
        """
        mock_full_name.return_value = 'stable/zed'
        mock_exists.return_value = True
        result = gitutils.stable_branch_exists('/tmp', 'openstack/nova',
                                               'zed')
        self.assertEqual('stable/zed', result)
        mock_exists.assert_called_once_with('/tmp', 'openstack/nova',
                                            'stable', 'zed')
