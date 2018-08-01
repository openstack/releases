#!/bin/bash
#
# Convenience wrapper to show the unreleased changes in all
# projects that have not yet been released.

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

# Figure out the previous series from the releases directory.
previous_series=$(ls $BASEDIR/deliverables | grep -B1 $current_series \
    | head -n 1)
if [ -z "$previous_series" ]; then
    echo "Could not determine the previous release series."
    exit 1
fi

echo "Finding deliverables with no releases in the current series..."
deliverables=$(list-deliverables --unreleased)
for deliv in $deliverables; do
    echo $deliv
done

function show_deliv {
    # Show some details about the deliverable

    title $deliv
    echo
    list-deliverables --deliverable "$deliv" -v

    # Show the changes for each repo for the deliverable, as defined
    # by the previous series releases.
    repos=$(list-deliverables --deliverable "$deliv" --repos \
        --series "$previous_series")
    $TOOLSDIR/list_unreleased_changes.sh master $repos
}

for deliv in $deliverables; do

    owner=$(echo \
        $(grep team $BASEDIR/deliverables/$current_series/${deliv}.yaml \
            | cut -f2 -d:) \
        | sed -e 's/ /-/g')
    if [[ -z "$owner" ]]; then
        echo "ERROR: No owner for $deliv"
        continue
    fi

    outfile=unreleased-${current_series}-${owner}.txt

    show_deliv $deliv 2>&1 | tee $outfile
done
