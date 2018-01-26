#!/bin/bash
#
# Script to produce the zuul commands for reenqueuing a release if the
# jobs fail part way through. This command assumes that the tag has
# been applied to the repository already. If that is not true, we can
# revert and re-land the patch in openstack/releases.

if [[ $# -lt 2 ]]; then
    echo "Usage: $(basename $0) <repo> <tag>"
    echo "repo should be e.g. openstack/glance"
    exit 1
fi

repo="$1"
tag="$2"

TOOLSDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASEDIR=$(dirname $TOOLSDIR)
source $TOOLSDIR/functions

setup_temp_space 'build-reenqueue-commands'

clone_repo $repo

hash=$(cd $repo && git show-ref -s $tag)

pipelines="tag"

if [[ $tag =~ (a|b|rc) ]]; then
    pipelines="$pipelines pre-release"
else
    pipelines="$pipelines release"
fi

for pipeline in $pipelines; do
    echo "zuul enqueue-ref --tenant=openstack --trigger=gerrit --pipeline=$pipeline --project=$repo --ref=refs/tags/$tag --newrev=$hash"
done
