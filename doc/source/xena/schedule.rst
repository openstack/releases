=====================
Xena Release Schedule
=====================

.. note::

   Deadlines are generally the Thursday of the week on which they are noted
   below. Exceptions to this policy will be explicitly mentioned in the event
   description.

19 April 2021 - 06 October 2021 (25 weeks)

.. datatemplate::
   :source: schedule.yaml
   :template: schedule_table.tmpl

.. ics::
   :source: schedule.yaml
   :name: Xena

`Subscribe to iCalendar file <schedule.ics>`_

Cross-project events
====================

.. _x-goals-research:

Xena Goals Research
-------------------

Pre-cycle planning and investigation into `the community-wide goals
for Xena
<https://governance.openstack.org/tc/goals/selected/xena/index.html>`__.

.. _x-ptg:

Virtual PTG
-----------

.. This needs to be added to the schedule once we know when the event will be

A virtual PTG will be held during this week. The Project Teams Gathering
provides and opportunity for teams to collaborate
and plan, and discuss requirements for future releases.

.. _x-1:

Xena-1 milestone
----------------

27 May, 2021 is the Xena-1 milestone. See project-specific notes for
relevant deadlines.

.. _x-cycle-trail:

Wallaby Cycle-Trailing Release Deadline
---------------------------------------

All projects following the cycle-trailing release model must release
their Wallaby deliverables by 02 July, 2021.

.. _x-2:

Xena-2 milestone
----------------

15 July, 2021 is the Xena-2 milestone. See project-specific notes for
relevant deadlines.

.. _x-mf:

Membership Freeze
-----------------

Projects must participate in at least two milestones in order to be considered
part of the release. Projects made official after the second milestone, or
which fail to produce milestone releases for at least one of the first and
second milestones as well as the third milestone, are therefore not considered
part of the release for the cycle. This does not apply to cycle-trailing
packaging / lifecycle management projects.

.. _x-final-lib:

Final release for non-client libraries
--------------------------------------

Libraries that are not client libraries (Oslo and others) should issue their
final release during this week. That allows to give time for last-minute
changes before feature freeze.

.. _x-3:

Xena-3 milestone
----------------

02 September, 2021 is the Xena-3 milestone. See project-specific notes for
relevant deadlines.

.. _x-ff:

Feature freeze
--------------

The Xena-3 milestone marks feature freeze for projects following the
`release:cycle-with-rc`_ model. No featureful patch should be landed
after this point. Exceptions may be granted by the project PTL.

.. _release:cycle-with-rc: https://releases.openstack.org/reference/release_models.html#cycle-with-rc

.. _x-final-clientlib:

Final release for client libraries
----------------------------------

Client libraries should issue their final release during this week, to match
feature freeze.

.. _x-soft-sf:

Soft StringFreeze
-----------------

You are no longer allowed to accept proposed changes containing modifications
in user-facing strings. Such changes should be rejected by the review team and
postponed until the next series development opens (which should happen when RC1
is published).

.. _x-rf:

Requirements freeze
-------------------

After the Xena-3 milestone, only critical requirements and constraints
changes will be allowed. Freezing our requirements list gives packagers
downstream an opportunity to catch up and prepare packages for everything
necessary for distributions of the upcoming release. The requirements remain
frozen until the stable branches are created, with the release candidates.

.. _x-goals-complete:

Xena Community Goals Completed
------------------------------

Teams should prepare their documentation for completing `the
community-wide goals for Xena
<https://governance.openstack.org/tc/goals/selected/xena/index.html>`__.

.. _x-rc1:

RC1 target week
---------------

The week of 13 September, 2021 is the target date for projects following the
`release:cycle-with-rc`_ model to issue their first release candidate.

.. _x-hard-sf:

Hard StringFreeze
-----------------

This happens when the RC1 for the project is tagged. At this point, ideally
no strings are changed (or added, or removed), to give translators time to
finish up their efforts.

.. _x-finalrc:

Final RCs and intermediary releases
-----------------------------------

The week of 27 September, 2021 is the last week to issue release candidates or
intermediary releases before release week. During release week, only
final-release-critical releases will be accepted (at the discretion of the
release team).

.. _x-final:

Xena release
------------

The Xena coordinated release will happen on Wednesday, 06 October, 2021.

.. _x-summit:

Open Infrastructure Summit
--------------------------

The Open Infrastructure Summit is expected to take place some time in October.
Exact event dates are yet to be determined.

.. _x-cycle-highlights:

Cycle Highlights
----------------

Cycle highlights need to be added to the release deliverables by feature
freeze to be included in any marketing release messaging.
Highlights may be added after this point, but they will likely only be
useful for historical purposes.

See the `Project Team Guide`_ for more details and instructions on adding
these highlights.

For examples of previous release highlights:
`Stein Highlights <https://releases.openstack.org/stein/highlights.html>`_,
`Train Highlights <https://releases.openstack.org/train/highlights.html>`_,
`Ussuri Highlights <https://releases.openstack.org/ussuri/highlights.html>`_,
`Victoria Highlights <https://releases.openstack.org/victoria/highlights.html>`_.
`Wallaby Highlights <https://releases.openstack.org/wallaby/highlights.html>`_.

.. _Project Team Guide: https://docs.openstack.org/project-team-guide/release-management.html#cycle-highlights

Project-specific events
=======================

Oslo
----

.. _x-oslo-feature-freeze:

Oslo Feature Freeze
^^^^^^^^^^^^^^^^^^^

All new Oslo features must be proposed and substantially complete, with unit
tests by the end of the week.
