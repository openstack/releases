===================
 Deliverable Types
===================

The type of a deliverable affects in which section it is listed on
the releases.openstack.org website, as well as which deadline applies
to it within a development cycle.

.. _`type-service`:

service
=======

This deliverable type indicates that a project provides a user-facing
long-running service with a REST API. The deadline for producing such
a deliverable in a development cycle is the 'Final RCs and intermediary
releases' week, usually located at R-1.

.. _`type-library`:

library
=======

This deliverable type indicates that a project is a library,
middleware, or other piece of software that is used to build
another project and does not, by itself, provide a long-running
service or stand-alone tool. The deadline for producing such a
deliverable in a development cycle is the 'Final release for
non-client libraries' week, usually located at R-6.

* The repository contains software used as a library for the loose and
  commonly-understood definition of "library".

.. _`type-client-library`:

client-library
==============

This deliverable type indicates that a project is a library containing
a client for an OpenStack service that is intended to be consumed by
other OpenStack services (so not a general-purpose user client such as
``shade``). The deadline for producing such a deliverable in a development
cycle is the 'Final release for client libraries' week, usually located
at R-5.

.. _`type-horizon-plugin`:

horizon-plugin
==============

This deliverable type indicates that a deliverable is meant to be
consumed by Horizon as a plug-in, to provide an integrated web UI for
a given project. The deadline for producing such a deliverable in a
development cycle is the 'Final RCs and intermediary releases' week,
usually located at R-1.

* The repository contains code meant to be dynamically loaded by
  OpenStack Horizon to provide UI to specific projects.

.. _`type-trailing`:

trailing
========

This deliverable type indicates that a deliverable is a deployment tool
or some other tool that builds on top of an existing release. The deadline
for producing such a deliverable in a development cycle is the 'cycle-trailing
Release Deadline', usually located 3 months after the coordinated release.

.. _`type-tempest-plugin`:

tempest-plugin
==============

This deliverable type indicates that a deliverable is a tempest plugin.
those need to be automatically released once at the end of a cycle.
Those may, optionally, also be released in the middle of the cycle.
Those do not need a stable branch created. Those deliverables were previously
managed by `the legacy cycle-automatic model`_.

.. _`the legacy cycle-automatic model`: ./release_models.html#cycle-automatic

.. _`type-other`:

other
=====

Deliverables without a more specific categorization are listed as
``other``. The deadline for producing such a deliverable in a development
cycle is the 'Final RCs and intermediary releases' week, usually located
at R-1.
