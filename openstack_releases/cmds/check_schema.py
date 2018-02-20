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

"""Verify that all deliverable files match the schema.

"""

from __future__ import print_function

import argparse
import glob
import logging
import os
import os.path
import pkgutil
import sys

import jsonschema

from openstack_releases import yamlutils

_SCHEMA = yamlutils.loads(
    pkgutil.get_data('openstack_releases', 'schema.yaml').decode('utf-8')
)


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
    log = logging.getLogger('')

    filenames = args.input or sorted(glob.glob('deliverables/*/*.yaml'))

    errors = []
    warnings = []

    for filename in filenames:
        log.info('Checking %s', filename)
        if not os.path.isfile(filename):
            log.info("File was deleted, skipping.")
            continue
        with open(filename, 'r', encoding='utf-8') as f:
            deliverable_info = yamlutils.loads(f.read())

        def mk_warning(msg):
            log.warning(msg)
            warnings.append('{}: {}'.format(filename, msg))

        def mk_error(msg):
            log.error(msg)
            errors.append('{}: {}'.format(filename, msg))
            if args.debug:
                raise RuntimeError(msg)

        validator = jsonschema.Draft4Validator(_SCHEMA)
        for error in validator.iter_errors(deliverable_info):
            mk_error(str(error))

    print('\n\n%s warnings found' % len(warnings))
    for w in warnings:
        print(w)

    print('\n\n%s errors found' % len(errors))
    for e in errors:
        print(e)

    return 1 if errors else 0
