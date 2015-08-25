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

import glob
import os.path

from docutils import nodes
from docutils.parsers import rst
from docutils.parsers.rst import directives
from docutils.statemachine import ViewList
from sphinx.util.nodes import nested_parse_with_titles

import yaml


def _list_table(add, headers, data):
    """Build a list-table directive.

    :param add: Function to add one row to output.
    :param headers: List of header values.
    :param data: Iterable of row data, yielding lists or tuples with rows.
    """
    add('.. list-table::')
    add('   :header-rows: 1')
    add('')
    add('   - * %s' % headers[0])
    for h in headers[1:]:
        add('     * %s' % h)
    for row in data:
        add('   - * %s' % row[0])
        for r in row[1:]:
            add('     * %s' % r)
    add('')


class DeliverableDirective(rst.Directive):

    option_spec = {
        'series': directives.unchanged,
    }

    def run(self):
        env = self.state.document.settings.env
        app = env.app

        series = self.options.get('series')
        if not series:
            error = self.state_machine.reporter.error(
                'No series set for deliverable directive',
                nodes.literal_block(self.block_text, self.block_text),
                line=self.lineno)
            return [error]

        result = ViewList()

        for filename in sorted(glob.glob('deliverables/%s/*.yaml' % series)):
            app.info('[deliverables] reading %s' % filename)
            with open(filename, 'r') as f:
                deliverable_info = yaml.load(f.read())
            deliverable_name = os.path.basename(filename)[:-5]  # strip .yaml ext

            # These closures need to be redefined in each iteration of
            # the loop because they use the filename.
            def _add(text):
                result.append(text, filename)

            def _title(text, underline):
                text = str(text)  # version numbers might be converted to floats
                _add(text)
                _add(underline * len(text))
                _add('')

            def _rubric(text):
                text = str(text)  # version numbers might be converted to floats
                _add('.. rubric:: %s' % text)
                _add('')

            _title(deliverable_name, '=')

            for release in deliverable_info.get('releases', []):
                app.info('[deliverables] release %s' % release['version'])
                _rubric(release['version'])
                _list_table(
                    _add, ['Repo', 'SHA'],
                    ((p['repo'], p['hash']) for p in release.get('projects', []))
                )

        node = nodes.section()
        node.document = self.state.document
        nested_parse_with_titles(self.state, result, node)
        return node.children


def setup(app):
    app.add_directive('deliverable', DeliverableDirective)
