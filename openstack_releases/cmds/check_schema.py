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

"""Verify that all data files match the schema."""

import argparse
import datetime
import glob
import logging
import os
import os.path
import pkgutil
import sys

import jsonschema
import jsonschema.validators

from openstack_releases import yamlutils

LOG = logging.getLogger('')

_SERIES_SCHEMA = yamlutils.loads(
    pkgutil.get_data('openstack_releases',
                     'series_status_schema.yaml').decode('utf-8')
)

_DELIVERABLE_SCHEMA = yamlutils.loads(
    pkgutil.get_data('openstack_releases', 'schema.yaml').decode('utf-8')
)

_LIAISONS_SCHEMA = yamlutils.loads(
    pkgutil.get_data('openstack_releases',
                     'liaisons_schema.yaml').decode('utf-8')
)


def is_date(validator, instance):
    return (
        isinstance(instance, datetime.date) and
        not isinstance(instance, datetime.datetime)
    )


def make_validator_with_date(schema_data):
    draft4_validator = jsonschema.Draft4Validator
    date_type_checker = draft4_validator.TYPE_CHECKER.redefine("date", is_date)
    return jsonschema.validators.extend(
        validator=draft4_validator,
        type_checker=date_type_checker
    )(schema=schema_data)


def validate_one_file(filename, schema_data, debug):
    LOG.info('Checking %s', filename)
    validator = make_validator_with_date(schema_data)
    with open(filename, 'r', encoding='utf-8') as f:
        info = yamlutils.loads(f.read())
    for error in validator.iter_errors(info):
        LOG.error(error)
        yield '{}: {}'.format(filename, error)
        if debug:
            raise RuntimeError(error)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--debug',
        default=False,
        action='store_true',
        help='throw exception on error',
    )
    parser.add_argument(
        'input',
        nargs='*',
        help=('YAML files to validate, defaults to '
              'files changed in the latest commit'),
    )
    args = parser.parse_args()

    # Set up logging, including making some loggers quiet.
    logging.basicConfig(
        format='%(levelname)7s: %(message)s',
        stream=sys.stdout,
        level=logging.DEBUG,
    )
    logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)

    errors = []

    if not args.input:
        errors.extend(
            validate_one_file('data/series_status.yaml',
                              _SERIES_SCHEMA, args.debug)
        )

        errors.extend(
            validate_one_file('data/release_liaisons.yaml',
                              _LIAISONS_SCHEMA, args.debug)
        )

    filenames = args.input or sorted(glob.glob('deliverables/*/*.yaml'))

    for filename in filenames:
        if not os.path.isfile(filename):
            LOG.info("%s was deleted, skipping.", filename)
            continue
        errors.extend(
            validate_one_file(filename, _DELIVERABLE_SCHEMA, args.debug)
        )

    print('\n\n%s errors found' % len(errors))
    for e in errors:
        print(e)

    return 1 if errors else 0
