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

import importlib
import os
import sys


def get_versions(workdir, repo):
    """Get the package versions from packages."""
    versions = []

    # Switch to the workdir
    start_path = os.getcwd()
    repo_dir = '%s/%s' % (workdir, repo)
    os.chdir(repo_dir)

    # Add the repo to the PYTHONPATH so we can import its contents
    sys.path.append(repo_dir)

    # Extract PACAKGE_VERSION from any xstatic packages found
    try:
        for name in os.listdir('xstatic/pkg'):
            if '__' in name:
                continue
            if os.path.isdir('xstatic/pkg/%s' % name):
                xs = importlib.import_module('xstatic.pkg.%s' % name)
                versions.append(xs.PACKAGE_VERSION)
    finally:
        # Get back to our original state
        sys.path.pop()
        os.chdir(start_path)

    return versions
