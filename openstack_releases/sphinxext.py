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
import os.path

from docutils import nodes
from docutils.parsers import rst
from docutils.parsers.rst import directives
from docutils.statemachine import ViewList
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
            add('     * %s' % r)
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


class DeliverableDirectiveBase(rst.Directive):

    option_spec = {
        'series': directives.unchanged,
    }

    _TYPE_ORDER = [
        'type:service',
        'type:library',
        'type:other',
    ]

    def run(self):
        env = self.state.document.settings.env
        app = env.app

        team_data = governance.get_team_data()

        # The series value is optional for some directives.
        series = self.options.get('series')

        deliverable_types = {}
        for team in (governance.Team(n, i) for n, i in team_data.items()):
            for dn, di in team.deliverables.items():
                for tag in di.tags:
                    if tag.startswith('type:'):
                        deliverable_types[dn] = tag

        result = ViewList()

        # Read all of the deliverable data for the series.

        deliverables = collections.defaultdict(list)

        for filename in sorted(self._get_deliverables_files(series)):
            app.info('[deliverables] reading %s' % filename)
            deliverable_name = os.path.basename(filename)[:-5]  # strip .yaml
            deliverable_type = _get_deliverable_type(
                deliverable_types,
                deliverable_name,
            )
            with open(filename, 'r') as f:
                deliverables[deliverable_type].append(
                    (deliverable_name,
                     filename,
                     yaml.load(f.read())))

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
    }

    @staticmethod
    def _tarball_link(version, repo):
        return '`{v} <{s}/{n}/{n}-{v}.tar.gz>`__'.format(
            s='http://tarballs.openstack.org',
            v=version,
            n=repo.rsplit('/')[-1],
        )

    def _add_deliverables(self, type_tag, deliverables, series, app, result):
        source_name = '<' + __name__ + '>'

        if not deliverables:
            # There are no deliverables of this type, and that's OK.
            return

        result.append('', source_name)
        title = self._TYPE_TITLE.get(type_tag, 'Unknown Projects')
        result.append('-' * len(title), source_name)
        result.append(title, source_name)
        result.append('-' * len(title), source_name)
        result.append('', source_name)

        # Build a table of the first and most recent versions of each
        # deliverable.

        most_recent = []
        for deliverable_name, filename, deliverable_info in deliverables:
            earliest_version = deliverable_info.get('releases', {})[0].get(
                'version', 'unreleased')
            recent_version = deliverable_info.get('releases', {})[-1].get(
                'version', 'unreleased')
            ref = ':ref:`%s-%s`' % (series, deliverable_name)
            most_recent.append((ref, earliest_version, recent_version))
        _list_table(
            lambda t: result.append(t, source_name),
            ['Deliverable', 'Earliest Version', 'Most Recent Version'],
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
                _add('.. _%s-%s:' % (series, text))
                _add('')
                _add(text)
                _add(underline * len(text))
                _add('')

            _title(deliverable_name, '=')

            app.info('[deliverables] %s' % deliverable_name)

            _list_table(
                _add,
                ['Version', 'Repo', 'Git Commit'],
                ((self._tarball_link(r['version'], p['repo']),
                  p['repo'], p['hash'])
                 for r in reversed(deliverable_info.get('releases', []))
                 for p in r.get('projects', [])),
                columns=[10, 40, 50],
            )


class DeliverableDirective(DeliverableDirectiveBase):

    def _get_deliverables_files(self, series):
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


def setup(app):
    app.add_directive('deliverable', DeliverableDirective)
    app.add_directive('independent-deliverables',
                      IndependentDeliverablesDirective)
