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

import requests


def link_exists(url):
    try:
        response = requests.head(
            url,
            headers={'user-agent': 'openstack-release-link-checker'},
        )
        missing = (
            (response.status_code // 100 != 2) or
            'Bad object id' in response.text
        )
    except requests.exceptions.ConnectionError as e:
        print('Failed to access %s: %s' % (url, e))
        missing = True
    return not missing


def tarball_url(version, project):
    repo_base = project['repo'].rsplit('/')[-1]
    base = project.get('tarball-base', repo_base)
    return '{s}/{r}/{n}-{v}.tar.gz'.format(
        s='https://tarballs.openstack.org',
        v=version,
        r=repo_base,
        n=base,
    )


def wheel_py2_url(version, project):
    repo_base = project['repo'].rsplit('/')[-1]
    base = project.get('tarball-base', repo_base)
    return '{s}/{r}/{n}-{v}-py2-none-any.whl'.format(
        s='https://tarballs.openstack.org',
        v=version,
        r=repo_base,
        n=base,
    )


def wheel_both_url(version, project):
    repo_base = project['repo'].rsplit('/')[-1]
    base = project.get('tarball-base', repo_base)
    return '{s}/{r}/{n}-{v}-py2.py3-none-any.whl'.format(
        s='https://tarballs.openstack.org',
        v=version,
        r=repo_base,
        n=base,
    )


def artifact_link(version, project, deliverable_info):
    mode = deliverable_info.get('artifact-link-mode', 'tarball')
    if mode == 'tarball':
        # Link the version number to the tarball for downloading.
        url = tarball_url(version, project)
        return '`{v} <{url}>`__'.format(v=version, url=url)
    elif mode == 'none':
        # Only show the version number.
        return version
    raise ValueError('Unrecognized artifact-link-mode: %r' % mode)


def signature_url(version, project):
    tb_url = tarball_url(version, project)
    return tb_url + '.asc'


def artifact_signature_link(version, type, project, deliverable_info):
    mode = deliverable_info.get('artifact-link-mode', 'tarball')
    if mode == 'tarball':
        url = signature_url(version, project)
        # Link the signature type to the tarball for downloading.
        return '`{t} <{url}>`__'.format(
            t=type,
            url=url,
        )
    elif mode == 'none':
        return ""
    raise ValueError('Unrecognized artifact-link-mode: %r' % mode)
