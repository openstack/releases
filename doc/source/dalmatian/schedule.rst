=================================
2024.2 Dalmatian Release Schedule
=================================

.. note::

   Deadlines are generally the Thursday of the week on which they are noted
   below. Exceptions to this policy will be explicitly mentioned in the event
   description.

April 3, 2024 - October 2, 2024 (26 weeks)

.. datatemplate::
   :source: schedule.yaml
   :template: schedule_table.tmpl

.. ics::
   :source: schedule.yaml
   :name: Dalmatian

`Subscribe to iCalendar file <schedule.ics>`_

Cross-project events
====================

.. _d-vptg:

PTG (virtual)
-------------

From April 8 to April 12 we'll have a virtual PTG to plan the Dalmatian
release schedule.

.. _d-1:

Dalmatian-1 milestone
---------------------

30 May, 2024 is the Dalmatian-1 milestone. See project-specific notes
for relevant deadlines.

.. _d-cycle-trail:

2024.1 Caracal Cycle-Trailing Release Deadline
----------------------------------------------

All projects following the cycle-trailing release model must release
their 2024.1 Caracal deliverables by 13 June, 2024.

.. _d-2:

Dalmatian-2 milestone
---------------------

18 July, 2024 is the Dalmatian-2 milestone. See project-specific notes
for relevant deadlines.

.. _d-mf:

Membership Freeze
-----------------

Projects must participate in at least two milestones in order to be considered
part of the release. Projects made official after the second milestone, or
which fail to produce milestone releases for at least one of the first and
second milestones as well as the third milestone, are therefore not considered
part of the release for the cycle. This does not apply to cycle-trailing
packaging / lifecycle management projects.

.. _d-extra-acs:

Extra-AC freeze
---------------

All contributions to OpenStack are valuable, but some are not expressed as
Gerrit code changes. That allow teams to list active contributors to their
projects and who do not have a code contribution this cycle, and therefore won't
automatically be considered an Active Contributor and allowed
to vote. This is done by adding extra-acs to
https://opendev.org/openstack/governance/src/branch/master/reference/projects.yaml
before the Extra-AC freeze date.

.. _d-final-lib:

Final release for non-client libraries
--------------------------------------

Libraries that are not client libraries (Oslo and others) should issue their
final release during this week. That allows to give time for last-minute
changes before feature freeze.

.. _d-3:

Dalmatian-3 milestone
---------------------

29 August, 2024 is the Dalmatian-3 milestone. See project-specific notes
for relevant deadlines.

.. _d-ff:

Feature freeze
--------------

The Dalmatian-3 milestone marks feature freeze for projects following the
`release:cycle-with-rc`_ model. No featureful patch should be landed
after this point. Exceptions may be granted by the project PTL.

.. _release:cycle-with-rc: https://releases.openstack.org/reference/release_models.html#cycle-with-rc

.. _d-final-clientlib:

Final release for client libraries
----------------------------------

Client libraries should issue their final release during this week, to match
feature freeze.

.. _d-soft-sf:

Soft StringFreeze
-----------------

You are no longer allowed to accept proposed changes containing modifications
in user-facing strings. Such changes should be rejected by the review team and
postponed until the next series development opens (which should happen when RC1
is published).

.. _d-rf:

Requirements freeze
-------------------

After the Dalmatian-3 milestone, only critical requirements and constraints
changes will be allowed. Freezing our requirements list gives packagers
downstream an opportunity to catch up and prepare packages for everything
necessary for distributions of the upcoming release. The requirements remain
frozen until the stable branches are created, with the release candidates.

.. _d-rc1:

RC1 target week
---------------

The week of 9 September, 2024 is the target date for projects following the
`release:cycle-with-rc`_ model to issue their first release candidate.

.. _d-hard-sf:

Hard StringFreeze
-----------------

This happens when the RC1 for the project is tagged. At this point, ideally
no strings are changed (or added, or removed), to give translators time to
finish up their efforts.

.. _d-finalrc:

Final RCs and intermediary releases
-----------------------------------

The week of 23 September, 2024 is the last week to issue release
candidates or intermediary releases before release week. During release week,
only final-release-critical releases will be accepted (at the discretion of
the release team).

.. _d-final:

Dalmatian release
-----------------

The Dalmatian coordinated release will happen on Wednesday, 2 October, 2024.

.. _d-cycle-highlights:

Cycle Highlights
----------------

Cycle highlights need to be added to the release deliverables after the
feature freeze to be included in any marketing release messaging.
Highlights may be added after this point, but they will likely only be
useful for historical purposes.

See the `Project Team Guide`_ for more details and instructions on adding
these highlights.

For examples of previous release highlights:
`Stein Highlights <https://releases.openstack.org/stein/highlights.html>`_,
`Train Highlights <https://releases.openstack.org/train/highlights.html>`_,
`Ussuri Highlights <https://releases.openstack.org/ussuri/highlights.html>`_,
`Victoria Highlights <https://releases.openstack.org/victoria/highlights.html>`_,
`Wallaby Highlights <https://releases.openstack.org/wallaby/highlights.html>`_,
`Xena Highlights <https://releases.openstack.org/xena/highlights.html>`_,
`Yoga Highlights <https://releases.openstack.org/yoga/highlights.html>`_,
`Zed Highlights <https://releases.openstack.org/zed/highlights.html>`_.
`2023.1 Antelope Highlights <https://releases.openstack.org/antelope/highlights.html>`_.
`2023.2 Bobcat Highlights <https://releases.openstack.org/bobcat/highlights.html>`_.
`2024.1 Caracal Highlights <https://releases.openstack.org/caracal/highlights.html>`_.

.. _Project Team Guide: https://docs.openstack.org/project-team-guide/release-management.html#cycle-highlights


Project-specific events
=======================

