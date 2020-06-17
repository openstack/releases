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
import functools
import glob
import os
import os.path
import weakref

from openstack_governance import governance
import pbr.version

from openstack_releases import series_status
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
    # NOTE(dhellmann): We want EOL and EM tags to sort last. This assumes we
    # won't have more than 1000 major releases of anything, and I
    # surely hope that is a safe assumption.
    version_string = release['version']
    if version_string.endswith('-eol') or version_string.endswith('-em'):
        return _safe_semver('1000.0.0')
    return _safe_semver(version_string)


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
        self._active_teams = set()
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
        return os.path.basename(os.path.dirname(filename)).lstrip('_')

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
        d = Deliverable(team, series, deliverable, d_info)
        if d.allows_releases:
            self._active_teams.add(team)
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

    def get_active_teams(self):
        "Return the names of all teams which have releasable deliverables."
        return self._active_teams

    def get_deliverables(self, team, series):
        """Return a sequence of deliverable data for the team and series.

        Return tuples containing team, series, deliverable, and parsed
        deliverable file content.

        If the team or series is None, treat that value as a wildcard.

        """
        if team is None:
            if series is None:
                series = 'independent'
            filenames = self._by_series[series]
        else:
            filenames = self._by_team_and_series[(team, series)]
        for filename in filenames:
            yield Deliverable(
                team,
                self._series_from_filename(filename),
                self._deliverable_from_filename(filename),
                self._by_filename.get(filename, {}),
            )

    def get_deliverable_history(self, name):
        """Return info associated with a deliverable name.
        """
        for filename in self._by_deliverable_name.get(name, []):
            yield Deliverable(
                None,  # team will be taken from the data
                self._series_from_filename(filename),
                self._deliverable_from_filename(filename),
                self._by_filename.get(filename, {}),
            )


@functools.total_ordering
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

    @property
    def pypi_name(self):
        return self._data.get('pypi-name')

    @property
    def base_name(self):
        return self.name.rsplit('/')[-1]

    @property
    def tarball_base(self):
        return self._data.get('tarball-base')

    def __eq__(self, other):
        return self.name == other.name

    def __gt__(self, other):
        return self.name > other.name

    def __str__(self):
        return self.name


@functools.total_ordering
class ReleaseProject(object):

    def __init__(self, repo, hash, data, release=None):
        self._repo = repo
        self.repo = release.deliv.get_repo(repo)
        self.hash = hash
        self._data = data
        self.release = weakref.proxy(release)

    @property
    def tarball_base(self):
        if 'tarball-base' in self._data:
            return self._data['tarball-base']
        return self.repo.tarball_base

    def guess_sdist_name(self):
        return self.tarball_base or self.repo.base_name

    def __eq__(self, other):
        return self.repo == other.repo

    def __gt__(self, other):
        return self.repo > other.repo


class Release(object):

    def __init__(self, version, projects, data, deliv):
        self.version = version
        if deliv:
            self.deliv = weakref.proxy(deliv)
        else:
            self.deliv = deliv
        self._data = data
        self._projects = {
            p['repo']: ReleaseProject(p['repo'], p['hash'], p, self)
            for p in projects
        }

    @property
    def was_forced(self):
        return 'forced' in self._data.get('flags', set())

    @property
    def skipped_sig(self):
        return 'skipped-sig' in self._data.get('flags', set())

    @property
    def projects(self):
        return sorted(self._projects.values())

    def project(self, repo):
        if repo in self._projects:
            return self._projects[repo]
        return None

    @property
    def diff_start(self):
        return self._data.get('diff-start')

    @property
    def is_release_candidate(self):
        return 'rc' in self.version

    @property
    def is_pre_release_version(self):
        return (
            'rc' in self.version
            or 'a' in self.version
            or 'b' in self.version
        )

    @property
    def is_eol(self):
        return self.version.endswith('-eol')

    @property
    def eol_series(self):
        if self.is_eol:
            return self.version.rpartition('-')[0]
        return ''

    @property
    def is_em(self):
        return self.version.endswith('-em')

    @property
    def em_series(self):
        if self.is_em:
            return self.version.rpartition('-')[0]
        return ''

    def __eq__(self, other):
        return self.version == other.version


class Branch(object):

    def __init__(self, name, location, data, deliv):
        self.name = name
        self.location = location
        self.deliv = weakref.proxy(deliv)
        self._data = data

    def __eq__(self, other):
        return self.version == other.version

    @property
    def prefix(self):
        return self.name.split('/')[0]

    @property
    def series(self):
        return self.name.split('/')[1]

    def get_repo_map(self):
        "Return mapping between repo and hash."
        if isinstance(self.location, dict):
            return self.location
        release = self.deliv.get_release(self.location)
        return {
            p.repo.name: p.hash
            for p in release.projects
        }


