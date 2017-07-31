#!/bin/bash -x
#
# Wrapper around yamllint that only looks at recent branches to avoid
# us having to reformat really old deliverable files.

bindir=$(dirname $0)
topdir=$(dirname $bindir)

# determine the 3 most recent series, since those are most likely to
# still be open
series=$(ls -1d deliverables/* | tail -n 3)

yamllint -f parsable -c $topdir/yamllint.yml $series deliverables/_independent
