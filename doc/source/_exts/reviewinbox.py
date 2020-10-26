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

from docutils import nodes
from docutils.parsers import rst
from docutils import statemachine as sm
from urllib import parse as urllib_parse

from openstack_releases import series_status

QUERY_TEMPLATE = ('project:openstack/releases file:^deliverables/{}/.* '
                  'NOT label:Workflow-1')


# Leveraging a couple pieces from gerrit-dash-creator so we don't have to pull
# in the full project.
def escape(buff):
    """Because otherwise Firefox is a sad panda."""
    return buff.replace(',', '%2c').replace('-', '%2D')


class ReviewInbox(rst.Directive):
    """Directive for generating review inbox based on current series status."""

    has_content = True

    def run(self):
        url = 'https://review.opendev.org/#/dashboard/?'
        sections = []

        url += escape(urllib_parse.urlencode({
            'title': 'Releases Inbox',
            'foreach': 'is:open'})) + '&'

        # Add the series specific data based on its current status
        series_status_data = series_status.SeriesStatus.default()
        for series_name in series_status_data:
            series = series_status_data[series_name]
            if series.status not in ['development', 'maintained']:
                continue

            if series_name == 'independent':
                series_name = '_independent'
            sections.append(escape(urllib_parse.urlencode({
                series.name.title(): QUERY_TEMPLATE.format(series_name)})))

        # Now add our sections that never change
        sections.append(escape(urllib_parse.urlencode({
            'Other':
            r'project:openstack/releases NOT file:^deliverables/.*'})))

        sections.append(escape(urllib_parse.urlencode({
            'Jobs':
            r'project:openstack/project-config file:^roles/'
            r'copy-release-tools-scripts/files/release-tools/.*'})))

        sections.append(escape(urllib_parse.urlencode({
            'Tools':
            r'(( project:openstack/releases file:^tools/.* ) OR '
            r'project:openstack/release-test OR '
            r'( project:openstack/releases file:^openstack_releases/.* ) OR '
            r'project:openstack/reno)'})))

        sections.append(escape(urllib_parse.urlencode({
            'All Releases': 'is:open project:openstack/releases'})))

        url += '&'.join(sections)

        result = sm.ViewList()
        source = '<{}>'.format(__name__)

        result.append('`Gerrit Release Review Inbox <{}>`_'.format(
            url), source)

        node = nodes.section()
        node.document = self.state.document
        self.state.nested_parse(result, 0, node)
        return node.children


def setup(app):
    app.add_directive('reviewinbox', ReviewInbox)
    return {
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
