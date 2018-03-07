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
"""Class for manipulating all of the deliverable data.
"""

import collections
import copy
import glob
import os
import os.path
import weakref

import pbr.version

from openstack_releases import governance
from openstack_releases import yamlutils


def _safe_semver(v):
    """Get a SemanticVersion that closely represents the version string.

    We can't always get a SemanticVersion instance because some of the
    legacy tags don't comply with the parser. This method corrects
    some of the more common mistakes in formatting to make it more
    likely we can construct a SemanticVersion, even if the results
    don't quite match the input.

    """
    v = str(v)
    # Remove "v" prefixes.
    v = v.lstrip('v')
    # Remove any stray "." at the start or end, after the other
    # cleanups.
    v = v.strip('.')
    # If we have a version with 4 positions that are all integers,
    # drop the fourth.
    parts = v.split('.')
    if len(parts) > 3:
        try:
            int(parts[3])
        except ValueError:
            pass
        else:
            parts = parts[:3]
        v = '.'.join(parts)
    return pbr.version.SemanticVersion.from_pip_string(v)


def _version_sort_key(release):
    """Return a value we can compare for sorting.
    """
    return _safe_semver(release['version'])


def _collapse_deliverable_history(name, info):
    """Collapse pre-releases into their final release.

    Edit the info dictionary in place.

    """
    sorted_releases = sorted(
        info.get('releases', []),
        key=_version_sort_key,
    )
    # Collapse pre-releases into their final release.
    releases = []
    known_versions = set()
    for r in reversed(sorted_releases):
        try:
            parsed_vers = pbr.version.SemanticVersion.from_pip_string(
                str(r['version']))
            vers_tuple = parsed_vers.version_tuple()
        except Exception:
            # If we can't parse the version, it must be some sort
            # of made up legacy tag. Ignore the parse error
            # and include the value in our output.
            releases.append(r)
        else:
            if len(vers_tuple) != 3:
                # This is not a normal release, so assume it
                # is a pre-release.
                final = parsed_vers.brief_string()
                if final in known_versions:
                    continue
                releases.append(r)
                known_versions.add(r['version'])
    info['releases'] = list(reversed(releases))


class Deliverables(object):

    def __init__(self, root_dir, collapse_history=True):
        self._root_dir = root_dir
        self._collapse_history = collapse_history

        # Map team names to a list of all of their deliverables.
        self._team_deliverables = collections.defaultdict(set)
        # Map team names to a set of all the series in which they
        # produced anything.
        self._team_series = collections.defaultdict(set)
        # Map team, series, and deliverable names to a list of the
        # deliverable files.
        self._by_team_and_series = collections.defaultdict(list)
        self._by_series = collections.defaultdict(list)
        self._by_deliverable_name = collections.defaultdict(list)
        # Map filenames to parsed content.
        self._by_filename = {}

        self._load_deliverable_files(root_dir)

    def _load_deliverable_files(self, root_dir):
        deliverable_files = glob.glob(os.path.join(root_dir, '*/*.yaml'))
        for filename in sorted(deliverable_files):
            series = self._series_from_filename(filename)
            deliverable = self._deliverable_from_filename(filename)
            with open(filename, 'r', encoding='utf-8') as f:
                d_info = yamlutils.loads(f.read())
                if self._collapse_history:
                    _collapse_deliverable_history(deliverable, d_info)
            team = d_info['team']
            self._add_deliverable_file(
                filename, series, team, deliverable, d_info,
            )

    @staticmethod
    def _series_from_filename(filename):
        return os.path.basename(os.path.dirname(filename))

    @staticmethod
    def _deliverable_from_filename(filename):
        return os.path.splitext(os.path.basename(filename))[0]

    def _add_deliverable_file(self, filename, series, team, deliverable,
                              d_info):
        self._by_filename[filename] = d_info
        self._by_team_and_series[(team, series)].append(filename)
        self._by_series[series].append(filename)
        self._team_deliverables[team].add(deliverable)
        self._team_series[team].add(series)
        deliv = self._deliverable_from_filename(filename)
        self._by_deliverable_name[deliv].append(filename)

    def get_team_deliverables(self, team):
        "Returns a list of deliverable names produced by the team."
        return list(sorted(self._team_deliverables[team]))

    def get_team_series(self, team):
        "Return the names of the series in which the team produced anything."
        return self._team_series[team]

    def get_teams(self):
        "Return all of the names of all of the teams seen."
        return list(self._team_series.keys())

    def get_deliverables(self, team, series):
        """Return a sequence of deliverable data for the team and series.

        Return tuples containing team, series, deliverable, and parsed
        deliverable file content.

        If the team or series is None, treat that value as a wildcard.

        """
        if team is None:
            if series is None:
                series = '_independent'
            filenames = self._by_series[series]
        else:
            filenames = self._by_team_and_series[(team, series)]
        for filename in filenames:
            yield (
                team,
                self._series_from_filename(filename),
                self._deliverable_from_filename(filename),
                self._by_filename.get(filename, {}),
            )

    def get_deliverable_history(self, name):
        """Return info associated with a deliverable name.
        """
        for filename in self._by_deliverable_name.get(name, []):
            yield (
                None,
                self._series_from_filename(filename),
                self._deliverable_from_filename(filename),
                self._by_filename.get(filename, {}),
            )


