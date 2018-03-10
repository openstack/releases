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
import subprocess


LOG = logging.getLogger(__name__)


from subprocess import CalledProcessError  # noqa


def _multi_line_log(level, msg):
    for line in msg.splitlines():
        LOG.log(level, line)


def check_call(*popenargs, timeout=None, **kwargs):
    # A variation of subprocess.check_call that captures and then
    # logs the output of the command which makes it easier for tests
    # to capture it.

    kwargs['stdout'] = subprocess.PIPE
    kwargs['stderr'] = subprocess.STDOUT

    cmd = kwargs.get("args")
    if cmd is None:
        cmd = popenargs[0]
    if 'cwd' in kwargs:
        LOG.debug('cwd = {}'.format(kwargs['cwd']))
    LOG.debug('$ {}'.format(' '.join(cmd)))

    completed = subprocess.run(*popenargs, **kwargs)
    _multi_line_log(logging.DEBUG, completed.stdout.decode('utf-8'))

    if completed.returncode:
        raise subprocess.CalledProcessError(completed.returncode, cmd)
    return 0


def check_output(*popenargs, timeout=None, **kwargs):
    # A variation of subprocess.check_output that captures stderr and
    # logs it instead of letting it go to the console directly to make
    # it easier for tests to capture it.

    # NOTE(dhellmann): copied from subprocess.py vv
    if 'stdout' in kwargs:
        raise ValueError('stdout argument not allowed, it will be overridden.')
    if 'input' in kwargs and kwargs['input'] is None:
        # Explicitly passing input=None was previously equivalent to passing an
        # empty string. That is maintained here for backwards compatibility.
        kwargs['input'] = '' if kwargs.get('universal_newlines', False) else b''
    # NOTE(dhellmann): end copied from subprocess.py ^^

    cmd = kwargs.get("args")
    if cmd is None:
        cmd = popenargs[0]
    if 'cwd' in kwargs:
        LOG.debug('cwd = {}'.format(kwargs['cwd']))
    LOG.debug('$ {}'.format(' '.join(cmd)))

    if 'stderr' not in kwargs:
        kwargs['stderr'] = subprocess.PIPE

    completed = subprocess.run(*popenargs,
                               stdout=subprocess.PIPE,
                               timeout=timeout,
                               check=True,
                               **kwargs)

    if completed.stderr:
        _multi_line_log(logging.WARNING, completed.stderr.decode('utf-8'))

    return completed.stdout
