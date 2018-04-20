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

import fixtures
from oslotest import base

from openstack_releases import series_status
from openstack_releases import yamlutils


class TestConstructSeriesStatus(base.BaseTestCase):

    _body = textwrap.dedent('''
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
        deliv_dir = os.path.join(self.tmpdir, 'deliverables')
        os.mkdir(deliv_dir)
        with open(os.path.join(deliv_dir, 'series_status.yaml'),
                  'w', encoding='utf-8') as f:
            f.write(self._body)

    def test_init(self):
        data = yamlutils.loads(self._body)
        status = series_status.SeriesStatus(data)
        self.assertIn('rocky', status)

    def test_from_directory(self):
        status = series_status.SeriesStatus.from_directory(self.tmpdir)
        self.assertIn('rocky', status)


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
