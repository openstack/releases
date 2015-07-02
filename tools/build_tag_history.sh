#!/bin/bash -x

# Run as: tox -e venv -- `pwd`/tools/build_tag_history.sh

TOOLSDIR=$(dirname $0)
REPOS=/mnt/repos/openstack

if [ ! -z "$1" ]; then
    cd $1
fi

function gen {
    $TOOLSDIR/tag_history_from_lp.py $@
}

gen nova $REPOS/nova

gen swift $REPOS/swift
gen swift-bench $REPOS/swift-bench

gen glance $REPOS/glance
gen glance_store $REPOS/glance_store

gen keystone $REPOS/keystone
gen keystoneauth $REPOS/keystoneauth
gen keystonemiddleware $REPOS/keystonemiddleware
gen pycadf $REPOS/pycadf
gen python-keystone-kerberos $REPOS/python-keystone-kerberos
gen keystoneauth-saml2 $REPOS/keystoneauth-saml2

gen horizon $REPOS/horizon
gen django_openstack_auth $REPOS/django_openstack_auth
gen django-openstack-auth-kerberos $REPOS/django-openstack-auth-kerberos
gen tuskar-ui $REPOS/tuskar-ui
gen manlia-ui $REPOS/manila-ui

gen neutron $REPOS/neutron $REPOS/neutron-fwaas $REPOS/neutron-lbaas \
    $REPOS/neutron-vpnaas $REPOS/dragonflow \
    $REPOS/octavia $REPOS/vmware-nsx
for d in $REPOS/networking-*; do
    gen $(basename $d) $d
done

gen cinder $REPOS/cinder
gen os-brick $REPOS/os-brick

gen ceilometer $REPOS/ceilometer
gen ceilometermiddleware $REPOS/ceilometermiddleware
gen gnocchi $REPOS/gnocchi
gen aodh $REPOS/aodh

gen heat $REPOS/heat
gen heat-cfntools $REPOS/heat-cfntools
gen heat-translator $REPOS/heat-translator

gen trove $REPOS/trove
gen trove-integration $REPOS/trove-integration

gen bifrost $REPOS/bifrost
gen coreos-image-builder $REPOS/coreos-image-builder
gen ironic $REPOS/ironic
gen ironic-inspector $REPOS/ironic-inspector
gen ironic-lib $REPOS/ironic-lib
gen ironic-python-agent $REPOS/ironic-python-agent

gen tempest-lib $REPOS/tempest-lib
gen hacking $REPOS/hacking
gen os-testr $REPOS/os-testr
gen bashate $REPOS/bashate

# TripleO ?

gen zaqar $REPOS/zaqar

gen sahara $REPOS/sahara $REPOS/sahara-dashboard $REPOS/sahara-extra \
    $REPOS/sahara-image-elements

gen barbican $REPOS/barbican
gen castellan $REPOS/castellan
gen kite $REPOS/kite

gen designate $REPOS/designate $REPOS/designate-dashboard

gen magnum $REPOS/magnum

gen manila $REPOS/manila $REPOS/manila-image-elements

gen murano $REPOS/murano $REPOS/murano-dashboard $REPOS/murano-agent \
    $REPOS/murano-apps

gen cliff $REPOS/cliff
gen os-client-config $REPOS/os-client-config

gen congress $REPOS/congress

gen rally $REPOS/rally

gen mistral $REPOS/mistral $REPOS/mistral-dashboard $REPOS/mistral-extra

gen magnetodb $REPOS/magnetodb

gen solum $REPOS/solum

gen cue $REPOS/cue $REPOS/cue-dashboard

# ALL CLIENTS
for d in $REPOS/python-*client; do
    gen $(basename $d) $d
done

# OSLO
OSLO_REPOS="
automaton
debtcollector
futurist
mox3
oslo-incubator
oslo-specs
oslo.cache
oslo.concurrency
oslo.config
oslo.context
oslo.db
oslo.i18n
oslo.log
oslo.messaging
oslo.middleware
oslo.policy
oslo.rootwrap
oslo.serialization
oslo.service
oslo.utils
oslo.versionedobjects
oslo.vmware
oslosphinx
oslotest
pylockfile
stevedore
taskflow
tooz
"

for repo in $OSLO_REPOS; do
    gen $repo $REPOS/$repo
done

# Remove things that don't look like named releases
rm -rf deliverables/[0-9]*

# Remove anything that had a "trunk" series
rm -rf deliverables/trunk
