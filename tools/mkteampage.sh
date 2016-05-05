#!/bin/bash

PROJ=$1

SERIES=$(ls deliverables/*/*${PROJ}* | cut -f2 -d/ | sort -ru)

function line {
    typeset c="$1"
    sed -e "s/./$c/g"
}

echo =${PROJ}= | line =
echo " ${PROJ^}"
echo =${PROJ}= | line =
echo
for s in $SERIES
do
    echo ${s^}
    echo $s | line =
    echo
    echo ".. deliverable::"
    echo "   :series: $s"
    echo "   :team: $PROJ"
    echo
done
