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

import packaging.version
import pbr.version

# The keys for this dict are the valid release types for OpenStack releases.
# The values are a three-tuple that contains:
#  1. constructor:  The function used to convert the version string in to a
#                   *Verion object.
#  2. exception:    The exception raised by the constructor iff version
#                   string is invalid in some way.
#  3. canonicalise: The function used to canonicalise the *Version object.
#                   Used to verify that the version string is already in the
#                   canonical form
_VALIDATORS = {'std': (pbr.version.SemanticVersion.from_pip_string,
                       ValueError,
                       lambda x: x.release_string()),
               'xstatic': (packaging.version.Version,
                           packaging.version.InvalidVersion,
                           lambda x: str(x)),
               }
_VALIDATORS['fuel'] = _VALIDATORS['std']
_VALIDATORS['openstack-manuals'] = _VALIDATORS['std']
_VALIDATORS['puppet'] = _VALIDATORS['std']
_VALIDATORS['nodejs'] = _VALIDATORS['std']
_VALIDATORS['neutron'] = _VALIDATORS['std']
_VALIDATORS['horizon'] = _VALIDATORS['std']


def validate_version(versionstr, release_type='std', pre_ok=True):
    """Given a version string, yield error messages if it is "bad"

    Apply our SemVer rules to version strings and report all issues.

    """
    if not pre_ok:
        for pre_indicator in ['a', 'b', 'rc']:
            if pre_indicator in versionstr:
                yield('Version %s looks like a pre-release and the release '
                      'model does not allow for it' % versionstr)

    if release_type not in _VALIDATORS:
        yield 'Release Type %r not valid using \'std\' instead' % release_type
        release_type = 'std'

    constructor, exception, canonicalise = _VALIDATORS[release_type]
    try:
        semver = constructor(versionstr)
    except exception as err:
        yield 'Invalid version: %s' % err
    else:
        # Make sure we didn't change the version to meet the canonical form.
        canonical = canonicalise(semver)
        if canonical != versionstr:
            yield 'Version %r does not match canonical form %r' % \
                (versionstr, canonical)


def canonical_version(versionstr, release_type='std'):
    """Given a version string verify it is in the canonical form."""
    errors = list(validate_version(versionstr, release_type))
    if errors:
        raise ValueError(errors[-1])
    return versionstr
