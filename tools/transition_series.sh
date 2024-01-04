#!/bin/bash
#
# Convenience wrapper transition a release cycle to its next stable
# phase.

TOOLSDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASEDIR=$(dirname $TOOLSDIR)
#source $TOOLSDIR/functions

if [[ $# -lt 2 ]]; then
    echo "Usage: $(basename $0) <series> <tag>"
    echo ""
    echo "<tag> either 'em', 'eom' or 'eol'"
    exit 1
fi

series="$1"
tag="$2"

if [[ -z "$VIRTUAL_ENV" ]]; then
    if [[ ! -d $BASEDIR/.tox/venv ]]; then
        (cd $BASEDIR && tox -e venv --notest)
    fi
    source $BASEDIR/.tox/venv/bin/activate
fi

echo "Finding deliverables for $series series..."
deliverables=$(list-deliverables --series $series)

errors=()
for deliverable in $deliverables; do
    echo "Adding $series-$tag tag for $deliverable..."
    new-release $series $deliverable $tag
    if [[ $? -ne 0 ]]; then
        echo ""
        echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        echo "$deliverable failed to update"
        echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        echo ""

        errors+=("$deliverable")
    fi
done

if [[ ${#errors[@]} -ne 0 ]]; then
    echo ""
    echo "Errors adding tags to some deliverables. Check the following:"
    echo "  ${errors[@]}"
    exit 1
fi
