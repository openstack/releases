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

import collections
import glob
import itertools
import os.path

from docutils import nodes
from docutils.parsers import rst
from docutils.parsers.rst import directives
from docutils.statemachine import ViewList
import pbr.version
from sphinx.util.nodes import nested_parse_with_titles
import yaml

from openstack_releases import governance


def _list_table(add, headers, data, title='', columns=None):
    """Build a list-table directive.

    :param add: Function to add one row to output.
    :param headers: List of header values.
    :param data: Iterable of row data, yielding lists or tuples with rows.
    """
    add('.. list-table:: %s' % title)
    add('   :header-rows: 1')
    if columns:
        add('   :widths: %s' % (','.join(str(c) for c in columns)))
    add('')
    add('   - * %s' % headers[0])
    for h in headers[1:]:
        add('     * %s' % h)
    for row in data:
        add('   - * %s' % row[0])
        for r in row[1:]:
            lines = str(r).splitlines()
            if not lines:
                # empty string
                add('     * ')
            else:
                # potentially multi-line string
                add('     * %s' % lines[0])
                for l in lines[1:]:
                    add('       %s' % l)
    add('')


def _get_deliverable_type(deliverable_types, name):
    if (name.startswith('python-') and not name.endswith('client')):
        name = name[7:]
    if (name.startswith('python-') and name.endswith('client')):
        return 'type:library'
    if name in deliverable_types:
        return deliverable_types[name]
    no_dashes = name.replace('-', '_')
    if no_dashes in deliverable_types:
        return deliverable_types[no_dashes]
    return 'type:other'


def _version_sort_key(release):
    """Return a value we can compare for sorting.

    We can't just use SemanticVersion instances because some of the
    legacy tags don't comply with the parser. Use a tuple of the parts
    of the version string, converted to integers where possible to
    avoid weird alphabetical sorting of numbers.

    """
    key = []
    for p in str(release['version']).split('.'):
        try:
            key.append(int(p))
        except ValueError:
            key.append(p)
    return tuple(key)


def _collapse_deliverable_history(app, name, info):
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
        except:
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
                    app.info('[deliverables] ignoring %s %s' %
                             (name, r['version']))
                    continue
                releases.append(r)
                known_versions.add(r['version'])
    info['releases'] = list(reversed(releases))


_cached_deliverable_files = {}


def _get_deliverable_file_content(app, deliverable_name, filename):
    if filename in _cached_deliverable_files:
        return _cached_deliverable_files[filename]
    app.info('[deliverables] reading %s' % filename)
    with open(filename, 'r') as f:
        d_info = yaml.load(f.read())
        _collapse_deliverable_history(app, deliverable_name, d_info)
        _cached_deliverable_files[filename] = d_info
        return d_info


_all_teams = {}
_deliverable_files_by_team = {}


def _initialize_team_data(app):
    team_data = governance.get_team_data()
    for team in (governance.Team(n, i) for n, i in team_data.items()):
        _all_teams[team.name] = team
        _deliverable_files_by_team[team.name] = list(itertools.chain(
            *(glob.glob('deliverables/*/%s.yaml' % dn)
              for dn in team.deliverables)
        ))


