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

"""Do dirty things with wikis.
"""
from __future__ import print_function

import itertools

import mwclient


def get_page_section(page_content, section):
    "Return iterable of lines making up a section of a wiki page."
    section_start = u'== {} =='.format(section).lower()
    lines = page_content.splitlines()
    lines = itertools.dropwhile(
        lambda x: x.lower() != section_start,
        lines,
    )
    next(lines)  # skip the section heading
    lines = itertools.takewhile(
        lambda x: not x.startswith('== '),
        lines,
    )
    return lines


def get_wiki_table(page_content, section):
    """Return iterable of dicts making up rows of a wiki table.

    Assumes there is only one table per section.

    """
    lines = get_page_section(page_content, section)
    lines = itertools.dropwhile(
        lambda x: x != '{| class="wikitable"',
        lines,
    )
    headings = []
    for line in lines:
        if line == '|-':
            continue
        elif line.startswith('!'):
            headings = [h.strip() for h in line.lstrip('!').split('!!')]
        elif line in ['}', '|}']:
            # end of table
            break
        elif line.startswith('|'):
            items = [i.strip() for i in line.lstrip('|').split('||')]
            row = {
                h: i
                for (h, i) in zip(headings, items)
            }
            yield row


def get_wiki_page(name):
    "Return the text of a wiki page as a string."
    site = mwclient.Site('wiki.openstack.org')
    page = site.Pages[name]
    return page.text()


def get_liaison_data():
    """Return information about all liaisons.

    Map the team name to a dict containing Project, Liaison, and 'IRC
    Handle' keys.

    """
    text = get_wiki_page('CrossProjectLiaisons')
    table = get_wiki_table(text, 'Release management')
    return {
        row['Project'].lower(): row
        for row in table
    }


def main():
    d = get_liaison_data()
    for team, data in sorted(d.items()):
        print('{:20}: {} ({})'.format(team, data['Liaison'], data['IRC Handle']))
