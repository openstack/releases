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
import os.path
import subprocess


def get_sdist_name(workdir, repo):
    "Check out the code."
    dest = os.path.join(workdir, repo)
    if not os.path.exists(os.path.join(dest, 'setup.py')):
        # Not a python project
        return None
    use_tox = repo.endswith('/pbr')
    if use_tox and not os.path.exists(os.path.join(dest, '.tox', 'venv')):
        # Use tox to set up a virtualenv so we can install the
        # dependencies for the package. This only seems to be
        # necessary for pbr, but...
        subprocess.check_output(
            ['tox', '-e', 'venv', '--notest'],
            cwd=dest,
        )
    if use_tox:
        python = '.tox/venv/bin/python'
    else:
        python = 'python'
    # Run it once and discard the result to ensure any setup_requires
    # dependencies are installed.
    cmd = [python, 'setup.py', '--name']
    subprocess.check_output(cmd, cwd=dest)
    # Run it again to get a clean version of the name.
    name = subprocess.check_output(cmd, cwd=dest).strip()
    return name