class DeliverableDirectiveBase(rst.Directive):

    option_spec = {
        'series': directives.unchanged,
        'team': directives.unchanged,
    }

    _TYPE_ORDER = [
        'type:service',
        'type:library',
        'type:other',
        'release:cycle-trailing',
    ]

    def run(self):
        env = self.state.document.settings.env
        app = env.app

        # The series value is optional for some directives.
        series = self.options.get('series')

        # If the user specifies a team, track only the deliverables
        # for that team.
        self.team_name = self.options.get('team')
        self.team_deliverables = []

        if self.team_name:
            deliverables = _all_teams[self.team_name].deliverables
            self.team_deliverables = list(deliverables.keys())
        else:
            deliverables = {}
            for team in _all_teams.values():
                deliverables.update(team.deliverables)

        # Pre-populate the mapping between deliverable names and their
        # types.
        deliverable_types = {}
        for dn, di in deliverables.items():
            for tag in di.tags:
                # Treat the cycle-trailing model as a separate "type"
                # so those items are all grouped together in the
                # output.
                if tag == 'release:cycle-trailing':
                    deliverable_types[dn] = tag
                    break
                if tag.startswith('type:'):
                    deliverable_types[dn] = tag
                    break

        result = ViewList()

        # Assemble all of the deliverable data to be displayed and
        # build the RST representation.

        if self.team_name:
            deliverables = []
            for filename in sorted(self._get_deliverables_files(series)):
                deliverable_name = os.path.basename(filename)[:-5]  # strip .yaml
                d_info = _get_deliverable_file_content(
                    app, deliverable_name, filename,
                )
                deliverables.append(
                    (deliverable_name,
                     filename,
                     d_info))
            self._add_deliverables(
                None,
                deliverables,
                series,
                app,
                result,
            )
        else:
            deliverables = collections.defaultdict(list)

            for filename in sorted(self._get_deliverables_files(series)):
                deliverable_name = os.path.basename(filename)[:-5]  # strip .yaml
                deliverable_type = _get_deliverable_type(
                    deliverable_types,
                    deliverable_name,
                )
                d_info = _get_deliverable_file_content(
                    app, deliverable_name, filename,
                )
                deliverables[deliverable_type].append(
                    (deliverable_name,
                     filename,
                     d_info))

            for type_tag in self._TYPE_ORDER:
                self._add_deliverables(
                    type_tag,
                    deliverables[type_tag],
                    series,
                    app,
                    result,
                )

        # NOTE(dhellmann): Useful for debugging.
        # print('\n'.join(result))

        node = nodes.section()
        node.document = self.state.document
        nested_parse_with_titles(self.state, result, node)
        return node.children

    _TYPE_TITLE = {
        'type:service': 'Service Projects',
        'type:library': 'Library Projects',
        'type:other': 'Other Projects',
        'release:cycle-trailing': 'Projects Trailing the Release Cycle',
    }

    @staticmethod
    def _artifact_link(mode, version, project):
        if mode == 'tarball':
            # Link the version number to the tarball for downloading.
            repo_base = project['repo'].rsplit('/')[-1]
            if 'tarball-base' in project:
                base = project['tarball-base']
            else:
                base = repo_base
            return '`{v} <{s}/{r}/{n}-{v}.tar.gz>`__'.format(
                s='https://tarballs.openstack.org',
                v=version,
                r=repo_base,
                n=base,
            )
        elif mode == 'none':
            # Only show the version number.
            return version
        raise ValueError('Unrecognized artifact-link-mode: %r' % mode)

    def _add_deliverables(self, type_tag, deliverables, series, app, result):
        source_name = '<' + __name__ + '>'

        if not deliverables:
            # There are no deliverables of this type, and that's OK.
            return

        result.append('', source_name)
        if type_tag is not None:
            title = self._TYPE_TITLE.get(type_tag, 'Unknown Projects')
            result.append('-' * len(title), source_name)
            result.append(title, source_name)
            result.append('-' * len(title), source_name)
            result.append('', source_name)

        # Build a table of the first and most recent versions of each
        # deliverable.
        if not self.team_name:
            most_recent = []
            for deliverable_name, filename, deliverable_info in deliverables:
                earliest_version = deliverable_info.get('releases', {})[0].get(
                    'version', 'unreleased')
                recent_version = deliverable_info.get('releases', {})[-1].get(
                    'version', 'unreleased')
                ref = ':ref:`%s-%s`' % (series, deliverable_name)
                release_notes = deliverable_info.get('release-notes')
                if not release_notes:
                    notes_link = ''
                elif isinstance(release_notes, dict):
                    notes_link = '\n'.join(
                        '| `%s release notes <%s>`__' % (n.split('/')[-1], v)
                        for n, v in sorted(release_notes.items())
                    )
                else:
                    notes_link = '`release notes <%s>`__' % release_notes
                most_recent.append((ref, earliest_version, recent_version, notes_link))
            _list_table(
                lambda t: result.append(t, source_name),
                ['Deliverable', 'Earliest Version', 'Most Recent Version', 'Notes'],
                most_recent,
                title='Release Summary',
            )

        # Show the detailed history of the deliverables within the series.

        for deliverable_name, filename, deliverable_info in deliverables:

            # These closures need to be redefined in each iteration of
            # the loop because they use the filename.
            def _add(text):
                result.append(text, filename)

            def _title(text, underline):
                text = str(text)  # version numbers might be seen as floats
                if self.team_name:
                    _add('.. _team-%s-%s:' % (series, text))
                else:
                    _add('.. _%s-%s:' % (series, text))
                _add('')
                _add(text)
                _add(underline * len(text))
                _add('')

            _title(deliverable_name, '=')

            app.info('[deliverables] rendering %s (%s)' %
                     (deliverable_name, series))

            release_notes = deliverable_info.get('release-notes')
            if not release_notes:
                notes_link = None
            elif isinstance(release_notes, dict):
                notes_link = ' | '.join(
                    '`%s <%s>`__' % (n.split('/')[-1], v)
                    for n, v in sorted(release_notes.items())
                )
            else:
                notes_link = '`%s <%s>`__' % (deliverable_name, release_notes)
            if notes_link:
                _add('')
                _add('Release Notes: %s' % notes_link)
                _add('')
            link_mode = deliverable_info.get('artifact-link-mode', 'tarball')
            _list_table(
                _add,
                ['Version', 'Repo', 'Git Commit'],
                ((self._artifact_link(link_mode, r['version'], p),
                  p['repo'], p['hash'])
                 for r in reversed(deliverable_info.get('releases', []))
                 for p in r.get('projects', [])),
                columns=[10, 40, 50],
            )


