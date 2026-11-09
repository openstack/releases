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

import os

import fixtures
from oslotest import base

from openstack_releases import pythonutils


class TestGetSdistName(base.BaseTestCase):
    def setUp(self):
        super().setUp()
        self.workdir = self.useFixture(fixtures.TempDir()).path
        self.repo = 'test-project'
        os.mkdir(os.path.join(self.workdir, self.repo))

    def test_get_dist_name__pyproject_toml(self):
        with open(
            os.path.join(self.workdir, self.repo, 'pyproject.toml'), 'w'
        ) as fh:
            print('[project]', file=fh)
            print('name = "foobar"', file=fh)

        name = pythonutils.get_sdist_name(self.workdir, self.repo)
        self.assertEqual('foobar', name)

    def test_get_dist_name__setup_cfg(self):
        with open(
            os.path.join(self.workdir, self.repo, 'setup.cfg'), 'w'
        ) as fh:
            print('[metadata]', file=fh)
            print('name = foobar', file=fh)

        name = pythonutils.get_sdist_name(self.workdir, self.repo)
        self.assertEqual('foobar', name)

    def test_get_dist_name__setup_cfg_and_pyproject_toml(self):
        with open(
            os.path.join(self.workdir, self.repo, 'pyproject.toml'), 'w'
        ) as fh:
            print('[build-system]', file=fh)
            print('build-backend = "pbr.build"', file=fh)
            print('requires = ["pbr>=7.0.0"]', file=fh)

        with open(
            os.path.join(self.workdir, self.repo, 'setup.cfg'), 'w'
        ) as fh:
            print('[metadata]', file=fh)
            print('name = foobar', file=fh)

        name = pythonutils.get_sdist_name(self.workdir, self.repo)
        self.assertEqual('foobar', name)

    def test_get_dist_name__empty_setup_cfg_and_pyproject_toml(self):
        with open(
            os.path.join(self.workdir, self.repo, 'pyproject.toml'), 'w'
        ) as fh:
            print('[build-system]', file=fh)
            print('build-backend = "pbr.build"', file=fh)
            print('requires = ["pbr>=7.0.0"]', file=fh)

        with open(
            os.path.join(self.workdir, self.repo, 'setup.cfg'), 'w'
        ) as fh:
            print('[bdist_wheel]', file=fh)
            print('universal = 1', file=fh)

        name = pythonutils.get_sdist_name(self.workdir, self.repo)
        self.assertIsNone(name)

    def test_get_dist_name__none(self):
        name = pythonutils.get_sdist_name(self.workdir, self.repo)
        self.assertIsNone(name)
