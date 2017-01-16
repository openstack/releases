# -*- encoding: utf-8 -*-
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

import pkgutil

import mock
from oslotest import base

from openstack_releases import wiki


# Sample content from wiki.openstack.org/wiki/CrossProjectLiaisons
# on 16 Jan 2017.
_PAGE = pkgutil.get_data('openstack_releases.tests',
                         'CrossProjectLiaisons.txt')
_PAGE = _PAGE.decode('utf-8')


class TestWikiParser(base.BaseTestCase):

    def test_get_section(self):
        actual = list(wiki.get_page_section(_PAGE, 'Oslo'))
        expected = _PAGE.splitlines()[3:66]
        self.assertEqual(expected, actual)

    def test_get_wiki_table(self):
        all = list(wiki.get_wiki_table(_PAGE, 'Release Management'))
        self.assertEqual(32, len(all))
        actual = all[0]
        expected = {
            'Project': 'Barbican',
            'Liaison': 'Dave McCowan',
            'IRC Handle': 'dave-mccowan',
        }
        self.assertEqual(expected, actual)

    def test_get_liaison_data(self):
        with mock.patch.object(wiki, 'get_wiki_page') as gwp:
            gwp.return_value = _PAGE
            data = wiki.get_liaison_data()
        self.assertIn('barbican', data)
        actual = data['barbican']
        expected = {
            'Project': 'Barbican',
            'Liaison': 'Dave McCowan',
            'IRC Handle': 'dave-mccowan',
        }
        self.assertEqual(expected, actual)
