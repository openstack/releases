#!/bin/bash
#
# Script to generate a release announcement for a project.
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

set -e

if [ $# -lt 1 ]; then
    echo "Usage: $0 path-to-repository [version]"
    echo
    echo "Example: $0 ~/repos/openstack/oslo.rootwrap"
    echo "Example: $0 ~/repos/openstack/oslo.rootwrap 3.0.3"
    exit 2
fi

set -x

TOOLSDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $TOOLSDIR/functions
RELEASESDIR=$(realpath $TOOLSDIR/..)

REPODIR=$(cd $1 && pwd)
VERSION=$2

# If the version looks like an alpha or beta, ignore it. The script
# for producing release notes has templates for regular releases and
# release candidates.
if [[ $VERSION =~ (a|b) ]]; then
    echo "No announcements are generated for alpha or beta releases."
    exit 0
fi

# The repository directory may be named something other than what the
# repository is, if we're running under CI or someone has checked it
# out locally to an alternate name. Use the git remote URL as a source
# of better information for the real repository name.
REMOTE_URL=$(cd $REPODIR && git config --get remote.origin.url || echo "")
if [ ! -z "$REMOTE_URL" ] && [ "$REMOTE_URL" != "file:///dev/null" ]; then
    # Make sure .git extensions are not included
    SHORTNAME=$(basename $REMOTE_URL .git)
else
    # WARNING(dhellmann): This formulation only works in CI where the
    # workspace structure matches the git repo names upstream.
    SHORTNAME=$(basename $REPODIR)
fi

# Assign a default "from" email address if one is not specified by the
# user's environment.
export EMAIL=${EMAIL:-no-reply@openstack.org}

if [[ -z "$VIRTUAL_ENV" ]]; then
    if ! (cd $RELEASESDIR && tox -e venv --notest); then
        echo "Failed to build virtualenv"
        exit 1
    fi
    source $RELEASESDIR/.tox/venv/bin/activate
fi

# Make our output directory before we start moving around into
# temporary directories.
RELNOTESDIR="$PWD/relnotes"
mkdir -p $RELNOTESDIR

# Set up temporary directory for scratch files
setup_temp_space announce-$SHORTNAME

cd $REPODIR

# Determine the most recent tag if we weren't given a value.
if [[ -z "$VERSION" ]]; then
    VERSION=$(get_last_tag)
fi

# Look for the previous version on the same branch. If the command
# fails because there are no other tags, we will produce the entire
# history.
PREVIOUS_VERSION=$(git describe --abbrev=0 ${VERSION}^ 2>/dev/null || echo "")
if [[ "$PREVIOUS_VERSION" = "" ]]; then
    # There was no previous tag, so we're looking for the full history
    # of the project.
    PREVIOUS_VERSION=$(git rev-list --max-parents=0 HEAD | tail -1)
    first_release="--first-release"
fi

# Extract the tag message by parsing the git show output, which looks
# something like:
#
# tag 2.0.0
# Tagger: Doug Hellmann <doug@doughellmann.com>
# Date:   Tue Dec 1 21:45:44 2015 +0000
#
# python-keystoneclient 2.0.0 release
#
# meta:version: 2.0.0
# meta:series: mitaka
# meta:release-type: release
# -----BEGIN PGP SIGNATURE-----
# Comment: GPGTools - http://gpgtools.org
#
# iQEcBAABAgAGBQJWXhUIAAoJEDttBqDEKEN62rMH/ihLAGfw5GxPLmdEpt7gsLJu
# ...
#
TAG_META=$(git show --no-patch "$VERSION" | grep '^meta:' || true)
if [[ -z "$TAG_META" ]]; then
    echo "WARNING: Missing meta lines in $VERSION tag message,"
    echo "         skipping announcement."
    echo
    echo "Was the tag for $VERSION created with release.sh?"
    exit 0
fi

function get_tag_meta {
    typeset fieldname="$1"

    echo "$TAG_META" | grep "^meta:$fieldname:" | sed "s/meta:$fieldname: *//"
}

# How far back should we look for release info? If there is no
# explicit metadata (signaled by passing "-"), use whatever previous
# version number we were able to detect.
DIFF_START=$(get_tag_meta diff-start)
if [[ "$DIFF_START" == "-" ]]; then
    DIFF_START="$PREVIOUS_VERSION"
fi

# The series name is part of the commit message left by release.sh.
SERIES=$(get_tag_meta series)

# The type of release this is.
RELEASETYPE=$(get_tag_meta release-type)

# Figure out if that series is a stable branch or not. We don't
# release pre-releases on stable branches, so we only need to check
# for stable if the release type is a normal release.
if [[ $RELEASETYPE = "release" ]]; then
    if git branch -a | grep -q origin/stable/$SERIES; then
        stable="--stable"
    fi
fi

# If this is the first full release in a series, it isn't "stable"
# yet.
FIRST_FULL=$(get_tag_meta first)
if [[ $FIRST_FULL = "yes" ]]; then
    stable=""
fi

# Only include the PyPI link if we are told to.
INCLUDE_PYPI_LINK=$(get_tag_meta pypi)
if [[ "$INCLUDE_PYPI_LINK" == "yes" ]]; then
    include_pypi_link="--include-pypi-link"
fi

echo "$DIFF_START to $VERSION on $SERIES"

relnotes_file="$RELNOTESDIR/$SHORTNAME-$VERSION"

# As we use importlib to retrieve information we have to pass the
# importable name of the module, example: oslo.messaging => oslo_messaging
modified_shortname=${SHORTNAME//\./_}

# ensure that the package is a valid package that can be imported by
# importlib.metadata
python -m pip install .
project_name=$(python -c "import importlib.metadata; print(importlib.metadata.metadata('${modified_shortname}')['Name'])" || true)
if [ -n "${project_name}" ] ; then
    description=$(python -c "import importlib.metadata; print(importlib.metadata.metadata('${modified_shortname}')['Summary'])")
else
    # As a last resort, guess that the project name may be the same as that
    # of the local working directory at the point this script is invoked.
    project_name="$(basename $(pwd))"
fi

# If we are running in the context of a Zuul CI system,
# we can just infer the project name from the repo name it supplies.
if [ -n "$ZUUL_PROJECT" ] ; then
    project_name="$(basename ${ZUUL_PROJECT})"
fi

echo
echo "Generating email body in $relnotes_file"
release-notes \
    --email \
    --series "$SERIES" \
    $stable \
    $first_release \
    --publishing-dir-name "$SHORTNAME" \
    . "$project_name" "$DIFF_START" "$VERSION" \
    $include_pypi_link \
    --description "$description" \
    | tee $relnotes_file

echo
echo "Sending release announcement"
send-mail -v $relnotes_file
