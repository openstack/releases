========================
Wallaby Release Schedule
========================

.. note::

   Deadlines are generally the Thursday of the week on which they are noted
   below. Exceptions to this policy will be explicitly mentioned in the event
   description.

19 October 2020 - 14 April 2021 (26 weeks)

.. datatemplate::
   :source: schedule.yaml
   :template: schedule_table.tmpl

.. ics::
   :source: schedule.yaml
   :name: Wallaby

`Subscribe to iCalendar file <schedule.ics>`_

Cross-project events
====================

.. _w-goals-research:

Wallaby Goals Research
----------------------

Pre-cycle planning and investigation into `the community-wide goals
for Wallaby
<https://governance.openstack.org/tc/goals/selected/wallaby/index.html>`__.

.. _w-ptg:

Virtual PTG
-----------

.. This needs to be added to the schedule once we know when the event will be

A virtual PTG will be held during this week. The Project Teams Gathering
provides and opportunity for teams to collaborate
and plan, and discuss requirements for future releases.

.. _w-1:

Wallaby-1 milestone
-------------------

3 December, 2020 is the Wallaby-1 milestone. See project-specific notes for
relevant deadlines.

.. _w-cycle-trail:

Victoria Cycle-Trailing Release Deadline
----------------------------------------

All projects following the cycle-trailing release model must release
their Victoria deliverables by 14 January, 2021.

.. _w-2:

Wallaby-2 milestone
-------------------

21 January, 2021 is the Wallaby-2 milestone. See project-specific notes for
relevant deadlines.

.. _w-mf:

Membership Freeze
-----------------

Projects must participate in at least two milestones in order to be considered
part of the release. Projects made official after the second milestone, or
which fail to produce milestone releases for at least one of the first and
second milestones as well as the third milestone, are therefore not considered
part of the release for the cycle. This does not apply to cycle-trailing
packaging / lifecycle management projects.

.. _w-final-lib:

Final release for non-client libraries
--------------------------------------

Libraries that are not client libraries (Oslo and others) should issue their
final release during this week. That allows to give time for last-minute
changes before feature freeze.

.. _w-3:

Wallaby-3 milestone
-------------------

11 March, 2021 is the Wallaby-3 milestone. See project-specific notes for
relevant deadlines.

.. _w-ff:

Feature freeze
--------------

The Wallaby-3 milestone marks feature freeze for projects following the
`release:cycle-with-rc`_ model. No featureful patch should be landed
after this point. Exceptions may be granted by the project PTL.

.. _release:cycle-with-rc: https://releases.openstack.org/reference/release_models.html#cycle-with-rc

.. _w-final-clientlib:

Final release for client libraries
----------------------------------

Client libraries should issue their final release during this week, to match
feature freeze.

.. _w-soft-sf:

Soft StringFreeze
-----------------

You are no longer allowed to accept proposed changes containing modifications
in user-facing strings. Such changes should be rejected by the review team and
postponed until the next series development opens (which should happen when RC1
is published).

.. _w-rf:

Requirements freeze
-------------------

After the Wallaby-3 milestone, only critical requirements and constraints
changes will be allowed. Freezing our requirements list gives packagers
downstream an opportunity to catch up and prepare packages for everything
necessary for distributions of the upcoming release. The requirements remain
frozen until the stable branches are created, with the release candidates.

.. _w-goals-complete:

Wallaby Community Goals Completed
---------------------------------

Teams should prepare their documentation for completing `the
community-wide goals for Wallaby
<https://governance.openstack.org/tc/goals/selected/wallaby/index.html>`__.

.. _w-rc1:

RC1 target week
---------------

The week of 22 March, 2021 is the target date for projects following the
`release:cycle-with-rc`_ model to issue their first release candidate.

.. _w-hard-sf:

Hard StringFreeze
-----------------

This happens when the RC1 for the project is tagged. At this point, ideally
no strings are changed (or added, or removed), to give translators time to
finish up their efforts.

.. _w-finalrc:

Final RCs and intermediary releases
-----------------------------------

The week of 5 April, 2021 is the last week to issue release candidates or
intermediary releases before release week. During release week, only
final-release-critical releases will be accepted (at the discretion of the
release team).

.. _w-final:

Wallaby release
---------------

The Wallaby coordinated release will happen on Wednesday, 14 April, 2021.

.. _w-summit:

Open Infrastructure Summit
--------------------------

The Open Infrastructure Summit is expected to take place some time in May.
Exact event dates are yet to be determined.

Project-specific events
=======================
