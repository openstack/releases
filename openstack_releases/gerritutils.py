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
import requests


GERRIT_URL = 'https://review.opendev.org/changes/?q='


def gerrit_query(*query):
    query_url = GERRIT_URL + '+'.join(query)
    response = requests.get(query_url)
    if (response.status_code // 100) != 2:
        raise RuntimeError(
            'Bad HTTP response from gerrit %s: %s' %
            (query_url, response.status_code)
        )
    elif response.content[:4] == b")]}'":
        content = response.content[5:].decode('utf-8')
        return json.loads(content)
    else:
        print('could not parse response from %s' % query_url)
        print(repr(response.content))
        raise RuntimeError('failed to parse gerrit response')
