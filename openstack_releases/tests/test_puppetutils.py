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

from openstack_releases import puppetutils


class TestModuleDetection(base.BaseTestCase):

    def test_no_metadata(self):

        def exists(name):
            if name.endswith('metadata.json'):
                return False

        with mock.patch('os.path.exists', exists):
            is_mod = puppetutils.looks_like_a_module(
                '.', 'openstack/puppet-watcher')
        self.assertFalse(is_mod)

    def test_no_lib_or_manifests(self):

        def exists(name):
            if name.endswith('metadata.json'):
                return True
            return False

        with mock.patch('os.path.exists', exists):
            is_mod = puppetutils.looks_like_a_module(
                '.', 'openstack/puppet-watcher')
        self.assertFalse(is_mod)

    def test_with_lib(self):

        def exists(name):
            if name.endswith('metadata.json'):
                return True
            if name.endswith('lib'):
                return True
            return False

        with mock.patch('os.path.exists', exists):
            is_mod = puppetutils.looks_like_a_module(
                '.', 'openstack/puppet-watcher')
        self.assertTrue(is_mod)

    def test_with_manifests(self):

        def exists(name):
            if name.endswith('metadata.json'):
                return True
            if name.endswith('manifests'):
                return True
            return False

        with mock.patch('os.path.exists', exists):
            is_mod = puppetutils.looks_like_a_module(
                '.', 'openstack/puppet-watcher')
        self.assertTrue(is_mod)


class TestGetMetadata(base.BaseTestCase):

    def setUp(self):
        super(TestGetMetadata, self).setUp()
        self.tmpdir = self.useFixture(fixtures.TempDir()).path
        self.repo = 'foo'
        self.mdfn = os.path.join(self.tmpdir, self.repo, 'metadata.json')
        os.makedirs(os.path.join(self.tmpdir, self.repo))
        self.expected = {
            "name": "openstack-zaqar",
            "version": "10.1.0",
            "author": "OpenStack Contributors",
            "summary": "Puppet module for OpenStack Zaqar",
            "license": "Apache-2.0",
            "source": "git://github.com/openstack/puppet-zaqar.git",
            "project_page": "https://launchpad.net/puppet-zaqar",
            "issues_url": "https://bugs.launchpad.net/puppet-zaqar",
            "description": "Installs and configures OpenStack Zaqar."
        }

        with open(self.mdfn, 'w') as f:
            f.write(json.dumps(self.expected))

    def test_get_metadata(self):
        md = puppetutils.get_metadata(self.tmpdir, self.repo)
        self.assertEqual(self.expected, md)

    def test_get_version(self):
        ver = puppetutils.get_version(self.tmpdir, self.repo)
        self.assertEqual('10.1.0', ver)
