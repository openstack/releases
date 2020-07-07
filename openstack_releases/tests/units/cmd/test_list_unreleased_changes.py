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
import textwrap

from oslotest import base

from openstack_releases.cmds import list_unreleased_changes as luc


class TestStableStatus(base.BaseTestCase):

    _data = json.loads(textwrap.dedent('''
        [
            {
                "repo": "openstack/castellan",
                "branch": "victoria",
                "commits": {
                    "range": [
                        "3.2.0",
                        "3a3a738"
                    ],
                    "logs": [
                        "* 3a3a738 2020-06-26 13:51:12 +0200 Bump vault version"
                    ]
                },
                "error": false,
                "not_yet_released": false,
                "msg": ""
            },
            {
                "repo": "openstack/devstack-plugin-amqp1",
                "branch": "victoria",
                "commits": null,
                "error": false,
                "not_yet_released": true,
                "msg": "openstack/devstack-plugin-amqp1 has not yet been released"
            },
            {
                "repo": "openstack/oslo.cache",
                "branch": "victoria",
                "commits": {
                    "range": [
                        "2.5.0",
                        "f3f006c"
                    ],
                    "logs": [
                        "* a5ff884 2020-05-04 18:18:10 +0200 Align contributing doc with oslo's policy"
                    ]
                },
                "error": false,
                "not_yet_released": false,
                "msg": ""
            },
            {
                "repo": "openstack/oslo.service",
                "branch": "victoria",
                "commits": {
                    "range": [
                        "2.3.1",
                        "585768b"
                    ],
                    "logs": []
                },
                "error": false,
                "not_yet_released": false,
                "msg": ""
            },
            {
                "repo": "openstack/devstack-plugin-kafka",
                "branch": "victoria",
                "commits": null,
                "error": false,
                "not_yet_released": true,
                "msg": "openstack/devstack-plugin-kafka has not yet been released"
            },
            {
                "repo": "openstack/tttt",
                "branch": "victoria",
                "commits": null,
                "error": true,
                "not_yet_released": false,
                "msg": "fatal: repository 'https://opendev.org/openstack/tttt' not found"
            }
        ]
    '''))  # noqa

    def test_filter_results(self):
        results = luc.filter_results(self._data)
        self.assertEqual(6, len(results))
        results = luc.filter_results(self._data, ignore_all=True)
        self.assertEqual(2, len(results))
        results = luc.filter_results(self._data, ignore_errors=True)
        self.assertEqual(5, len(results))
        results = luc.filter_results(self._data, ignore_not_yet_released=True)
        self.assertEqual(4, len(results))
        results = luc.filter_results(self._data,
                                     ignore_not_yet_released=True,
                                     ignore_errors=True)
        self.assertEqual(3, len(results))
        results = luc.filter_results(self._data, ignore_no_results=True)
        self.assertEqual(2, len(results))

    def test_generate_output(self):
        results = luc.generate_output(self._data, output_format='json')
        self.assertEqual(json.dumps(self._data, indent=4), results)
        results = luc.generate_output(self._data, ignore_all=True)
        expected_result = textwrap.dedent('''\
            [ Unreleased changes in openstack/castellan (victoria) ]
            Changes between 3.2.0 and 3a3a738
            * 3a3a738 2020-06-26 13:51:12 +0200 Bump vault version
            [ Unreleased changes in openstack/oslo.cache (victoria) ]
            Changes between 2.5.0 and f3f006c
            * a5ff884 2020-05-04 18:18:10 +0200 Align contributing doc with oslo's policy''')  # noqa
        self.assertEqual(expected_result, "".join(results))
        results = luc.generate_output(self._data, output_format='yaml',
                                      ignore_all=True)
        expected_result = textwrap.dedent("""\
            ---
              - repo: openstack/castellan
                branch: victoria
                commits:
                  range:
                    - 3.2.0
                    - 3a3a738
                  logs:
                    - '* 3a3a738 2020-06-26 13:51:12 +0200 Bump vault version'
                error: false
                not_yet_released: false
                msg: ''
              - repo: openstack/oslo.cache
                branch: victoria
                commits:
                  range:
                    - 2.5.0
                    - f3f006c
                  logs:
                    - "* a5ff884 2020-05-04 18:18:10 +0200 Align contributing doc\\
                      \\ with oslo's policy"
                error: false
                not_yet_released: false
                msg: ''
        """)  # noqa
        self.assertEqual(expected_result, results)
