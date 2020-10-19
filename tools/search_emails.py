#!/usr/bin/python3
#
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

import argparse
import datetime
from dateutil.relativedelta import relativedelta
import re
import sys
import textwrap
from urllib.parse import urlparse

from bs4 import BeautifulSoup
import requests


MINIMAL_DATE = datetime.datetime.strptime("2018-11-1", "%Y-%m-%d")
BASE_URL = "http://lists.openstack.org/pipermail/openstack-discuss"
DEFAULT_SEARCHING_PATTERN = '.?\[release\].*'  # noqa


def get(url):
    """Request a given url."""
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error with {url} server returned code {response.status_code}")
        return None
    return BeautifulSoup(response.content, features="html.parser")


def get_author(email):
    """Retrieve the author of an email."""
    email = get(email)
    if not email:
        return None
    return email.find_all('b')[0].string


def is_sent_by(author, authors):
    """Check if the email have been sent by one of the authors in the list.

    if authors is empty true will be returned by default.
    """
    if not authors:
        return True
    if author.lower() in [auth.lower() for auth in authors]:
        return True
    return False


def search(month_url, topic, authors):
    """Search for matching emails."""
    exit = 0
    results = []
    soup = get(month_url)
    if not soup:
        exit = 1
        return results, exit
    for tag in soup.find_all('a', href=True):
        href = tag['href']
        email_subject = tag.string.replace('\n', '')
        # Only collect legit urls (ML links are at the 000000.html)
        if not re.match("[0-9]{6}.html", href):
            continue
        url = f'{month_url}/{href}'
        if not re.search(topic, email_subject):
            continue
        author = get_author(url)
        if not author:
            exit = 1
            continue
        if not is_sent_by(author, authors):
            continue
        results.append(
            {
                'url': url,
                'subject': email_subject,
                'author': author
            }
        )
    return results, exit


def display(results):
    """Display our results."""
    default = 'No results found...'
    count = 0
    final = []
    for year in results:
        for month in results[year]:
            if not results[year][month]['emails']:
                continue
            final.append(f'{year}-{month}:')
            for email in results[year][month]['emails']:
                final.append('\t- {subject} - {author}\n\t{url}'.format(
                    subject=email['subject'],
                    author=email['author'],
                    url=email['url']))
                count += 1
    if final and count > 0:
        print(f'{count} result(s) have been found')
        print('\n'.join(final))
    else:
        print(default)


def mailing_list_url(string):
    error_msg = f'{string} is not a valid url'
    try:
        result = urlparse(string)
        if not all([result.scheme, result.netloc, result.path]):
            raise argparse.ArgumentTypeError(error_msg)
        return string if not string.endswith("/") else string[:-1]
    except Exception:
        raise argparse.ArgumentTypeError(error_msg)


def main():
    """Main entrypoint."""
    epilog = textwrap.dedent("""
    Topic:\n
        Various topic can be used to looking for specific topics, by example
        topic can be set to `.?\[oslo\].*` to search all emails related to
        oslo.

        Useful topics:
        - `.?\[release\] Release countdown.*` (looking for release countdown)
        - `.?\[all\].*` (looking for email related to all)
        - `.?\[requirements\].*` (looking for email related to requirements)
        - `.?\[release\].*FFE.*` (looking for email related to release FFE)

    Usages:\n
        To looking for emails related to release and filtered between 2 dates:
        ```
        $ {cmd} --starting-date 2020-04-01 --ending-date 2020-4-1
        ```
        To looking for emails related to release and filtered by authors:
        ```
        $ {cmd} --authors "Herve Beraud" "Sean McGinnis
        ```
        To looking for emails related to release between 2 dates and sent by authors:
        ```
        $ {cmd} --starting-date 2020-04-01 --ending-date 2020-4-1 --authors "Herve Beraud" "Sean McGinnis
        ```
        To looking for emails related to release FFE since August 2020:
        ```
        $ {cmd} --topic ".?\[release\].*FFE.*" --starting-date 2020-8-1
        ```
        To looking for all the release countdown emails sent during victoria (18 May 2020 - 16 October 2020):
        ```
        $ {cmd} --topic ".?\[release\] Release countdown.*" --starting-date 2020-5-1
        ```
    """.format(cmd=sys.argv[0]))  # noqa
    parser = argparse.ArgumentParser(
        description='Search emails on the mailing list by topic and authors',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=epilog)
    parser.add_argument(
        '-t',
        '--topic',
        default=DEFAULT_SEARCHING_PATTERN,
        help='Regex pattern to match in emails subject.'
             f'The default pattern is set to `{DEFAULT_SEARCHING_PATTERN}` '
             'to looking for release topics on the ML.'
    )
    parser.add_argument(
        '-a',
        '--authors',
        nargs='+',
        default=[], type=str,
        help='filtering on authors within emails found with the '
             'related topic. Many authors can be given.')
    parser.add_argument(
        '--starting-date',
        type=lambda s: datetime.datetime.strptime(s, '%Y-%m-%d'),
        default=MINIMAL_DATE,
        help="Starting research at the given date. Can't be before "
             f"{MINIMAL_DATE} which is the minimal date allowed for research."
             "Notice that a research doesn't looking for a day but for an "
             "entire month, in other words day will be ignored."
    )
    parser.add_argument(
        '--ending-date',
        type=lambda s: datetime.datetime.strptime(s, '%Y-%m-%d'),
        default=datetime.datetime.today(),
        help='Ending research at the given date.'
             'Default set to today. '
             "Notice that a research doesn't looking for a day but for an "
             "entire month, in other words day will be ignored."
    )
    parser.add_argument(
        '--mailing-list',
        type=mailing_list_url,
        default=BASE_URL,
        help='Mailing list url to use for search. Should be a valid url.'
             f'Default set to {BASE_URL}.'
    )
    args = parser.parse_args()
    exit_code = 0
    mailing_list = args.mailing_list
    results = {}
    cursor = args.starting_date
    if mailing_list == BASE_URL and cursor < MINIMAL_DATE:
        print(f"--starting-date can't be inferior to {MINIMAL_DATE} "
              f"with {mailing_list}")
        sys.exit(1)
    ending = args.ending_date
    print('Looking for emails sent on {mailing_list} who match `{topic}` '
          'between {start} and {end} and sent by {authors}\n...'.format(
              mailing_list=mailing_list,
              topic=args.topic,
              start=cursor.strftime('%Y %B'),
              end=ending.strftime('%Y %B'),
              authors=', '.join(args.authors) if args.authors else 'anybody'))
    while cursor <= ending:
        year = cursor.year
        month = cursor.strftime("%B")
        if year not in results:
            results.update({year: {}})
        url = f"{mailing_list}/{year}-{month}"
        print(f"Analyzing {month} {year}: {url}")
        emails, current_exit_code = search(url, args.topic, args.authors)
        data = {
            "url": url,
            "emails": emails
        }
        results[year].update({month: data})
        cursor += relativedelta(months=1)
        exit_code = current_exit_code if exit_code == 0 else exit_code
    display(results)
    return exit_code


if __name__ == '__main__':
    sys.exit(main())
