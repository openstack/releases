#!/bin/bash
#
# Convenience wrapper to show details about projects that have not yet
# been releases.

TOOLSDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASEDIR=$(dirname $TOOLSDIR)
source $TOOLSDIR/functions

if [[ -z "$VIRTUAL_ENV" ]]; then
    if [[ ! -d $BASEDIR/.tox/venv ]]; then
        (cd $BASEDIR && tox -e venv --notest)
    fi
    source $BASEDIR/.tox/venv/bin/activate
fi

setup_temp_space inactive-project-report

# Figure out the current series from the releases directory.
current_series=$(python -c 'import openstack_releases.defaults; \
    print(openstack_releases.defaults.RELEASE)')
if [ -z "$current_series" ]; then
    echo "Could not determine the current release series."
    exit 1
fi

# Figure out the previous series from the releases directory.
previous_series=$(ls $BASEDIR/deliverables | grep -B1 $current_series \
    | head -n 1)
if [ -z "$previous_series" ]; then
    echo "Could not determine the previous release series."
    exit 1
fi

echo "Finding deliverables with no releases during ${current_series}..."
deliverables=$(list-deliverables --unreleased)

for deliv in $deliverables; do
    title $deliv

    # Show some details about the deliverable
    echo
    list-deliverables --deliverable "$deliv" -v

    repos=$(list-deliverables --deliverable "$deliv" --repos \
        --series "$previous_series")

    for repo in $repos; do
        title "$repo"
        echo
        clone_repo $repo
        cd $repo
        echo "Current version: $(git describe)"
        echo
        git log -n 1 --no-notes --decorate
        echo
        cd $MYTMPDIR
    done
done
