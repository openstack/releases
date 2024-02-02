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


def generate_constraints_redirections(_deliverables, _series_status_data,
                                      future_releases=[]):
    redirections = []
    # Loop through all the releases for requirements
    for deliv in _deliverables.get_deliverable_history('requirements'):
        # Any open deliverables should point to master
        target = 'master'
        ref_type = 'branch'

        release_id = _series_status_data[deliv.series].release_id
        if not release_id:
            release_id = deliv.series
        # Unless there is a stable or unmaintained branch
        # Look at all branches We can't rely the ordering in the deliverable
        # file
        for branch in deliv.branches:
            # Set the target when the branch is 'stable/'
            # but ONLY If the target would otherwise be the master branch
            if target == 'master' and branch.name == 'stable/%s' % (release_id):
                target = branch.name
            # An open unmaintained branch should become the target in
            # preference over a master or stable branch
            elif branch.name == 'unmaintained/%s' % (release_id):
                target = branch.name

        # After looking at all the branches we now look for ${series}-eom
        # or a ${series}-eol tag
        for release in deliv.releases:
            # an EOM release is a probable target.
            if release.is_eom:
                # Select the EOM tag instad of a master or stable branch.
                # however if there is an unmaintained branch that's the
                # expected target until the series is marked EOL
                if target == 'master' or target == 'stable/%s' % (release_id):
                    target = str(release.version)
                    ref_type = 'tag'
            # If a series is marked as EOL then we that tag is the correct
            # destination, no options
            if release.is_eol:
                target = str(release.version)
                ref_type = 'tag'
                break

        # Insert into the beginning of the list so that redirections are
        # master -> juno
        status = 302 if target == 'master' else 301
        redirections.insert(0, dict(code=status, src=release_id,
                                    ref_type=ref_type, dst=target))

    for series in future_releases:
        redirections.insert(0, dict(code=302, src=series,
                                    ref_type='branch', dst='master'))

    return redirections
