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
import collections
import contextlib
import os
import shutil
import subprocess
import sys
import tempfile

from prompt_toolkit.completion import WordCompleter
from prompt_toolkit import prompt
from prompt_toolkit.validation import ValidationError
from prompt_toolkit.validation import Validator

from tqdm import tqdm

from openstack_releases import gitutils
from openstack_releases import yamlutils

NOTES_URL_TPL = 'https://docs.openstack.org/releasenotes/%s/%s.html'
RELEASE_INCREMENTS = {
    'bugfix': (0, 0, 1),
    'feature': (0, 1, 0),
    'major': (1, 0, 0),
}
RELEASE_KINDS = tuple(sorted(RELEASE_INCREMENTS))
OVERVIEW = """
A interactive command line helper tool that makes it easy create
releases of openstack projects.

Supported features:

- Tab completion

Notes:

- To exit the multi-line highlights text entry field press
  'escape' then 'enter'.
"""


def to_unicode(blob, encoding='utf8'):
    if isinstance(blob, str):
        return blob
    elif isinstance(blob, bytes):
        return blob.decode(encoding)
    else:
        raise TypeError("Unable to convert %r to a text type" % blob)


class NoEmptyValidator(Validator):
    def validate(self, document):
        text = document.text.strip()
        if len(text) == 0:
            raise ValidationError(message='Empty input is not allowed')


class SetValidator(Validator):
    def __init__(self, allowed_values, show_possible=False):
        super(SetValidator, self).__init__()
        self.allowed_values = frozenset(allowed_values)
        self.show_possible = show_possible

    def validate(self, document):
        text = document.text
        if text not in self.allowed_values:
            if self.show_possible:
                raise ValidationError(
                    message='This input is not allowed, '
                            ' please choose from %s' % self.allowed_values)
            else:
                raise ValidationError(
                    message='This input is not allowed')


@contextlib.contextmanager
def tempdir(**kwargs):
    # This seems like it was only added in python 3.2
    # Make it since its useful...
    # See: http://bugs.python.org/file12970/tempdir.patch
    tdir = tempfile.mkdtemp(**kwargs)
    try:
        yield tdir
    finally:
        shutil.rmtree(tdir)


def yes_no_prompt(title, default=True):
    result = prompt(title, completer=WordCompleter(['yes', 'no']),
                    validator=SetValidator(['yes', 'no'],
                                           show_possible=True),
                    default="yes" if default else "no")
    return result == 'yes'


def clean_changes(changes):
    for line in changes:
        line = to_unicode(line)
        sha, descr = line.split(" ", 1)
        yield sha, descr


def generate_suggested_next_version(last_release, release_type):
    """Generates a suggested next version for a given project."""
    if not last_release:
        return None
    last_version = last_release['version'].split('.')
    # Ensure we have at least 3 components...
    while len(last_version) < 3:
        last_version.append(0)
    increment = RELEASE_INCREMENTS[release_type]
    new_version_parts = []
    for cur, inc in zip(last_version, increment):
        new_version_parts.append(str(int(cur) + inc))
    # Ensure that we reset any numbers after the version we
    # incremented, since those should now roll-over to the next
    # version.
    if release_type == 'major':
        for i in range(1, len(new_version_parts)):
            new_version_parts[i] = '0'
    if release_type == 'feature':
        for i in range(2, len(new_version_parts)):
            new_version_parts[i] = '0'
    if release_type == 'bugfix':
        for i in range(3, len(new_version_parts)):
            new_version_parts[i] = '0'
    return '.'.join(new_version_parts)


