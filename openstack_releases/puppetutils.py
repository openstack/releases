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

import json
import os.path


def looks_like_a_module(workdir, repo):
    "Does the directory look like it contains a puppet module?"
    if not os.path.exists(os.path.join(workdir, repo, 'metadata.json')):
        return False
    return any([
        os.path.exists(os.path.join(workdir, repo, 'lib')),
        os.path.exists(os.path.join(workdir, repo, 'manifests')),
    ])


def get_metadata(workdir, repo):
    "Load the metadata.json file from the repo"
    with open(os.path.join(workdir, repo, 'metadata.json'), 'r') as f:
        body = f.read()
    return json.loads(body)


def get_version(workdir, repo):
    "Get the version string from the project metadata."
    return get_metadata(workdir, repo).get('version')
