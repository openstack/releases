#!/bin/bash -xe

# Run as: tox -e history

TOOLSDIR=$(dirname $0)
REPOS=/mnt/repos

if [ ! -z "$1" ]; then
    cd $1
fi

function gen {
    $TOOLSDIR/tag_history_from_lp.py --series liberty $1 $REPOS/$2
}

function gen_from_git {
    $TOOLSDIR/tag_history_from_git.py $1 $REPOS/$2
}

# No repository or series history in LP
# gen astara openstack/astara

gen_from_git cloudkitty stackforge/cloudkitty

# Only pre-release versions
gen_from_git congress openstack/congress

# Only alpha versions
gen_from_git cue openstack/cue

gen_from_git gnocchi openstack/gnocchi

gen_from_git coreos-image-builder openstack/coreos-image-builder
gen_from_git ironic-inspector openstack/ironic-inspector

gen_from_git magnum openstack/magnum
gen_from_git magnum-ui openstack/magnum-ui

gen_from_git mistral openstack/mistral

gen_from_git murano openstack/murano
gen_from_git murano-agent openstack/murano-agent
gen_from_git murano-apps openstack/murano-apps
gen_from_git murano-dashboard openstack/murano-dashboard

gen_from_git searchlight openstack/searchlight

gen_from_git solum openstack/solum

gen_from_git dib-utils openstack/dib-utils
gen_from_git diskimage-builder openstack/diskimage-builder
gen_from_git instack-undercloud openstack/instack-undercloud
gen_from_git os-apply-config openstack/os-apply-config
gen_from_git os-cloud-config openstack/os-cloud-config
gen_from_git os-collect-config openstack/os-collect-config
gen_from_git os-net-config openstack/os-net-config
gen_from_git os-refresh-config openstack/os-refresh-config
gen_from_git tuskar openstack/tuskar

# These lib repositories don't exist
# openstack/networking-hpe
# openstack/networking-hyperv

LIB_NAMES="
stackforge/python-cloudkittyclient
stackforge/cloudkitty-dashboard
openstack/python-congressclient
openstack/cue-dashboard
openstack/python-cueclient
openstack/castellan
openstack/designate-dashboard
openstack/python-gnocchiclient
openstack/django-openstack-auth-kerberos
openstack/horizon-cisco-ui
openstack/manila-ui
openstack/tuskar-ui
openstack/python-dracclient
openstack/python-ironic-inspector-client
openstack/python-magnumclient
openstack/mistral-dashboard
openstack/python-mistralclient
openstack/python-muranoclient
openstack/dragonflow
openstack/kuryr
openstack/networking-ale-omniswitch
openstack/networking-arista
openstack/networking-bagpipe
openstack/networking-bgpvpn
openstack/networking-calico
openstack/networking-cisco
openstack/networking-fortinet
openstack/networking-infoblox
openstack/networking-fujitsu
openstack/networking-l2gw
openstack/networking-lenovo
openstack/networking-midonet
openstack/networking-odl
openstack/networking-ofagent
openstack/networking-onos
openstack/networking-ovn
openstack/networking-plumgrid
openstack/networking-powervm
openstack/networking-sfc
openstack/networking-vsphere
openstack/octavia
openstack/python-neutron-pd-driver
openstack/vmware-nsx
openstack/rally
openstack/python-solumclient
openstack/solum-dashboard
openstack/instack
openstack/python-tripleoclient
openstack/python-tuskarclient
openstack/tripleo-common
openstack/tripleo-heat-templates
openstack/tripleo-image-elements
"

# ALL LIBS
for c in $LIB_NAMES; do
    gen_from_git $(basename $c) $c
done

# Remove things that don't look like named releases
rm -rf deliverables/[0-9]*

# Remove anything that had a "trunk" series
rm -rf deliverables/trunk
