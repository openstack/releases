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

import fixtures
import json
import mock
from oslotest import base

from openstack_releases import npmutils


class TestModuleDetection(base.BaseTestCase):

    def test_no_metadata(self):

        def exists(name):
            if name.endswith('package.json'):
                return False

        with mock.patch('os.path.exists', exists):
            is_mod = npmutils.looks_like_a_module(
                '.', 'openstack/monasca-kibana-plugin')
        self.assertFalse(is_mod)

    def test_with_metadata(self):

        def exists(name):
            if name.endswith('package.json'):
                return True

        with mock.patch('os.path.exists', exists):
            is_mod = npmutils.looks_like_a_module(
                '.', 'openstack/monasca-kibana-plugin')
        self.assertTrue(is_mod)


class TestGetMetadata(base.BaseTestCase):

    def setUp(self):
        super(TestGetMetadata, self).setUp()
        self.tmpdir = self.useFixture(fixtures.TempDir()).path
        self.repo = 'foo'
        self.mdfn = os.path.join(self.tmpdir, self.repo, 'package.json')
        os.makedirs(os.path.join(self.tmpdir, self.repo))
        self.expected = {
            "name": "monasca-kibana-plugin",
            "version": "0.0.5",
            "description": "fake description",
            "author": "OpenStack",
            "license": "Apache-2.0",
        }

        with open(self.mdfn, 'w') as f:
            f.write(json.dumps(self.expected))

    def test_get_metadata(self):
        md = npmutils.get_metadata(self.tmpdir, self.repo)
        self.assertEqual(self.expected, md)

    def test_get_version(self):
        ver = npmutils.get_version(self.tmpdir, self.repo)
        self.assertEqual('0.0.5', ver)