class Repo(object):

    def __init__(self, name, data, deliv):
        self.name = name
        self._data = data
        self.deliv = weakref.proxy(deliv)

    @property
    def flags(self):
        return self._data.get('flags', [])

    @property
    def is_retired(self):
        return 'retired' in self.flags

    @property
    def no_artifact_build_job(self):
        return 'no-artifact-build-job' in self.flags


class ReleaseProject(object):

    def __init__(self, repo, hash, release):
        self._repo = repo
        self.repo = release.deliv.get_repo(repo)
        self.hash = hash
        self.release = weakref.proxy(release)


class Release(object):

    def __init__(self, version, projects, deliv):
        self.version = version
        self.deliv = weakref.proxy(deliv)
        self._projects = {
            p['repo']: ReleaseProject(release=self, **p)
            for p in projects
        }

    @property
    def projects(self):
        return sorted(self._projects.values(), key=lambda p: p.repo.name)


class Deliverable(object):

    _governance_data = None

    def __init__(self, team, series, name, data):
        self.team = team
        if self.team is None:
            self.team = data.get('team')
        self.series = series
        self.name = name
        self._data = data
        repos = set(self._data.get('repository-settings', {}).keys())
        # NOTE(dhellmann): We do this next bit for legacy deliverable
        # files without the repository-settings sections. We should be
        # able to remove this after the T series is opened because at
        # that point all actively validated deliverable files will
        # have this data.
        for r in data.get('releases', []):
            for p in r.get('projects', []):
                repos.add(p.get('repo'))
        self._repos = {
            r: Repo(
                name=r,
                data=self._data.get('repository-settings', {}).get(r, {}),
                deliv=self,
            )
            for r in sorted(repos)
        }

    @property
    def launchpad_id(self):
        return self._data.get('launchpad')

    @property
    def storyboard_id(self):
        sb_id = self._data.get('storyboard')
        return int(sb_id) if sb_id else None

    @property
    def repos(self):
        return sorted(self._repos.values(), key=lambda r: r.name)

    @property
    def known_repo_names(self):
        return set(self._repos.keys())

    def get_repo(self, name):
        return self._repos[name]

    @property
    def model(self):
        if self.is_independent:
            return 'independent'
        return self._data.get('release-model', '')

    @property
    def is_independent(self):
        return self.series == 'independent'

    @property
    def is_releasable(self):
        return self.model != 'untagged'

    @property
    def is_cycle_based(self):
        return self.model.startswith('cycle-')

    @property
    def type(self):
        return self._data.get('type', 'other')

    @property
    def artifact_link_mode(self):
        return self._data.get('artifact-link-mode', 'tarball')

    @property
    def latest_release(self):
        rel = (self.releases or [{}])[-1]
        return rel.get('version')

    @property
    def release_notes(self):
        return self._data.get('release-notes', '')

    @property
    def release_type(self):
        return self._data.get('release-type', None)

    @property
    def include_pypi_link(self):
        return self._data.get('include-pypi-link', False)

    @property
    def versions(self):
        return [
            r['version']
            for r in self.releases
        ]

    @property
    def releases(self):
        return [
            Release(deliv=self, **r)
            for r in self._data.get('releases', [])
        ]

    def get_branch_location(self, name):
        branches = self._data.get('branches', [])
        for b in branches:
            if b['name'] == name:
                return b['location']
        return None

    @property
    def tags(self):
        if self._governance_data is None:
            Deliverable._governance_data = governance.get_team_data()
        return governance.get_tags_for_deliverable(
            self._governance_data, self.team, self.name)

    @property
    def filename(self):
        return os.path.join(self.series, self.name + '.yaml')

    @property
    def data(self):
        return copy.deepcopy(self._data)
