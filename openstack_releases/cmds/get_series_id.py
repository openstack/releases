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

import argparse
import os

from openstack_releases import series_status

BASE_PATH = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = f'{BASE_PATH}/../../data'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'series',
        help='the name of the series, such as "wallaby" or "xena"',
    )
    args = parser.parse_args()

    series = series_status.SeriesStatus.from_directory(ROOT_DIR)
    for release in series:
        if release == args.series:
            print(series.get(release).release_id)