class DeliverableDirective(DeliverableDirectiveBase):

    def _get_deliverables_files(self, series):
        if self.team_name:
            # Only show the deliverables associated with the team
            # specified.
            return itertools.chain(
                *(glob.glob('deliverables/%s/%s.yaml' % (series, dn))
                  for dn in self.team_deliverables)
            )
        else:
            # Show all of the deliverables for all teams producing
            # anything in the series.
            return glob.glob('deliverables/%s/*.yaml' % series)

    def run(self):
        # Require a series value.
        series = self.options.get('series')
        if not series:
            error = self.state_machine.reporter.error(
                'No series set for deliverable directive',
                nodes.literal_block(self.block_text, self.block_text),
                line=self.lineno)
            return [error]

        return super(DeliverableDirective, self).run()


class IndependentDeliverablesDirective(DeliverableDirectiveBase):

    def _get_deliverables_files(self, series):
        return glob.glob('deliverables/_independent/*.yaml')


class TeamDirective(rst.Directive):

    option_spec = {
        'series': directives.unchanged,
        'name': directives.unchanged,
    }

    def run(self):
        # If the user specifies a team, track only the deliverables
        # for that team.
        self.team_name = self.options.get('name')
        if not self.team_name:
            error = self.state_machine.reporter.error(
                'No team name in team directive',
                nodes.literal_block(self.block_text, self.block_text),
                line=self.lineno)
            return [error]

        if self.team_name not in _all_teams:
            error = self.state_machine.reporter.error(
                'Team %r not found in governance data' % self.team_name,
                nodes.literal_block(self.block_text, self.block_text),
                line=self.lineno)
            return [error]
        team = _all_teams[self.team_name]
        self.team_deliverables = list(team.deliverables.keys())

        deliverable_files = _deliverable_files_by_team[self.team_name]
        all_series = reversed(sorted(set(
            os.path.basename(os.path.dirname(df))
            for df in deliverable_files
        )))

        result = ViewList()

        def _add(text):
            result.append(text, '<team tag>')

        for series in all_series:
            series_title = series.lstrip('_').title()
            _add(series_title)
            _add('=' * len(series_title))
            _add('')
            _add('.. deliverable::')
            _add('   :series: %s' % series)
            _add('   :team: %s' % self.team_name)
            _add('')

        # NOTE(dhellmann): Useful for debugging.
        # print('\n'.join(result))

        node = nodes.section()
        node.document = self.state.document
        nested_parse_with_titles(self.state, result, node)
        return node.children


def _generate_team_pages(app):
    teams_with_deliverables = []
    for team_name in sorted(_all_teams.keys()):
        if _deliverable_files_by_team.get(team_name):
            teams_with_deliverables.append(team_name)
    for team_name in teams_with_deliverables:
        app.info('[team page] %s' % team_name)
        slug = team_name.lower().replace('-', '_').replace(' ', '_')
        base_file = slug + '.rst'
        with open(os.path.join('doc/source/teams', base_file), 'w') as f:
            f.write('=' * (len(team_name) + 2))
            f.write('\n')
            f.write(' %s\n' % team_name.title())
            f.write('=' * (len(team_name) + 2))
            f.write('\n\n')
            f.write('.. team::\n')
            f.write('   :name: %s\n' % team_name)
    return


def setup(app):
    _initialize_team_data(app)
    app.add_directive('deliverable', DeliverableDirective)
    app.add_directive('independent-deliverables',
                      IndependentDeliverablesDirective)
    app.add_directive('team', TeamDirective)
    _generate_team_pages(app)
