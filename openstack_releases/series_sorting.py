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
_series_data = [
    ["austin", "bexar", "cactus", "diablo", "essex", "folsom", "grizzly",
     "havana", "icehouse", "juno", "kilo", "liberty", "mitaka", "newton",
     "ocata", "pike", "queens", "rocky", "stein", "train", "ussuri",
     "victoria", "wallaby", "xena", "yoga", "zed"],
    # ["antelope", bobcat, etc etc etc],`
]


def keyfunc(series_name):
    assert series_name.isascii()

    # NOTE(tonyb): Create a private copy to avoid mutating input variable
    _series_name = series_name.lower()
    # This for/else statement looks for a series_name in series_data.  If it
    # is found stop looking (via break), because we have all the information
    # we need.  If the series name isn't found, i.e a run through the entire
    # series_data list-of-lists, the 'else' clause will be executed to do our
    # best to deduce the sort key from there.
    for series_nr, series_names in enumerate(_series_data):
        if _series_name in series_names:
            series_idx = series_names.index(_series_name)
            break
    else:
        if _series_name[0].isalpha():
            series_nr += 1
            series_idx = ord(_series_name[0]) - ord("a")
        elif _series_name[0].isdigit():
            (year, release) = map(int, _series_name.split("."))
            # This arithmetic comes from the fact that we started using
            # year.release naming scheme, after we completed a full list
            # of the alphabet.
            # This happened with the 2023.1 release.  To date it's two
            # releases per year.  If that changes this code will need to
            # be updated.
            # Releases "austin" -> "zed" are 0 -> 25 so 2023.1 is the 26th
            # OpenStack release
            (series_nr, series_idx) = \
                divmod(26 + ((year - 2023) * 2 + (release - 1)), 26)
        else:
            assert False
    # TODO(tonyb): Do we want to switch this to aa_austin, ba_2023.1 to force
    # a stable sort order
    return series_nr * 26 + series_idx
