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

import datetime
import os
import os.path
import textwrap
from unittest import mock

import fixtures
from oslotest import base

from openstack_releases import series_status
from openstack_releases import yamlutils


class TestConstructSeriesStatus(base.BaseTestCase):

    _body = textwrap.dedent('''
    - name: stein
      status: future
      initial-release: 2019-04-11
      next-phase:
        status: development
        date: 2018-08-30
      signing-key:
        key: 12345678901234567890
        start: 2018-08-30
        end: 2019-06-01
    - name: rocky
      status: development
      initial-release: 2018-08-30
      next-phase:
        status: maintained
        date: 2018-08-30
    - name: queens
      status: maintained
      initial-release: 2018-02-28
      next-phase:
        status: extended maintenance
        date: 2019-08-25
    ''')

    def setUp(self):
        super().setUp()
        self.tmpdir = self.useFixture(fixtures.TempDir()).path
        with open(os.path.join(self.tmpdir, 'series_status.yaml'),
                  'w', encoding='utf-8') as f:
            f.write(self._body)

    def test_init(self):
        data = yamlutils.loads(self._body)
        status = series_status.SeriesStatus(data)
        self.assertIn('rocky', status)

    def test_from_directory(self):
        status = series_status.SeriesStatus.from_directory(self.tmpdir)
        self.assertIn('rocky', status)

    def test_independent_series(self):
        data = yamlutils.loads(self._body)
        status = series_status.SeriesStatus(data)
        self.assertIn('independent', status)


class TestSeries(base.BaseTestCase):

    def setUp(self):
        super().setUp()

    def test_next_phase(self):
        s = series_status.Series({
            'name': 'rocky',
            'status': 'development',
            'initial-release': datetime.date(2018, 8, 30),
            'next-phase': {
                'status': 'maintained',
                'date': datetime.date(2018, 8, 30),
            },
        })
        self.assertIsNotNone(s.next_phase)

    def test_no_next_phase(self):
        s = series_status.Series({
            'name': 'rocky',
            'status': 'development',
            'initial-release': datetime.date(2018, 8, 30),
        })
        self.assertIsNone(s.next_phase)

    def test_eol_date(self):
        s = series_status.Series({
            'name': 'icehouse',
            'status': 'end of life',
            'initial-release': datetime.date(2014, 4, 17),
            'eol-date': datetime.date(2015, 7, 2),
        })
        self.assertIsNotNone(s.eol_date)

    def test_no_eol_date(self):
        s = series_status.Series({
            'name': 'austin',
            'status': 'end of life',
            'initial-release': datetime.date(2010, 10, 21),
        })
        self.assertIsNone(s.eol_date)


class TestGetStableBranchId(base.BaseTestCase):

    def _make_status(self, series_data):
        data = [dict(d, name=name) for name, d in series_data.items()]
        return series_status.SeriesStatus(data)

    @mock.patch.object(series_status.SeriesStatus, 'default')
    def test_returns_release_id(self, mock_default):
        mock_default.return_value = self._make_status({
            'gazpacho': {
                'status': 'maintained',
                'initial-release': '2026-04-01',
                'release-id': '2026.1',
            },
        })
        self.assertEqual('2026.1',
                         series_status.get_stable_branch_id('gazpacho'))

    @mock.patch.object(series_status.SeriesStatus, 'default')
    def test_falls_back_to_series_name(self, mock_default):
        mock_default.return_value = self._make_status({
            'zed': {
                'status': 'end of life',
                'initial-release': '2022-10-05',
            },
        })
        self.assertEqual('zed',
                         series_status.get_stable_branch_id('zed'))

    @mock.patch.object(series_status.SeriesStatus, 'default')
    def test_unknown_series_raises(self, mock_default):
        mock_default.return_value = self._make_status({
            'gazpacho': {
                'status': 'maintained',
                'initial-release': '2026-04-01',
                'release-id': '2026.1',
            },
        })
        self.assertRaises(KeyError,
                          series_status.get_stable_branch_id, 'nonexistent')
