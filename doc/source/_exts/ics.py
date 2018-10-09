import datetime
import json
import os
import os.path

from docutils.io import FileOutput
from docutils import nodes
from docutils.parsers import rst
import icalendar
from sphinx.util import logging
import yaml

LOG = logging.getLogger(__name__)


class PendingICS(nodes.Element):

    def __init__(self, data_source, series_name, data):
        super(PendingICS, self).__init__()
        self._data_source = data_source
        self._series_name = series_name
        self._data = data


class ICS(rst.Directive):

    option_spec = {
        'source': rst.directives.unchanged,
        'name': rst.directives.unchanged,
    }
    has_content = False

    def _load_data(self, env, data_source):
        rel_filename, filename = env.relfn2path(data_source)
        if data_source.endswith('.yaml'):
            with open(filename, 'r') as f:
                return yaml.load(f)
        elif data_source.endswith('.json'):
            with open(filename, 'r') as f:
                return json.load(f)
        else:
            raise NotImplementedError('cannot load file type of %s' %
                                      data_source)

    def run(self):
        env = self.state.document.settings.env

        try:
            data_source = self.options['source']
        except KeyError:
            error = self.state_machine.reporter.error(
                'No source set for ics directive',
                nodes.literal_block(self.block_text, self.block_text),
                line=self.lineno)
            return [error]

        try:
            series_name = self.options['name']
        except KeyError:
            error = self.state_machine.reporter.error(
                'No name set for ics directive',
                nodes.literal_block(self.block_text, self.block_text),
                line=self.lineno)
            return [error]

        data = self._load_data(env, data_source)

        node = PendingICS(data_source, series_name, data)
        node.document = self.state.document
        return [node]


_global_calendar = icalendar.Calendar()
_global_calendar.add('prodid', '-//releases.openstack.org//EN')
_global_calendar.add('X-WR-CALNAME', 'OpenStack Release Schedule')


def _format_description(node):
    "Given a node, get its text and remove line breaks in paragraphs."
    text = node.astext()
    parts = text.split('\n\n')
    return '\n\n'.join(p.replace('\n', ' ') for p in parts)


def doctree_resolved(app, doctree, docname):
    builder = app.builder

    for node in doctree.traverse(PendingICS):

        series_name = node._series_name
        data = node._data

        LOG.info('building {} calendar'.format(series_name))

        cal = icalendar.Calendar()
        cal.add('prodid', '-//releases.openstack.org//EN')
        cal.add('X-WR-CALNAME', '{} schedule'.format(series_name))

        for week in data['cycle']:
            if not week.get('name'):
                continue

            event = icalendar.Event()

            summary = []
            for item in week.get('x-project', []):
                try:
                    # Look up the cross-reference name to get the
                    # section, then get the title from the first child
                    # node.
                    title = doctree.ids[item].children[0].astext()
                except Exception as e:
                    # NOTE(dhellmann): Catching "Exception" is a bit
                    # ugly, but given the complexity of the expression
                    # above there are a bunch of ways things might
                    # fail.
                    LOG.info('could not get title for {}: {}'.format(item, e))
                    title = item
                summary.append(title)
            if summary:
                summary_text = ' (' + '; '.join(summary) + ')'
            else:
                summary_text = ''
            event.add(
                'summary',
                '{} {}{}'.format(series_name.title(),
                                 week['name'],
                                 summary_text),
            )

            start = datetime.datetime.strptime(week['start'], '%Y-%m-%d')
            event.add('dtstart', icalendar.vDate(start.date()))

            # NOTE(dhellmann): ical assumes a time of midnight, so in
            # order to have the event span the final day of the week
            # we have to add an extra day.
            raw_end = datetime.datetime.strptime(week['end'], '%Y-%m-%d')
            end = raw_end + datetime.timedelta(days=1)
            event.add('dtend', icalendar.vDate(end.date()))

            # Look up the cross-reference name to get the
            # section, then add the full description to the
            # text.
            description = [
                _format_description(doctree.ids[item])
                for item in week.get('x-project', [])
            ]
            if description:
                event.add('description', '\n\n'.join(description))

            cal.add_component(event)
            _global_calendar.add_component(event)

        output_full_name = os.path.join(
            builder.outdir,
            docname + '.ics',
        )
        output_dir_name = os.path.dirname(output_full_name)
        if not os.path.exists(output_dir_name):
            os.makedirs(output_dir_name)
        destination = FileOutput(
            destination_path=output_full_name,
            encoding='utf-8',
        )
        LOG.info('generating {}'.format(output_full_name))
        destination.write(cal.to_ical())

        # Remove the node that the writer won't understand.
        node.parent.replace(node, [])


def build_finished(app, exception):
    if exception is not None:
        return
    builder = app.builder
    output_full_name = os.path.join(
        builder.outdir,
        'schedule.ics',
    )
    output_dir_name = os.path.dirname(output_full_name)
    if not os.path.exists(output_dir_name):
        os.makedirs(output_dir_name)
    destination = FileOutput(
        destination_path=output_full_name,
        encoding='utf-8',
    )
    LOG.info('generating {}'.format(output_full_name))
    destination.write(_global_calendar.to_ical())


def setup(app):
    LOG.info('initializing ICS extension')
    app.add_directive('ics', ICS)
    app.connect('doctree-resolved', doctree_resolved)
    app.connect('build-finished', build_finished)
