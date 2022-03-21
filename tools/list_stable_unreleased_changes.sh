#!/bin/bash
#
# Convenience wrapper to show the unreleased changes for a stable
# $series in all projects, so we don't have to remember the
# incantation.

if [[ $# -ne 1 ]]; then
    echo "Usage: $(basename $0) <series>"
    exit 1
fi

SERIES=${1}

TOOLSDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASEDIR=$(dirname $TOOLSDIR)
source $TOOLSDIR/functions

# Set up the virtualenv where the list-deliverables command will be
# found. This is done outside of the invocation below because
# otherwise we get the tox output mixed up in the repo list output and
# try to do things like look at the history of "venv" and
# "installing".
if [[ -z "$VIRTUAL_ENV" ]]; then
    if [[ ! -d $BASEDIR/.tox/venv ]]; then
        (cd $BASEDIR && tox -e venv --notest)
    fi
    source $BASEDIR/.tox/venv/bin/activate
fi

repos="$(list-deliverables --repos --series $SERIES)"

$TOOLSDIR/list_unreleased_changes.sh stable/$SERIES $repos
