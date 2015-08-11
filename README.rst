============================
 OpenStack Release Tracking
============================

This repository is for tracking release requests for OpenStack
projects. The releases are managed using groups of "deliverables",
made up of individual project repositories sharing a Launchpad group
and a version number history. Many deliverables will only have one
constituent project.

Requesting a Release
====================

The PTL or release liaison for a project may request a release from
master by submitting a patch to this repository, adding the necessary
release metadata to the file describing the deliverable to be
released. The release team will review the request and provide
feedback about the version number.

The stable maintenance team, PTL, or release liaison for a project may
request a release from a stable branch by submitting a patch to this
repository, adding the necessary release metadata to the file
describing the deliverable to be released. The release team will
review the request and provide feedback about the version number. If
the stable release is requested by the stable maintenance team, it
should be acknowledged by the PTL or release liaison to ensure that
the development team is aware of the coming change.

Release Approval
================

Releases will only be denied during periods where there are known gate
issues, or when releasing will introduce unwanted
instability. Releases made late in a week may be delayed until early
in the next week unless there is a pressing need such as a gate
failure or security issue.

Who is Responsible for the Release?
===================================

The release team is responsible for helping to clearly signal the
nature of the changes in the release through good version number
selection.

The project team is responsible for understanding the implications for
consuming projects when a new release is made, and ensuring that
releases do not break other projects. When breaks occur, the project
team is responsible for taking the necessary corrective action.

Deliverable Files
=================

For deliverable set of projects, we use one YAML file per release
series to hold all of the metadata for all releases of that
deliverable. For each release, we need to track:

* the launchpad project name (such as ``oslo.config``)
* the series (Kilo, Liberty, etc.)
* for each repository

  * the name (such as ``openstack/oslo.config``)
  * the hash of the commit to be tagged

* the version number to use
* highlights for the release notes email (optional)

We track this metadata for the history of all releases of the
deliverable, so we can render a set of release history documentation.

The file should be named based on the deliverable to be tagged, so
releases for ``liberty`` from the ``openstack/oslo.config`` repository
will have a file in ``openstack/releases`` called
``deliverables/liberty/oslo.config.yaml``. Releases of the same deliverable from
the ``stable/kilo`` branch will be described by
``deliverables/kilo/oslo.config.yaml``.

Deliverables File Schema
========================

The top level of a deliverable file is a mapping with keys:

``launchpad``
  The slug name of the launchpad project, suitable for use in URLs.

``releases``
  A list of the releases for the deliverable.

Each `release` entry is a mapping with keys:

``version``
  The version tag for that release, to be applied to all of the member
  projects.

``projects``
  A list of all of the projects making up the deliverable for that
  release.

``highlights``
  An optional message to be included in the release note email
  announcing the release.

Each `project` entry is a mapping with keys:

``repo``
  The name of the repository on git.openstack.org.

``hash``
  The SHA1 hash for the commit to receive the version tag.

Examples
========

For example, one version of
``deliverables/liberty/oslo.config.yaml`` might contain::

   ---
   launchpad: oslo.config
   releases:
     - version: 1.12.0
       projects:
         - repo: openstack/oslo.config
           hash: 02a86d2eefeda5144ea8c39657aed24b8b0c9a39

and then for the subsequent release it would be updated to contain::

   ---
   launchpad: oslo.config
   releases:
     - version: 1.12.0
       projects:
         - repo: openstack/oslo.config
           hash: 02a86d2eefeda5144ea8c39657aed24b8b0c9a39
     - version: 1.12.1
       projects:
         - repo: openstack/oslo.config
           hash: 0c9113f68285f7b55ca01f0bbb5ce6cddada5023
       highlights: >
          This release includes the change to stop importing
          from the 'oslo' namespace package.

For deliverables with multiple repositories, the list of projects
would contain all of them. For example, the Neutron deliverable might
be described by ``deliverables/liberty/neutron.yaml`` containing:

::

   ---
   launchpad: neutron
   releases:
     - version: 7.0.0
       projects:
         - repo: openstack/neutron
           hash: somethingunique
         - repo: openstack/neutron-fwaas
           hash: somethingunique
         - repo: openstack/neutron-lbaas
           hash: somethingunique
         - repo: openstack/neutron-vpnaas
           hash: somethingunique
