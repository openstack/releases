#!/usr/bin/env python
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
"""Read an email message and send it through localhost.

This is a separate script from the release notes email generator
because it might be used for other things and it might not be used
when notes are being send from a developer's system.

"""

from __future__ import print_function

import argparse
import email
import smtplib


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', default='lists.openstack.org',
                        help=('the SMTP server Valid forms are: server, '
                              'server:port, user:pw@server or '
                              'user:pw@server:port.  Default: %(default)s'))
    parser.add_argument('-v', dest='verbose',
                        action='store_true', default=False,
                        help='turn on extra debugging output')
    parser.add_argument('infile', help='the file containing the email')
    args = parser.parse_args()

    user = None
    pw = None
    server = args.server

    if '@' in server:
        creds, _, server = args.server.partition('@')
        user, _, pw = creds.partition(':')

    with open(args.infile, 'r') as f:
        msg = email.message_from_file(f)

    tolist = [address.strip() for address in msg['to'].split(",")]

    server = smtplib.SMTP(server)
    if args.verbose:
        server.set_debuglevel(True)
    try:
        if pw:
            server.starttls()
            server.login(user, pw)
        server.sendmail(msg['from'], tolist, msg.as_string().encode('utf-8'))
    finally:
        server.quit()
