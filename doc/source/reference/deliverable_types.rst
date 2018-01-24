===================
 Deliverable Types
===================

.. _`type-horizon-plugin`:

horizon-plugin
==============

This deliverable type indicates that a deliverable is meant to be
consumed by Horizon as a plug-in, to provide an integrated web UI for
a given project.

* The repository contains code meant to be dynamically loaded by
  OpenStack Horizon to provide UI to specific projects.

.. _`type-library`:

library
=======

This deliverable type indicates that a project is a library,
middleware, or other piece of software that is used to build
another project and does not, by itself, provide a long-running
service or stand-alone tool.

* The repository contains software used as a library for the loose and
  commonly-understood definition of "library".

.. _`type-client-library`:

client-library
==============

This deliverable type indicates that a project is a library containing
a client for an OpenStack service that is intended to be consumed by
other OpenStack services (so not a general-purpose user client such as
``shade``).

.. _`type-service`:

service
=======

This deliverable type indicates that a project provides a user-facing
long-running service with a REST API.

.. _`type-other`:

other
=====

Deliverables without a more specific categorization are listed as
``other``.
