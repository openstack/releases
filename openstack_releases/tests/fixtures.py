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

import logging
import os.path
import re
import textwrap

import fixtures

from openstack_releases import processutils

LOG = logging.getLogger(__name__)


class GPGKeyFixture(fixtures.Fixture):
    """Creates a GPG key for testing.

    It's recommended that this be used in concert with a unique home
    directory.
    """

    def setUp(self):
        super(GPGKeyFixture, self).setUp()
        # Force a temporary home directory with a short path so the
        # gpg commands do not complain about an excessively long
        # value.
        self.useFixture(fixtures.TempHomeDir('/tmp'))
        tempdir = self.useFixture(fixtures.TempDir('/tmp'))
        gnupg_version_re = re.compile(r'^gpg\s.*\s([\d+])\.([\d+])\.([\d+])')
        gnupg_version = processutils.check_output(
            ['gpg', '--version'],
            cwd=tempdir.path).decode('utf-8')
        for line in gnupg_version.split('\n'):
            gnupg_version = gnupg_version_re.match(line)
            if gnupg_version:
                gnupg_version = (int(gnupg_version.group(1)),
                                 int(gnupg_version.group(2)),
                                 int(gnupg_version.group(3)))
                break
        else:
            if gnupg_version is None:
                gnupg_version = (0, 0, 0)

        config_file = tempdir.path + '/key-config'
        LOG.debug('creating gpg config file in %s', config_file)
        with open(config_file, 'wt') as f:
            if gnupg_version[0] == 2 and gnupg_version[1] >= 1:
                f.write(textwrap.dedent("""
                %no-protection
                %transient-key
                """))
            f.write(textwrap.dedent("""
            %no-ask-passphrase
            Key-Type: RSA
            Name-Real: Example Key
            Name-Comment: N/A
            Name-Email: example@example.com
            Expire-Date: 2d
            %commit
            """))

        # Note that --quick-random (--debug-quick-random in GnuPG 2.x)
        # does not have a corresponding preferences file setting and
        # must be passed explicitly on the command line instead
        if gnupg_version[0] == 1:
            gnupg_random = '--quick-random'
        elif gnupg_version[0] >= 2:
            gnupg_random = '--debug-quick-random'
        else:
            gnupg_random = ''

        cmd = ['gpg', '--gen-key', '--batch']
        if gnupg_random:
            cmd.append(gnupg_random)
        cmd.append('key-config')

        LOG.debug('generating gpg key')
        processutils.check_call(cmd, cwd=tempdir.path)


class GitRepoFixture(fixtures.Fixture):

    def __init__(self, workdir, name):
        self.workdir = workdir
        self.name = name
        self.path = os.path.join(self.workdir, self.name)
        super().__init__()

    def setUp(self):
        super().setUp()
        self.useFixture(GPGKeyFixture())
        os.makedirs(self.path)
        LOG.debug('initializing repo in %s', self.path)
        self.git('init', '.')
        self.git('config', '--local', 'user.email', 'example@example.com')
        self.git('config', '--local', 'user.name', 'super developer')
        self.git('config', '--local', 'user.signingkey',
                 'example@example.com')

    def git(self, *args):
        output = processutils.check_output(
            ['git'] + list(args),
            cwd=self.path,
        )
        return output

    def commit(self, message='commit message'):
        LOG.debug('committing %r', message)
        self.git('add', '.')
        self.git('commit', '-m', message)
        sha = self.git('log', '-n', '1', '--pretty=format:%H')
        LOG.debug('SHA: %r', sha)
        return sha.decode('utf-8').strip()

    def add_file(self, name):
        LOG.debug('adding file %r', name)
        with open(os.path.join(self.path, name), 'w') as f:
            f.write('adding %s\n' % name)
        return self.commit('add %s' % name)

    def tag(self, version):
        LOG.debug('tagging %r', version)
        self.git('tag', '-s', '-m', version, version)