def maybe_create_release(release_repo_path, deliverable_info,
                         last_release, change_lines,
                         latest_cycle, project,
                         short_project, max_changes_show=100,
                         should_prompt=True):
    if last_release:
        print("%s changes to release since %s are:"
              % (len(change_lines), last_release['version']))
    else:
        print("%s changes to release are:" % (len(change_lines)))
    for sha, descr in change_lines[0:max_changes_show]:
        print("  %s %s" % (sha, descr))
    leftover_change_lines = change_lines[max_changes_show:]
    if leftover_change_lines:
        print("   and %s more changes..." % len(leftover_change_lines))
    if not should_prompt:
        return
    create_release = yes_no_prompt('Create a release in %s containing'
                                   ' those changes? ' % latest_cycle)
    if create_release:
        # NOTE(harlowja): use of an ordered-dict here is on purpose, so that
        # the ordering here stays similar to what is already being used.
        newest_release_path = os.path.join(
            release_repo_path, 'deliverables',
            latest_cycle, "%s.yaml" % short_project)
        ok_change = True
        if os.path.exists(newest_release_path):
            with open(newest_release_path, 'rb') as fh:
                newest_release = yamlutils.loads(fh.read())
            ok_change = yes_no_prompt("Alter existing file (reformatting"
                                      " may lose comments and some existing"
                                      " yaml indenting/structure)? ")
        else:
            notes_link = to_unicode(
                NOTES_URL_TPL % (short_project, latest_cycle))
            notes_link = prompt(
                "Release notes link: ",
                validator=NoEmptyValidator(),
                default=notes_link)
            if deliverable_info:
                launchpad_project = to_unicode(deliverable_info['launchpad'])
            else:
                launchpad_project = prompt(
                    "Launchpad project name: ",
                    validator=NoEmptyValidator(),
                    default=to_unicode(short_project))
            team = prompt("Project team: ",
                          validator=NoEmptyValidator(),
                          default=to_unicode(launchpad_project))
            include_pypi_link = yes_no_prompt("Include pypi link? ")
            newest_release = collections.OrderedDict([
                ('launchpad', launchpad_project),
                ('include-pypi-link', include_pypi_link),
                ('release-notes', notes_link),
                ('releases', []),
                ('team', team),
            ])
        possible_hashes = []
        for sha, _descr in change_lines:
            possible_hashes.append(sha)
        release_kind = prompt("Release type: ",
                              validator=SetValidator(RELEASE_KINDS),
                              completer=WordCompleter(RELEASE_KINDS))
        suggested_version = generate_suggested_next_version(
            last_release, release_kind)
        if not suggested_version:
            suggested_version = ''
        version = prompt("Release version: ",
                         validator=NoEmptyValidator(),
                         default=to_unicode(suggested_version))
        highlights = prompt("Highlights (esc then enter to"
                            " exit): ", multiline=True)
        highlights = highlights.strip()
        release_hash = prompt("Hash to release at: ",
                              validator=SetValidator(possible_hashes),
                              completer=WordCompleter(possible_hashes),
                              default=possible_hashes[0])
        new_release = collections.OrderedDict([
            ('version', version),
            ('projects', [
                collections.OrderedDict([
                    ('repo', project),
                    ('hash', release_hash),
                ]),
            ]),
        ])
        if highlights:
            new_release['highlights'] = highlights
        if not ok_change:
            new_release = yamlutils.dumps(new_release)
            print("You may manually adjust %s and add:" % newest_release_path)
            print(new_release)
        else:
            try:
                newest_release['releases'].append(new_release)
            except KeyError:
                newest_release['releases'] = [new_release]
            newest_release = yamlutils.dumps(newest_release)
            with open(newest_release_path, 'w') as fh:
                fh.write(newest_release)


def find_last_release_path(release_repo_path,
                           latest_cycle, cycles,
                           project):
    latest_cycle_idx = cycles.index(latest_cycle)
    for a_cycle in reversed(cycles[0:latest_cycle_idx + 1]):
        release_path = os.path.join(release_repo_path, 'deliverables',
                                    a_cycle, "%s.yaml" % project)
        if os.path.isfile(release_path):
            return a_cycle, release_path
    return (None, None)


def read_projects(path):
    """Reads a list of openstack projects from a file.

    Example file::

        $ cat tools/oslo.txt
        openstack/oslo.i18n

    """
    raw_projects = []
    with open(path) as fh:
        for line in fh.read().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            else:
                raw_projects.append(line)
    return raw_projects


