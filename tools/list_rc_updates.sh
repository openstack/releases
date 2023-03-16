#!/bin/bash
#
# Convenience wrapper to show the unreleased changes in cycle-with-rc
# projects that have not yet been released. This is typically used
# after the first RC is cut to look for updates that need to be
# released.

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
    from openstack_releases import series_status; \
    series_status_data = series_status.SeriesStatus.default(); \
    print(series_status_data[openstack_releases.defaults.RELEASE].release_id)')
if [ -z "$current_series" ]; then
    echo "Could not determine the current release series."
    exit 1
fi

echo "Finding repos in the current series..."
repos=$(list-deliverables --model cycle-with-rc -r)

${TOOLSDIR}/list_unreleased_changes.sh stable/${current_series} ${repos}
