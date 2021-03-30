#!/bin/bash
#
# Convenience wrapper to show cycle-with-rc non trailing deliverables that
# have not done a RC1 yet, for which a release should be proposed from HEAD,
# and include stable branch creation.

TOOLSDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASEDIR=$(dirname $TOOLSDIR)
source $TOOLSDIR/functions

if [[ -z "$VIRTUAL_ENV" ]]; then
    if [[ ! -d $BASEDIR/.tox/venv ]]; then
        (cd $BASEDIR && tox -e venv --notest)
    fi
    source $BASEDIR/.tox/venv/bin/activate
fi

# Figure out the current series from the releases directory.
current_series=$(python -c 'import openstack_releases.defaults; \
    print(openstack_releases.defaults.RELEASE)')
if [ -z "$current_series" ]; then
    echo "Could not determine the current release series."
    exit 1
fi

trailing_projects=$(list-deliverables \
    --missing-rc \
    --model cycle-with-rc \
    --type trailing)
list-deliverables --missing-rc --model cycle-with-rc | \
    grep -v "${trailing_projects}"