@functools.total_ordering
class Deliverable(object):

    _gov_data = None
    _series_status_data = None

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
        for r in data.get('releases') or []:
            for p in r.get('projects') or []:
                repos.add(p.get('repo'))
        self._repos = {
            r: Repo(
                name=r,
                data=self._data.get('repository-settings', {}).get(r, {}),
                deliv=self,
            )
            for r in sorted(repos)
        }
        self._releases = [
            Release(
                version=r['version'],
                projects=r['projects'],
                data=r,
                deliv=self,
            )
            for r in self._data.get('releases') or []
        ]
        self._branches = [
            Branch(
                name=b['name'],
                location=b['location'],
                data=b,
                deliv=self,
            )
            for b in self._data.get('branches') or []
        ]

    @classmethod
    def read_file(cls, filename):
        with open(filename, 'r', encoding='utf-8') as f:
            data = yamlutils.loads(f.read())

        series_name = os.path.basename(
            os.path.dirname(filename)
        ).lstrip('_')
        deliverable_name = os.path.basename(filename)[:-5]  # strip .yaml

        return cls(
            team=None,  # extracted from the info automatically
            series=series_name,
            name=deliverable_name,
            data=data or {},  # if the file is empty yaml returns None
        )

    @property
    def launchpad_id(self):
        return self._data.get('launchpad')

    @property
    def storyboard_id(self):
        return self._data.get('storyboard')

    @property
    def repos(self):
        return sorted(self._repos.values())

    @property
    def known_repo_names(self):
        return set(self._data.get('repository-settings', {}).keys())

    def get_repo(self, name):
        return self._repos[name]

    @property
    def model(self):
        model = self._data.get('release-model', '')
        if self.is_independent and model != 'abandoned':
            return 'independent'
        return model

    @property
    def is_independent(self):
        return self.series == 'independent'

    @property
    def is_releasable(self):
        return self.model != 'untagged'

    @property
    def is_released(self):
        return len(self._data.get('releases') or []) > 0

    @property
    def is_cycle_based(self):
        return self.model.startswith('cycle-')

    @property
    def is_milestone_based(self):
        return self.model in ['cycle-with-milestones', 'cycle-with-rc']

    @property
    def is_branchless(self):
        # Tempest plugins do not branch.
        if self.type == 'tempest-plugin':
            return True
        if self.name == 'tempest':
            return True
        return False

    @property
    def type(self):
        if 'tempest-plugin' in self.name:
            return 'tempest-plugin'
        if self.model == 'cycle-trailing':
            return 'trailing'
        return self._data.get('type', 'other')

    @property
    def artifact_link_mode(self):
        return self._data.get('artifact-link-mode', 'tarball')

    @property
    def earliest_release(self):
        if not self.is_released:
            return ''
        return self.releases[0].version

    @property
    def latest_release(self):
        if not self.is_released:
            return ''
        return self.releases[-1].version

    @property
    def is_first_release(self):
        return len(self.releases) == 1

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
        return self._releases

    def get_release(self, version):
        for r in self.releases:
            if r.version == version:
                return r
        raise ValueError('Unknown version {}'.format(version))

    @property
    def branches(self):
        return self._branches

    def get_branch_location(self, name):
        branches = self._data.get('branches', [])
        for b in branches:
            if b['name'] == name:
                return b['location']
        return None

    @property
    def tags(self):
        if self._gov_data is None:
            Deliverable._gov_data = governance.Governance.from_remote_repo()
        try:
            team = self._gov_data.get_team(self.team)
            deliv = team.deliverables[self.name]
        except (KeyError, ValueError):
            # The deliverable is no longer listed under governance.
            return []
        return deliv.tags

    @property
    def filename(self):
        return os.path.join(self.series, self.name + '.yaml')

    @property
    def data(self):
        return copy.deepcopy(self._data)

    @property
    def stable_branch_type(self):
        branch_type = self._data.get('stable-branch-type', 'std')
        return None if branch_type == 'none' else branch_type

    @property
    def cycle_highlights(self):
        return self._data.get('cycle-highlights', [])

    @property
    def series_info(self):
        self.init_series_status_data()
        return self._series_status_data[self.series]

    @classmethod
    def init_series_status_data(cls, data=None):
        if cls._series_status_data is not None:
            return
        if data is None:
            data = series_status.SeriesStatus.default()
        cls._series_status_data = data

    @property
    def stable_status(self):
        status = self._data.get('stable-status')
        if status is None:
            if self.is_independent:
                status = 'development'
            else:
                status = self.series_info.status
        if self.model == 'abandoned':
            status = 'end of life'
        return status

    @property
    def allows_releases(self):
        return self.stable_status in ('development', 'maintained')

    def __eq__(self, other):
        return self.name == other.name

    def __gt__(self, other):
        return self.name > other.name

    def __str__(self):
        return self.name