def clone_repos(save_dir, projects):
    """Clones a bunch of openstack repos."""
    repos = {}
    for project, short_project in tqdm(
        projects, unit='repo', desc='Cloning %s repos' % len(projects)):
        gitutils.clone_repo(save_dir, project)
        repos[project] = os.path.join(save_dir, project)
    return repos


def extract_projects(raw_projects):
    projects = []
    seen_projects = set()
    for project in sorted(raw_projects):
        project_pieces = project.split("/", 1)
        if len(project_pieces) == 1:
            # This handles someone passing in just the base project
            # name instead of the fully qualified project name.
            project_pieces = ['openstack', project]
            project = "openstack/%s" % project
        if project in seen_projects:
            continue
        short_project = project_pieces[-1]
        projects.append((project, short_project))
        seen_projects.add(project)
    return projects


def main():
    parser = argparse.ArgumentParser(
        description=OVERVIEW,
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-p", "--projects", metavar="FILE",
                        help="File containing projects to analyze")
    parser.add_argument("-r", "--releases", metavar="PATH",
                        help="Release repository path (default=%(default)s)",
                        default=os.getcwd())
    parser.add_argument("--only-show", action="store_true", default=False,
                        help="Only list changes and do not"
                             " prompt to propose")
    parser.add_argument('project', nargs='*', help="Project to analyze")
    args = parser.parse_args()
    release_repo_path = args.releases
    release_deliverable_path = os.path.join(release_repo_path, 'deliverables')
    try:
        cycles = sorted([c for c in os.listdir(release_deliverable_path)
                         if not c.startswith("_")])
        latest_cycle = cycles[-1]
    except (IndexError, OSError):
        print("Please ensure release deliverables directory '%s' exists and"
              " it contains at least one release"
              " cycle." % (release_deliverable_path),
              file=sys.stderr)
        return 1
    raw_projects = []
    if args.projects:
        try:
            raw_projects.extend(read_projects(args.projects))
        except IOError:
            print("Please ensure projects '%s' file exists"
                  " and is readable." % (args.projects), file=sys.stderr)
            return 1
    raw_projects.extend(args.project)
    projects = extract_projects(raw_projects)
    if not projects:
        print("Please provide at least one project.")
        return 1
    with tempdir() as a_temp_dir:
        # Clone fresh copies of all the repos (so we have a good
        # non-altered starting set of repos, in the future we can
        # likely relax this).
        repos = clone_repos(a_temp_dir, projects)
        for project, short_project in projects:
            repo_path = repos[project]
            last_release_cycle, last_release_path = find_last_release_path(
                release_repo_path, latest_cycle, cycles, short_project)
            if last_release_path is None or last_release_cycle is None:
                last_release = None
                deliverable_info = None
            else:
                with open(last_release_path, 'rb') as fh:
                    deliverable_info = yamlutils.loads(fh.read())
                try:
                    last_release = deliverable_info['releases'][-1]
                except (IndexError, KeyError, TypeError):
                    last_release = None
            print("== Analysis of project '%s' ==" % short_project)
            if not last_release:
                print("It has never had a release.")
                cmd = ['git', 'log', '--pretty=oneline']
                output = subprocess.check_output(cmd, cwd=repo_path).decode('utf-8')
                output = output.strip()
                changes = list(clean_changes(output.splitlines()))
            else:
                print("The last release of project %s was:" % short_project)
                print("  Released in: %s" % last_release_cycle)
                print("  Version: %s" % last_release['version'])
                print("  At sha: %s" % last_release['projects'][0]['hash'])
                cmd = ['git', 'log', '--pretty=oneline',
                       "%s..HEAD" % last_release['projects'][0]['hash']]
                output = subprocess.check_output(cmd, cwd=repo_path).decode('utf-8')
                output = output.strip()
                changes = list(clean_changes(output.splitlines()))
            if changes:
                maybe_create_release(release_repo_path, deliverable_info,
                                     last_release, changes,
                                     latest_cycle, project,
                                     short_project,
                                     should_prompt=not args.only_show)
            else:
                print("  No changes.")
    return 0
