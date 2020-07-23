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

from sphinx.util import logging


LOG = logging.getLogger(__name__)


def generate_constraints_redirections(_deliverables, future_releases=[]):
    redirections = []
    # Loop through all the releases for requirements
    for deliv in _deliverables.get_deliverable_history('requirements'):
        # Any open deliverables should point to master
        target = 'master'
        ref_type = 'branch'

        # Unless there is a specific stable branch
        for branch in deliv.branches:
            if branch.name == 'stable/%s' % (deliv.series):
                target = branch.name
                break

        # Or we have a ${series}-eol tag
        for release in deliv.releases:
            if release.is_eol:
                target = str(release.version)
                ref_type = 'tag'
                break

        # Insert into the beginning of the list so that redirections are
        # master -> juno
        status = 302 if target == 'master' else 301
        redirections.insert(0, dict(code=status, src=deliv.series,
                                    ref_type=ref_type, dst=target))

    for series in future_releases:
        redirections.insert(0, dict(code=302, src=series,
                                    ref_type='branch', dst='master'))

    return redirections
