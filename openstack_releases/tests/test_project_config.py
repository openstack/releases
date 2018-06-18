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

import os.path
import textwrap

from oslotest import base

from openstack_releases.cmds import validate
from openstack_releases import deliverable
from openstack_releases import project_config
from openstack_releases.tests import fixtures as or_fixtures


class TestReleaseJobsGlobal(base.BaseTestCase):

    def setUp(self):
        super().setUp()
        self.ctx = validate.ValidationContext()

    def test_no_artifact_flag(self):
        deliv = deliverable.Deliverable(
            team='team',
            series='series',
            name='name',
            data={
                'repository-settings': {
                    'openstack/releases': {
                        'flags': [
                            'no-artifact-build-job',
                        ],
                    },
                },
            },
        )
        self.ctx._zuul_projects = {'validate-projects-by-name': {}}
        project_config.require_release_jobs_for_repo(
            deliv,
            deliv.repos[0],
            'std',
            self.ctx,
        )
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

    def test_retired_flag(self):
        deliv = deliverable.Deliverable(
            team='team',
            series='series',
            name='name',
            data={
                'repository-settings': {
                    'openstack/releases': {
                        'flags': [
                            'retired',
                        ]
                    }
                }
            },
        )
        self.ctx._zuul_projects = {'validate-projects-by-name': {}}
        project_config.require_release_jobs_for_repo(
            deliv,
            deliv.repos[0],
            'std',
            self.ctx,
        )
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

    def test_no_zuul_projects(self):
        deliv = deliverable.Deliverable(
            team='team',
            series='series',
            name='name',
            data={
                'repository-settings': {
                    'openstack/releases': {},
                },
            },
        )
        self.ctx._zuul_projects = {'validate-projects-by-name': {}}
        project_config.require_release_jobs_for_repo(
            deliv,
            deliv.repos[0],
            'std',
            self.ctx,
        )
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))

    def test_one_expected_job(self):
        deliv = deliverable.Deliverable(
            team='team',
            series='series',
            name='name',
            data={
                'repository-settings': {
                    'openstack/releases': {},
                },
            },
        )
        self.ctx._zuul_projects = {
            'openstack/releases': {
                'templates': [
                    'publish-to-pypi',
                ],
            },
        }
        project_config.require_release_jobs_for_repo(
            deliv,
            deliv.repos[0],
            'python-pypi',
            self.ctx,
        )
        self.ctx.show_summary()
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(0, len(self.ctx.errors))

    def test_two_expected_jobs(self):
        deliv = deliverable.Deliverable(
            team='team',
            series='series',
            name='name',
            data={
                'repository-settings': {
                    'openstack/releases': {},
                },
            },
        )
        self.ctx._zuul_projects = {
            'openstack/releases': {
                'templates': [
                    'publish-to-pypi',
                    'puppet-tarball-jobs',
                ],
            }
        }
        project_config.require_release_jobs_for_repo(
            deliv,
            deliv.repos[0],
            'python-pypi',
            self.ctx,
        )
        self.assertEqual(0, len(self.ctx.warnings))
        self.assertEqual(1, len(self.ctx.errors))


class TestReleaseJobsInTree(base.BaseTestCase):

    def setUp(self):
        super().setUp()
        self.ctx = validate.ValidationContext()
        self.repo = self.useFixture(
            or_fixtures.GitRepoFixture(
                self.ctx.workdir,
                'openstack/release-test',
            )
        )
        os.mkdir(os.path.join(self.ctx.workdir, self.repo.name, '.zuul.d'))
        os.mkdir(os.path.join(self.ctx.workdir, self.repo.name, 'zuul.d'))

    def test_none(self):
        templates = project_config.read_templates_from_repo(
            self.ctx.workdir, self.repo.name)
        self.assertEqual([], templates)

    def test_dot_zuul(self):
        filename = os.path.join(self.repo.path, '.zuul.yaml')
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(textwrap.dedent('''
            - project:
                templates:
                  - noop-jobs
                  - publish-to-pypi-python3
            '''))
        templates = project_config.read_templates_from_repo(
            self.ctx.workdir, self.repo.name)
        self.assertEqual(['noop-jobs', 'publish-to-pypi-python3'], templates)

    def test_zuul(self):
        filename = os.path.join(self.repo.path, 'zuul.yaml')
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(textwrap.dedent('''
            - project:
                templates:
                  - noop-jobs
                  - publish-to-pypi-python3
            '''))
        templates = project_config.read_templates_from_repo(
            self.ctx.workdir, self.repo.name)
        self.assertEqual(['noop-jobs', 'publish-to-pypi-python3'], templates)

    def test_zuul_dot_d(self):
        filename = os.path.join(self.repo.path, 'zuul.d/projects.yaml')
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(textwrap.dedent('''
            - project:
                templates:
                  - noop-jobs
                  - publish-to-pypi-python3
            '''))
        templates = project_config.read_templates_from_repo(
            self.ctx.workdir, self.repo.name)
        self.assertEqual(['noop-jobs', 'publish-to-pypi-python3'], templates)

    def test_dot_zuul_dot_d(self):
        filename = os.path.join(self.repo.path, '.zuul.d/projects.yaml')
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(textwrap.dedent('''
            - project:
                templates:
                  - noop-jobs
                  - publish-to-pypi-python3
            '''))
        templates = project_config.read_templates_from_repo(
            self.ctx.workdir, self.repo.name)
        self.assertEqual(['noop-jobs', 'publish-to-pypi-python3'], templates)
