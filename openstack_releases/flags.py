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

"""Work with the flags within a deliverable file.
"""

NO_ARTIFACT_BUILD_JOB = 'no-artifact-build-job'
RETIRED = 'retired'


def has_flag(deliverable_info, repo_name, flag_name):
    """Return boolean indicating whether the flag is present for the repo.
    """
    all_settings = deliverable_info.get('repository-settings', {})
    repo_settings = all_settings.get(repo_name, {})
    flags = repo_settings.get('flags', [])
    return flag_name in flags
