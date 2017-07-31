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
import re

import six
import yaml
import yamlordereddictloader


_LIKE_A_NUMBER = re.compile('^[0-9]+.[0-9]+$')


def _has_newline(data):
    if "\n" in data or "\r" in data:
        return True
    return False


class PrettySafeDumper(yaml.dumper.SafeDumper):
    """Yaml dumper that tries to not alter original formats (to much)."""

    BINARY_ENCODING = 'utf8'

    def represent_ordereddict(self, data):
        values = []
        node = yaml.nodes.MappingNode(
            'tag:yaml.org,2002:map', values, flow_style=None)
        if self.alias_key is not None:
            self.represented_objects[self.alias_key] = node
        for key, value in data.items():
            key_item = self.represent_data(key)
            value_item = self.represent_data(value)
            values.append((key_item, value_item))
        return node

    def represent_bool(self, data):
        if data:
            value = 'yes'
        else:
            value = 'no'
        return self.represent_scalar('tag:yaml.org,2002:bool', value)

    def choose_scalar_style(self):
        # Avoid messing up dict keys...
        if self.states[-1] == self.expect_block_mapping_simple_value:
            self.event.style = 'plain'
        return super(PrettySafeDumper, self).choose_scalar_style()\
            if self.event.style != 'plain' else ("'" if ' ' in
                                                 self.event.value else None)

    def represent_string(self, data):
        if isinstance(data, six.binary_type):
            data = data.decode(self.BINARY_ENCODING)
        style = "plain"
        if _has_newline(data):
            style = "|"
        elif _LIKE_A_NUMBER.match(data):
            style = '"'
        return yaml.representer.ScalarNode('tag:yaml.org,2002:str',
                                           data, style=style)

    def represent_undefined(self, data):
        if isinstance(data, collections.OrderedDict):
            return self.represent_odict(data)
        else:
            return super(PrettySafeDumper, self).represent_undefined(data)


# NOTE(harlowja): at some point this may not be needed...
# See: http://pyyaml.org/ticket/29
PrettySafeDumper.add_representer(collections.OrderedDict,
                                 PrettySafeDumper.represent_ordereddict)
PrettySafeDumper.add_representer(None,
                                 PrettySafeDumper.represent_undefined)

# NOTE(dhellmann): The representer functions in the base class are
# specified by class.method-name so we have to re-register the
# representer for bool if we want to override it.
PrettySafeDumper.add_representer(bool,
                                 PrettySafeDumper.represent_bool)


# Ensure we use our own routine here, because the style that comes by
# default is sort of wonky and messes up the values....
for str_type in [six.binary_type, six.text_type]:
    PrettySafeDumper.add_representer(str_type,
                                     PrettySafeDumper.represent_string)


def dumps(obj):
    """Dump a python object -> blob and apply our pretty styling."""
    buff = six.StringIO()
    yaml.dump_all([obj], buff,
                  explicit_start=True,
                  indent=2,
                  default_flow_style=False,
                  line_break="\n",
                  Dumper=PrettySafeDumper,
                  allow_unicode=True)
    return buff.getvalue()


def loads(blob):
    """Load a yaml blob and retain key ordering."""
    # This does use load, which is unsafe, but should be ok
    # for what we are loading here in this program; we should
    # be able to fix that in the future (if it matters).
    return yaml.load(blob, Loader=yamlordereddictloader.Loader)
