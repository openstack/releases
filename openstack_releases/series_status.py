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
"""Class for reading series status information.
"""

import collections.abc
import os.path

from openstack_releases import yamlutils


class Phase(object):

    def __init__(self, data):
        self._data = data
        self.status = data['status']
        self.date = data['date']


class Series(object):

    def __init__(self, data):
        self._data = data
        self.name = data['name']
        self.status = data['status']
        self.initial_release = data['initial-release']

    @property
    def next_phase(self):
        try:
            return Phase(self._data['next-phase'])
        except KeyError:
            return None

    @property
    def release_id(self):
        return str(self._data.get('release-id', self.name))

    @property
    def eol_date(self):
        return self._data.get('eol-date', None)

    @property
    def is_eol(self):
        return self.status == 'end of life'

    @property
    def is_em(self):
        return self.status == 'extended maintenance'

    @property
    def is_eom(self):
        return self.status == 'unmaintained'

    @property
    def is_maintained(self):
        return self.status == 'maintained' or self.status == 'development'


class SeriesStatus(collections.abc.Mapping):

    def __init__(self, raw_data):
        self._raw_data = raw_data
        self._data = self._organize_data(raw_data)
        # Ensure there is always an independent series.
        if 'independent' not in self._data:
            self._data['independent'] = Series({
                'name': 'independent',
                'status': 'development',
                'initial-release': None,
            })

    @classmethod
    def from_directory(cls, root_dir):
        raw_data = cls._load_series_status_data(root_dir)
        return cls(raw_data)

    @classmethod
    def default(cls):
        module_path = os.path.dirname(__file__)
        root_dir = os.path.dirname(module_path)
        return cls.from_directory(os.path.join(root_dir, 'data'))

    @staticmethod
    def _load_series_status_data(root_dir):
        filename = os.path.join(root_dir, 'series_status.yaml')
        with open(filename, 'r', encoding='utf-8') as f:
            return yamlutils.loads(f.read())

    @staticmethod
    def _organize_data(raw_data):
        organized = {
            s['name']: Series(s)
            for s in raw_data
        }
        return organized

    @property
    def names(self):
        for entry in self._raw_data:
            yield entry['name']

    # Mapping API

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def __getitem__(self, series):
        return self._data[series]


def get_stable_branch_id(series):
    """Retrieve the stable branch ID of the series.

    Returns the release-id if the series has such field, otherwise
    returns the series name. This is needed for the new stable branch
    naming style: stable/2023.1 (versus the old style: stable/zed).
    """
    series_status_data = SeriesStatus.default()
    return series_status_data[series].release_id


def get_full_branch_name(series):
    """Retrieve the full branch name for the series.

    Returns stable/<release-id> if the series is still maintained
    or returns unmaintained/<release-id> if the series already went
    to Unmaintained.
    """
    series_status_data = SeriesStatus.default()
    return '%s/%s' % (
        'unmaintained' if series_status_data[series].is_eom else 'stable',
        series_status_data[series].release_id)
