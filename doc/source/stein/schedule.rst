=======================
 Stein Release Schedule
=======================

3 September 2018 - 8 April 2019 (32 weeks)

.. datatemplate::
   :source: schedule.yaml
   :template: schedule_table.tmpl

.. ics::
   :source: schedule.yaml
   :name: Stein

`Subscribe to iCalendar file <schedule.ics>`__

.. note::

   With the exception of the final release date and cycle-trailing release
   date, deadlines are generally the Thursday of the week on which they are
   noted above. Exceptions to this policy will be explicitly mentioned in the
   event description.

Cross-project events
====================

.. _s-goals-research:

Stein Goals Research
--------------------

Pre-cycle planning and investigation into `the community-wide goals
for Stein <https://governance.openstack.org/tc/goals/stein/index.html>`__.

.. _s-ptg:

Stein Project Team Gathering (PTG)
----------------------------------

`Project team gathering <https://www.openstack.org/ptg>`__ for the Stein
cycle 10 - 14 September in Denver, Colorado, USA.

.. _s-1:

Stein-1 milestone
-----------------

25 October 2018 is the Stein-1 milestone window for projects following the
`release:cycle-with-milestones`_ model.

.. _release:cycle-with-milestones: https://releases.openstack.org/reference/release_models.html#cycle-with-milestones

.. _s-goals-ack:

Stein Community Goals Acknowledgement
-------------------------------------

Teams should prepare their acknowledgement of `the community-wide
goals for
<https://governance.openstack.org/tc/goals/stein/index.html>`__.

.. _s-summit:

OpenStack Summit
----------------

The OpenStack Summit happens during this week in Berlin, Germany. It will
include a "Forum" in which people from all parts of our community will gather
to give feedback on the last release (Rocky) and discuss requirements for the
next development cycle (Stein).

.. _s-2:

Stein-2 milestone
-----------------

10 January 2019 is the Stein-2 milestone window for projects following the
`release:cycle-with-milestones`_ model.

.. _s-final-lib:

Final release for non-client libraries
--------------------------------------

Libraries that are not client libraries (Oslo and others) should issue their
final release during this week. That allows to give time for last-minute
changes before feature freeze.

.. _s-3:

Stein-3 milestone
-----------------

28 February 2019 is the Stein-3 milestone window for projects following the
`release:cycle-with-milestones`_ model.

.. _s-goals-complete:

Stein Community Goals Completed
-------------------------------

Teams should prepare their documentation for completing `the
community-wide goals for Stein
<https://governance.openstack.org/tc/goals/stein/index.html>`__.

.. _s-ff:

Feature freeze
--------------

The Stein-3 milestone marks feature freeze for projects following the
`release:cycle-with-milestones`_ model. No featureful patch should be landed
after this point. Exceptions may be granted by the project PTL.

.. _s-rf:

Requirements freeze
-------------------

After the Stein-3 milestone, only critical requirements and constraints changes
will be allowed. Freezing our requirements list gives packagers downstream an
opportunity to catch up and prepare packages for everything necessary for
distributions of the upcoming release. The requirements remain frozen until the
stable branches are created, with the release candidates.

.. _s-final-clientlib:

Final release for client libraries
----------------------------------

Client libraries should issue their final release during this week, to match
feature freeze.

.. _s-soft-sf:

Soft StringFreeze
-----------------

You are no longer allowed to accept proposed changes containing modifications
in user-facing strings. Such changes should be rejected by the review team and
postponed until the next series development opens (which should happen when RC1
is published).

.. _s-mf:

Membership Freeze
-----------------

Projects must participate in at least two milestones in order to be considered
part of the release. Projects made official after the second milestone, or
which fail to produce milestone releases for at least one of the first and
second milestones as well as the third milestone, are therefore not considered
part of the release for the cycle. This does not apply to cycle-trailing
packaging / lifecycle management projects.

.. _s-rc1:

RC1 target week
---------------

This week is the target for projects following the
`release:cycle-with-milestones`_ model to issue their first release candidate,
with a deadline of 21 March 2019.

.. _s-hard-sf:

Hard StringFreeze
-----------------

This happens when the RC1 for the project is tagged. At this point, ideally
no strings are changed (or added, or removed), to give translator time to
finish up their efforts.

.. _s-finalrc:

Final RCs and intermediary releases
-----------------------------------

The week of 1 April 2019 is the last week to issue release candidates or
intermediary releases before release week. During release week, only
final-release-critical releases will be accepted (at the discretion of the
release team).

.. _s-release:

Stein release
-------------

The Stein coordinated release will happen on 11 April 2019.

.. _s-trailing-release:

Stein cycle-trailing release deadline
-------------------------------------

The release deadline for projects using the release:cycle-trailing model that
follow the main release cycle is set to 13 June, 2019.

Project-specific events
=======================

PTL Elections
-------------

