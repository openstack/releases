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

from collections import defaultdict
import itertools
import operator
import os.path

from docutils import nodes
from docutils.parsers import rst
from docutils.parsers.rst import directives
from docutils.statemachine import ViewList
from openstack_governance import governance
from sphinx.util import logging
from sphinx.util.nodes import nested_parse_with_titles

from openstack_releases import deliverable
from openstack_releases import links
from openstack_releases import series_status
from openstack_releases._redirections import generate_constraints_redirections

LOG = logging.getLogger(__name__)

_GOV_DATA = governance.Governance.from_remote_repo()
_PHASE_DOC_URL = 'https://docs.openstack.org/project-team-guide/stable-branches.html#maintenance-phases'  # noqa


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


def _get_category(deliv):
    model = deliv.model
    if model == 'cycle-trailing':
        return 'trailing'
    if model == 'abandoned':
        return 'abandoned'
    return deliv.type


_deliverables = None
_series_status_data = None


def _initialize_deliverable_data():
    global _deliverables
    global _series_status_data

    LOG.info('Loading deliverable data...')

    _series_status_data = series_status.SeriesStatus.default()
    deliverable.Deliverable.init_series_status_data(_series_status_data)
    _deliverables = deliverable.Deliverables('deliverables')


class DeliverableDirectiveBase(rst.Directive):

    option_spec = {
        'series': directives.unchanged,
        'team': directives.unchanged,
    }

    _CATEGORY_ORDER = [
        'service',
        'client-library',
        'library',
        'horizon-plugin',
        'other',
        'trailing',
        'tempest-plugin',
        'abandoned',
    ]

    def run(self):
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
                key=operator.attrgetter('series')
            )
            for s, d in d_source:
                self._add_deliverables(
                    None,
                    d,
                    s,
                    result,
                )
        else:
            # Add table of contents for all deliverables
            result.append('.. contents:: **Deliverables**', '<toc>')
            result.append('   :local:', '<toc>')
            result.append('   :backlinks: none', '<toc>')
            result.append('   :depth: 1', '<toc>')
            result.append('', '<toc>')

            # Only the deliverables for the given series are
            # shown. They are categorized by type, which we need to
            # extract from the data.
            raw_deliverables = [
                (_get_category(deliv), deliv)
                for deliv in _deliverables.get_deliverables(
                    self.team_name,
                    series,
                )
            ]
            grouped = itertools.groupby(
                sorted(raw_deliverables),
                key=operator.itemgetter(0),  # the category
            )
            # Convert the grouping iterators to a dictionary mapping
            # type to the list of tuples with deliverable name and
            # parsed deliverable info that _add_deliverables() needs.
            by_category = {}
            for deliverable_category, deliverables in grouped:
                by_category[deliverable_category] = [
                    d[1]
                    for d in deliverables
                ]
            for category in self._CATEGORY_ORDER:
                if category not in by_category:
                    LOG.info('[deliverables] No %r for %s', category,
                             (self.team_name, series))
                    continue
                self._add_deliverables(
                    category,
                    by_category[category],
                    series,
                    result,
                )

        # NOTE(dhellmann): Useful for debugging.
        # print('\n'.join(result))

        node = nodes.section()
        node.document = self.state.document
        nested_parse_with_titles(self.state, result, node)
        return node.children

    _TYPE_TITLE = {
        'service': 'Service Projects',
        'horizon-plugin': 'Horizon Plugins',
        'library': 'Library Projects',
        'client-library': 'Service Client Projects',
        'other': 'Other Projects',
        'trailing': 'Deployment and Packaging Tools',
        'tempest-plugin': 'Tempest Plugins',
        'abandoned': 'End-of-life deliverables',
    }

    def _add_deliverables(self, type_tag, deliverables, series, result):
        source_name = '<' + __name__ + '>'

        # expand any generators passed in and filter out deliverables
        # with no releases
        deliverables = [
            d
            for d in deliverables
            if d.releases
        ]
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
            for deliv in deliverables:
                recent_version = earliest_version = deliv.earliest_release
                # Determine the most recent release that is not an EOL
                # tag.
                has_non_eol_em = False
                for r in reversed(deliv.releases):
                    if not (r.is_eol or r.is_em):
                        recent_version = r.version
                        has_non_eol_em = True
                        break
                # Even though we have this check later for specific
                # deliverables, we need to do this at a couple points to make
                # sure we don't start adding something that doesn't actually
                # end up having any individual release data to show
                if not has_non_eol_em:
                    continue
                ref = ':ref:`%s-%s`' % (series, deliv.name)
                release_notes = deliv.release_notes
                if not release_notes:
                    notes_link = ''
                elif isinstance(release_notes, dict):
                    notes_link = '\n'.join(
                        '| `%s release notes <%s>`__' % (n.split('/')[-1], v)
                        for n, v in sorted(release_notes.items())
                    )
                else:
                    notes_link = '`release notes <%s>`__' % release_notes
                stable_status = '`{} <{}>`__'.format(
                    deliv.stable_status.title(),
                    _PHASE_DOC_URL,
                )
                most_recent.append(
                    (ref,
                     earliest_version,
                     recent_version,
                     stable_status,
                     notes_link)
                )
            _list_table(
                lambda t: result.append(t, source_name),
                ['Deliverable', 'Earliest Version',
                 'Most Recent Version', 'Stable Status', 'Notes'],
                most_recent,
                title='Release Summary',
            )

        # Show the detailed history of the deliverables within the series.

        for deliv in deliverables:
            has_non_eol_em = False
            for r in deliv.releases:
                if not (r.is_eol or r.is_em):
                    has_non_eol_em = True
                    break
            if not has_non_eol_em:
                continue

            # These closures need to be redefined in each iteration of
            # the loop because they use the deliverable name.
            def _add(text):
                result.append(text, '%s/%s' % (series, deliv.name))

            def _title(text, underline):
                text = str(text)  # version numbers might be seen as floats
                if self.team_name:
                    _add('.. _team-%s-%s:' % (series, text))
                    if deliv.model == 'abandoned':
                        text = '%s (EOL)' % text
                else:
                    _add('.. _%s-%s:' % (series, text))
                _add('')
                _add(text)
                _add(underline * len(text))
                _add('')

            _title(deliv.name, '=')

            LOG.debug('[deliverables] rendering %s (%s)',
                      deliv.name, series)

            release_notes = deliv.release_notes
            if not release_notes:
                notes_link = None
            elif isinstance(release_notes, dict):
                notes_link = ' | '.join(
                    '`%s <%s>`__' % (n.split('/')[-1], v)
                    for n, v in sorted(release_notes.items())
                )
            else:
                notes_link = '`%s <%s>`__' % (deliv.name, release_notes)
            if notes_link:
                _add('')
                _add('Release Notes: %s' % notes_link)
                _add('')
            headers = ['Version', 'Signature', 'Repo', 'Git Commit']
            data = ((links.artifact_link(r.version, p, deliv),
                     links.artifact_signature_link(r.version,
                                                   'pgp', p,
                                                   deliv)
                     if ((series and series[0] >= 'o')
                         or (deliv.is_independent and not r.skipped_sig))
                     else '',
                     p.repo, p.hash)
                    for r in reversed(deliv.releases)
                    for p in r.projects
                    if not (r.is_eol or r.is_em))
            columns = [10, 10, 40, 50]
            _list_table(
                _add,
                headers=headers,
                data=data,
                columns=columns,
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


def _generate_team_pages():
    teams_with_deliverables = list(sorted(_deliverables.get_teams()))
    for team_name in teams_with_deliverables:
        LOG.info('[team page] %s', team_name)
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


class HighlightsDirective(rst.Directive):
    """Directive to pull series highlights into docs output."""

    option_spec = {
        'series': directives.unchanged,
    }

    def _get_deliverable_highlights(self, series):
        """Collects the highlights for the series.

        :param series: The series to extract highlights from.
        :returns: The available highlights for the series.
        """
        series_highlights = defaultdict(list)
        series_deliverables = _deliverables.get_deliverables(None, series)
        for deliv in series_deliverables:
            highlights = deliv.cycle_highlights
            for item in highlights:
                series_highlights[deliv.team].append(item)

        return series_highlights

    def run(self):
        # Get the series we are reporting on
        series = self.options.get('series')
        if not series:
            raise self.error('series value must be set to a valid cycle name.')

        LOG.debug('[highlights] gathering highlights for {}'.format(
                  series))

        result = ViewList()
        series_highlights = self._get_deliverable_highlights(series)
        source_name = '<{}>'.format(__name__)

        for team in sorted(series_highlights.keys(), key=lambda x: x.lower()):
            LOG.debug('[highlights] rendering %s highlights for %s',
                      team.title(), series)

            tdata = None
            try:
                tdata = GOV_DATA.get_team(team)
            except:
                # Team may have moved out of governance
                pass

            title = team.title()
            if tdata and tdata.service:
                title = "{} - {}".format(title, tdata.service)
            result.append(title, source_name)
            result.append('-' * len(title), source_name)
            if tdata and tdata.mission:
                result.append(tdata.mission, source_name)
                result.append('', source_name)
            result.append('**Notes:**', source_name)
            result.append('', source_name)
            for item in series_highlights[team]:
                result.append('- {}'.format(item), source_name)
            result.append('', source_name)

        # NOTE(dhellmann): Useful for debugging.
        # print('\n'.join(result))

        node = nodes.section()
        node.document = self.state.document
        nested_parse_with_titles(self.state, result, node)
        return node.children


def build_finished(app, exception):
    def write_out_data(app, template, params, *path_parts):
        output_full_name = os.path.normpath(os.path.join(app.builder.outdir,
                                                         *path_parts))
        with open(output_full_name, "w") as f:
            f.write(app.builder.templates.render(template, params))
        LOG.info('Wrote %s to %s' % (template, output_full_name))

    if exception is not None:
        return

    future_releases = [series.name
                       for series in _series_status_data.values()
                       if series.status == 'future']
    params = dict(
        redirections=generate_constraints_redirections(_deliverables,
                                                       future_releases)
    )

    write_out_data(app, 'htaccess', params, '.htaccess')
    write_out_data(app, 'redirect-tests', params, '..', 'redirect-tests.txt')


def setup(app):
    _initialize_deliverable_data()
    app.add_directive('deliverable', DeliverableDirective)
    app.add_directive('independent-deliverables',
                      IndependentDeliverablesDirective)
    app.add_directive('team', TeamDirective)
    app.add_directive('serieshighlights', HighlightsDirective)
    app.connect('build-finished', build_finished)
    _generate_team_pages()
    return {
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
