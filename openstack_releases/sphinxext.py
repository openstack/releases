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

import itertools
import operator
import os.path

from docutils import nodes
from docutils.parsers import rst
from docutils.parsers.rst import directives
from docutils.statemachine import ViewList
from sphinx.util.nodes import nested_parse_with_titles

from openstack_releases import deliverable
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


def _get_deliverable_type(name, data):
    if (name.startswith('python-') and name.endswith('client')):
        return 'type:library'
    for tag in data.get('tags', []):
        if tag == 'release:cycle-trailing':
            return tag
        if tag.startswith('type:'):
            return tag
    return _DEFAULT_TYPE


_DEFAULT_TYPE = 'type:other'
_deliverables = None
_all_teams = {}
_all_deliverable_types = {}


def _initialize_team_data(app):
    global _deliverables
    global _all_teams

    _deliverables = deliverable.Deliverables('deliverables')
    team_data = governance.get_team_data()
    for tn, td in team_data.items():
        _all_teams[tn] = td
        for dn, dd in td['deliverables'].items():
            _all_deliverable_types[dn] = _get_deliverable_type(dn, dd)


class DeliverableDirectiveBase(rst.Directive):

    option_spec = {
        'series': directives.unchanged,
        'team': directives.unchanged,
    }

    _TYPE_ORDER = [
        'type:service',
        'type:library',
        'type:horizon-plugin',
        'type:other',
        'release:cycle-trailing',
    ]

    def run(self):
        env = self.state.document.settings.env
        app = env.app

        # The series value is optional for some directives. If it is
        # present but an empty string, convert to None so the
        # Deliverables class will treat it like a wildcard.
        series = self.options.get('series') or None

        # If the user specifies a team, track only the deliverables
        # for that team.
        self.team_name = self.options.get('team') or None

        result = ViewList()

        # Assemble all of the deliverable data to be displayed and
        # build the RST representation.

        # get_deliverables() -> (team, series, deliverable, info)

        if self.team_name:
            # All deliverables are shown, in alphabetical order. They
            # are organized by series but not type.
            d_source = itertools.groupby(
                sorted(_deliverables.get_deliverables(self.team_name, series)),
                key=operator.itemgetter(1)  # the series
            )
            for s, d in d_source:
                self._add_deliverables(
                    None,
                    ((i[2], i[3]) for i in d),  # only name and info
                    s,
                    app,
                    result,
                )
        else:
            # Only the deliverables for the given series are
            # shown. They are organized by type. The type is only
            # available from the governance data, so we have to add it
            # to the raw data before sorting and grouping.
            raw_deliverables = (
                (_all_deliverable_types.get(d[2], _DEFAULT_TYPE), d[2], d[3])
                for d in _deliverables.get_deliverables(
                    self.team_name,
                    series,
                )
            )
            raw_deliverables = list(raw_deliverables)
            grouped = itertools.groupby(
                sorted(raw_deliverables),
                key=operator.itemgetter(0),  # the deliverable type
            )
            # Convert the grouping iterators to a dictionary mapping
            # type to the list of tuples with deliverable name and
            # parsed deliverable info that _add_deliverables() needs.
            by_type = {}
            for deliverable_type, deliverables in grouped:
                by_type[deliverable_type] = [
                    (d[1], d[2])
                    for d in deliverables
                ]
            for type_tag in self._TYPE_ORDER:
                if type_tag not in by_type:
                    app.info('No %r for %s' % (type_tag, (self.team_name, series)))
                    continue
                self._add_deliverables(
                    type_tag,
                    by_type[type_tag],
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
        'type:horizon-plugin': 'Horizon Plugins',
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

        deliverables = list(deliverables)  # expand any generators passed in
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
            for deliverable_name, deliverable_info in deliverables:
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
                most_recent.append(
                    (ref, earliest_version, recent_version, notes_link)
                )
            _list_table(
                lambda t: result.append(t, source_name),
                ['Deliverable', 'Earliest Version',
                 'Most Recent Version', 'Notes'],
                most_recent,
                title='Release Summary',
            )

        # Show the detailed history of the deliverables within the series.

        for deliverable_name, deliverable_info in deliverables:

            # These closures need to be redefined in each iteration of
            # the loop because they use the deliverable name.
            def _add(text):
                result.append(text, '%s/%s' % (series, deliverable_name))

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
    pass


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

        self.team_deliverables = _deliverables.get_team_deliverables(
            self.team_name
        )

        all_series = reversed(sorted(
            _deliverables.get_team_series(self.team_name)
        ))

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
    teams_with_deliverables = list(sorted(_deliverables.get_teams()))
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
