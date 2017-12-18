================
 Release Models
================

Development in OpenStack is organized around 6-month cycles (like
"kilo").  At the end of every 6-month cycle a number of projects
release at the same time, providing a convenient reference point for
downstream teams (stable branch maintenance, vulnerability management)
and downstream users (in particular packagers of OpenStack
distributions).

This "final" release may be the only release of the development cycle,
in which case the project publishes intermediary "development
milestones" on a time-based schedule during the cycle. Or the project
may release more often and make intermediary releases in the middle of
the cycle. Other projects trail the main release deadline, waiting for
the final releases of components on which they rely.

A given deliverable can't have more than one model. It therefore must
choose between one of the following models. A number of rules apply
based on what the deliverable is and which bucket of the OpenStack map
it falls in:

* Components appearing in the *openstack* bucket in the `OpenStack map`_
  form the main components of an OpenStack cloud, and therefore should follow
  the release cycle. They need to pick between `cycle-with-milestones`_
  or `cycle-with-intermediary`_ models.
* Only deployment or lifecycle-management components are allowed to trail
  the cycle. Therefore only components appearing in the
  *openstack-lifecyclemanagement* bucket on the `OpenStack map`_ are
  allowed to use the `cycle-trailing`_ model.
* Libraries cannot use RCs or trail the release. They need to pick between
  `cycle-with-intermediary`_ and `independent`_ release models based on how
  much they are tied to OpenStack or more generally-useful.

.. _`OpenStack map`: https://www.openstack.org/openstack-map

.. _cycle-with-milestones:

cycle-with-milestones
=====================

The "cycle-with-milestones" model describes projects that produce a
single release at the end of the cycle, with development milestones
published at predetermined times in the cycle schedule.

* "cycle-with-milestones" projects commit to publish development
  milestones following a predetermined schedule published by the Release
  Management team before the start of the 6-month cycle.
* "cycle-with-milestones" projects commit to produce a release to
  match the end of the 6-month development cycle.
* Release tags for deliverables using this tag are reviewed and
  applied by the Release Management team.

.. _cycle-with-intermediary:

cycle-with-intermediary
=======================

The "cycle-with-intermediary" model describes projects that produce
multiple full releases during the development cycle, with a final
release to match the end of the cycle.

* "cycle-with-intermediary" projects commit to produce a
  release near the end of the 6-month development cycle to be used
  with projects using the other cycle-based release models that are
  required to produce a release at that time.
* Release tags for deliverables using this tag are reviewed and
  applied by the Release Management team.

.. _cycle-trailing:

cycle-trailing
==============

The "cycle-trailing" model describes projects that follow the release
cycle, but because they rely on the other projects being completed may
not always publish their final release at the same time as those
projects.

* "cycle-trailing" projects commit to produce a release no later than
  2 weeks after the end of the 6-month development cycle.
* Within the cycle, projects using this release model will produce
  intermediate or milestone releases (adhering to the same regular
  deadlines) leading up to their final release.
* Release tags for deliverables using this tag are reviewed and
  applied by the Release Management team.

.. _independent:

independent
===========

Some projects opt to completely bypass the 6-month cycle and release
independently. For example, that is the case of projects that support
the development infrastructure. The "independent" model describes such
projects.

* "independent" projects produce releases from time to time.
* Release tags for deliverables using this tag are managed without
  oversight from the Release Management team.

.. _untagged:

untagged
========

Some CI tools are used only from source and never tag releases, but
need to create stable branches.
