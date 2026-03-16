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

import datetime
import os
import re
import yaml
from docutils import nodes
from docutils.parsers.rst import Directive
from sphinx.util import logging
from sphinx.errors import SphinxError


LOG = logging.getLogger(__name__)

STATIC_DIR = "doc/source/static"
DATA_SERIES_STATUS = "data/series_status.yaml"


class SigningKeyError(SphinxError):
    pass


class SigningKeysDirective(Directive):
    def _parse_data_series(self):
        try:
            with open(DATA_SERIES_STATUS) as f:
                data = yaml.safe_load(f)
                return data
        except Exception as e:
            raise SigningKeyError(f"Error reading YAML: {e}")

    def _validate_release(self, rel):
        sk = rel.get('signing-key')

        for k in ['key', 'start', 'end']:
            val = sk.get(k, None)
            if val is None:
                raise SigningKeyError(
                    f"Release {rel['name']} signing-key does not have "
                    f"a '{k}' key")

            if k == 'key':
                txt_file = os.path.join(STATIC_DIR, "0x" + str(val) + ".txt")
                if not os.path.exists(txt_file):
                    raise SigningKeyError(
                        f"Release {rel['name']} signing-key file {txt_file} "
                        "does not exist")
            elif k == 'start' and not isinstance(val, datetime.date):
                raise SigningKeyError(
                        f"Release {rel['name']} signing-key start '{val}' is "
                        "not a valid YYYY-mm-dd date")
            elif k == 'end' and (
                val != "present" and not isinstance(val, datetime.date)
            ):
                raise SigningKeyError(
                    f"Release {rel['name']} signing-key end '{val}' is "
                    "not 'present' or a valid YYYY-mm-dd date")

    def _get_fingerprint_from_keyfile(self, sk):
        txt_file = os.path.join(STATIC_DIR, "0x" + str(sk["key"]) + ".txt")
        try:
            with open(txt_file, 'r') as f:
                content = f.read()
                m = re.search(r"Key fingerprint = ([0-9A-F ]+)", content)
                if m:
                    # Convert to lowercase to match the filenames in
                    # the static dir
                    fp = str(m.group(1).replace(" ", "")).lower()
                    return fp
                else:
                    raise SigningKeyError(
                        f"Could not find key 'Key fingerprint' regex pattern "
                        f"in {txt_file} content")
        except Exception as e:
            raise SigningKeyError(
                f"Could not read fingerprint from {txt_file}: {e}")

    def _render_date(self, dt):
        if isinstance(dt, datetime.date):
            return dt.strftime("%Y-%m-%d")
        return str(dt)

    def run(self):
        LOG.info(f"Loading signing keys from {DATA_SERIES_STATUS}...")

        releases = self._parse_data_series()

        table = nodes.table()
        tgroup = nodes.tgroup(cols=3)
        table += tgroup

        for _ in range(3):
            tgroup += nodes.colspec(colwidth=1)

        thead = nodes.thead()
        tgroup += thead
        header_row = nodes.row()
        for h in ["Validity", "Series", "Cycle Key"]:
            entry = nodes.entry()
            entry += nodes.paragraph(text=h)
            header_row += entry
        thead += header_row

        tbody = nodes.tbody()
        tgroup += tbody

        seen_files = set()

        for rel in reversed(releases):
            sk = rel.get("signing-key", None)
            if sk is None:
                continue

            self._validate_release(rel)

            fp = self._get_fingerprint_from_keyfile(sk)

            filename = "0x" + str(sk["key"]) + ".txt"
            seen_files.add(filename)

            if fp != sk['key']:
                txt_file = os.path.join(STATIC_DIR, filename)
                raise SigningKeyError(
                    f"Fingerprint '{fp}' in file {txt_file} does not "
                    f"match filename {sk['key']} part in filename {txt_file} "
                    "without the 0x prefix")

            row = nodes.row()

            entry = nodes.entry()
            start_dt = self._render_date(sk['start'])
            end_dt = self._render_date(sk['end'])
            entry += nodes.paragraph(text=f"{start_dt} - {end_dt}")
            row += entry

            entry = nodes.entry()
            if rel.get('release-id', None) is not None:
                rel_name = (
                    f"{rel['release-id']}/{rel['name'].capitalize()}")
            else:
                rel_name = rel['name'].capitalize()
            entry += nodes.paragraph(text=rel_name)
            row += entry

            entry = nodes.entry()
            link = nodes.reference(
                text=f"key 0x{fp}", refuri=f"_static/0x{fp}.txt")
            paragraph = nodes.paragraph()
            paragraph += link
            entry += paragraph
            row += entry

            tbody += row

        # Find static files matching pattern and see if it
        # was ever seen when rendering
        keyfile_pattern = re.compile(r'^0x.*\.txt$')
        matching_files = [
            f for f in os.listdir(STATIC_DIR) if keyfile_pattern.match(f)]
        for m in matching_files:
            if m not in seen_files:
                raise SigningKeyError(
                    f"File {m} in {STATIC_DIR} was not seen when rendering "
                    "the signing keys documentation. It's either orphaned or "
                    f"not included correctly in {DATA_SERIES_STATUS}")

        return [table]


def setup(app):
    app.add_directive("signingkeys", SigningKeysDirective)
    return {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
