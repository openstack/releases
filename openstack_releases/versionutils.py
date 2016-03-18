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

from __future__ import unicode_literals

import pbr.version


def validate_version(versionstr):
    """Given a version string, yield error messages if it is "bad"

    Apply our SemVer rules to version strings and report all issues.

    """
    # Apply pbr rules
    try:
        semver = pbr.version.SemanticVersion.from_pip_string(versionstr)
    except ValueError as err:
        yield 'Invalid version: %s' % err
    else:
        # Make sure pbr didn't change the version to meet the canonical form.
        canonical = semver.release_string()
        if canonical != versionstr:
            yield 'Version %r does not match canonical form %r' % \
                (versionstr, canonical)
