#!/bin/bash -xe

# Run as: tox -e history

TOOLSDIR=$(dirname $0)
REPOS=/mnt/repos/openstack

if [ ! -z "$1" ]; then
    cd $1
fi

function gen {
    $TOOLSDIR/tag_history_from_lp.py $@
}

function gen_from_git {
    $TOOLSDIR/tag_history_from_git.py $@
}

CLIENT_NAMES="
"

# ALL CLIENTS
for c in $CLIENT_NAMES; do
    d=$REPOS/$c
    gen_from_git $(basename $d) $d
done

# Remove things that don't look like named releases
rm -rf deliverables/[0-9]*

# Remove anything that had a "trunk" series
rm -rf deliverables/trunk
