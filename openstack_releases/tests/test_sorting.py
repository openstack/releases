# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
from unittest import mock

from oslotest import base

from openstack_releases import series_sorting


class TestSeries_Sorting(base.BaseTestCase):
    FAKE_SERIES_DATA = [
        series_sorting._series_data[0],
        ["antelope", "bobcat", "camel", "duck", "elephant", "fox", "gorilla",
         "hamster", "ibex", "jellyfish", "kudu", "lion", "meerkat", "narwhal",
         "otter", "pony", "quail", "raccoon", "salmon", "termite", "uakari",
         "viperfish", "whale", "xerus", "yak", "zebra"]
    ]

    def test_assert_nonascii(self):
        self.assertRaises(AssertionError, series_sorting.keyfunc, "ハロー")

    def test_assert_nonaplphanumeric(self):
        self.assertRaises(AssertionError, series_sorting.keyfunc, "__austin")

    def test_simple(self):
        test_series_list = ["antelope", "victoria", "2023.1", "zed",
                            "c-release-not-cactus"]
        sorted_series_list = ["victoria", "zed", "antelope", "2023.1",
                              "c-release-not-cactus"]
        self.assertEqual(sorted(test_series_list, key=series_sorting.keyfunc),
                         sorted_series_list)

    def test_simple_with_case(self):
        test_series_list = ["Antelope", "victoria", "2023.1", "zed",
                            "C-release-not-cactus"]
        sorted_series_list = ["victoria", "zed", "Antelope", "2023.1",
                              "C-release-not-cactus"]
        self.assertEqual(sorted(test_series_list, key=series_sorting.keyfunc),
                         sorted_series_list)

    @mock.patch.object(series_sorting, "_series_data", FAKE_SERIES_DATA)
    def test_with_series_2(self):
        test_series_list = ["antelope", "austin", "aardvark"]
        sorted_series_list = ["austin", "antelope", "aardvark"]
        self.assertEqual(sorted(test_series_list, key=series_sorting.keyfunc),
                         sorted_series_list)

    @mock.patch.object(series_sorting, "_series_data", FAKE_SERIES_DATA)
    def test_with_series_2_rollover(self):
        test_series_list = ["antelope", "austin", "zebra", "yak", "aardvark"]
        sorted_series_list = ["austin", "antelope", "yak", "zebra", "aardvark"]
        self.assertEqual(sorted(test_series_list, key=series_sorting.keyfunc),
                         sorted_series_list)

    @mock.patch.object(series_sorting, "_series_data", FAKE_SERIES_DATA)
    def test_with_series_2_mixed_styles(self):
        test_series_list = ["elephant", "2023.1", "duck", "2024.2",
                            "aardvark", "2024.1"]
        sorted_series_list = ["2023.1", "2024.1", "duck", "2024.2",
                              "elephant", "aardvark"]
        self.assertEqual(sorted(test_series_list, key=series_sorting.keyfunc),
                         sorted_series_list)
