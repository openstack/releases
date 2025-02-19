=============================
2025.1 Epoxy Release Schedule
=============================

.. note::

   Deadlines are generally the Thursday of the week on which they are noted
   below. Exceptions to this policy will be explicitly mentioned in the event
   description.

2 October, 2024 - 2 April, 2025 (26 weeks)

.. datatemplate::
   :source: schedule.yaml
   :template: schedule_table.tmpl

.. ics::
   :source: schedule.yaml
   :name: Epoxy

`Subscribe to iCalendar file <schedule.ics>`_

Cross-project events
====================

.. _e-vptg:

PTG (virtual)
-------------

From October 21 to 25 we'll have a virtual PTG to plan the Epoxy
release schedule.

.. _e-1:

Epoxy-1 milestone
-----------------

November 14, 2024 is the Epoxy-1 milestone. See project-specific notes
for relevant deadlines.

.. _e-cycle-trail:

2024.2 Dalmatian Cycle-Trailing Release Deadline
------------------------------------------------

All projects following the cycle-trailing release model must release
their 2024.2 Dalmatian deliverables by December 5, 2024.

.. _e-2:

Epoxy-2 milestone
-----------------

January 9, 2025 is the Epoxy-2 milestone. See project-specific notes
for relevant deadlines.

.. _e-mf:

Membership Freeze
-----------------

Projects must participate in at least two milestones in order to be considered
part of the release. Projects made official after the second milestone, or
which fail to produce milestone releases for at least one of the first and
second milestones as well as the third milestone, are therefore not considered
part of the release for the cycle. This does not apply to cycle-trailing
packaging / lifecycle management projects.

.. _e-extra-acs:

Extra-AC freeze
---------------

All contributions to OpenStack are valuable, but some are not expressed as
Gerrit code changes. That allow teams to list active contributors to their
projects and who do not have a code contribution this cycle, and therefore won't
automatically be considered an Active Contributor and allowed
to vote. This is done by adding extra-acs to
https://opendev.org/openstack/governance/src/branch/master/reference/projects.yaml
before the Extra-AC freeze date.

.. _e-final-lib:

Final release for non-client libraries
--------------------------------------

Libraries that are not client libraries (Oslo and others) should issue their
final release during this week. That allows to give time for last-minute
changes before feature freeze.

.. _e-3:

Epoxy-3 milestone
-----------------

February 27, 2025 is the Epoxy-3 milestone. See project-specific notes
for relevant deadlines.

.. _e-ff:

Feature freeze
--------------

The Epoxy-3 milestone marks feature freeze for projects following the
`release:cycle-with-rc`_ model. No featureful patch should be landed
after this point. Exceptions may be granted by the project PTL.

.. _release:cycle-with-rc: https://releases.openstack.org/reference/release_models.html#cycle-with-rc

.. _e-final-clientlib:

Final release for client libraries
----------------------------------

Client libraries should issue their final release during this week, to match
feature freeze.

.. _e-soft-sf:

Soft StringFreeze
-----------------

You are no longer allowed to accept proposed changes containing modifications
in user-facing strings. Such changes should be rejected by the review team and
postponed until the next series development opens (which should happen when RC1
is published).

.. _e-rf:

Requirements freeze
-------------------

After the Epoxy-3 milestone, only critical requirements and constraints
changes will be allowed. Freezing our requirements list gives packagers
downstream an opportunity to catch up and prepare packages for everything
necessary for distributions of the upcoming release. The requirements remain
frozen until the stable branches are created, with the release candidates.

.. _e-rc1:

RC1 target week
---------------

The week of March 10, 2025 is the target date for projects following the
`release:cycle-with-rc`_ model to issue their first release candidate.

.. _e-hard-sf:

Hard StringFreeze
-----------------

This happens when the RC1 for the project is tagged. At this point, ideally
no strings are changed (or added, or removed), to give translators time to
finish up their efforts.

.. _e-finalrc:

Final RCs and intermediary releases
-----------------------------------

The week of March 24, 2025 is the last week to issue release
candidates or intermediary releases before release week. During release week,
only final-release-critical releases will be accepted (at the discretion of
the release team).

.. _e-final:

Epoxy release
-------------

The Epoxy coordinated release will happen on Wednesday, April 2, 2025.

.. _e-cycle-highlights:

Cycle Highlights
----------------

Cycle highlights need to be added to the release deliverables after the
feature freeze to be included in any marketing release messaging.
Highlights may be added after this point, but they will likely only be
useful for historical purposes.

See the `Project Team Guide`_ for more details and instructions on adding
these highlights.

For examples of previous release highlights:
`Zed Highlights <https://releases.openstack.org/zed/highlights.html>`_.
`2023.1 Antelope Highlights <https://releases.openstack.org/antelope/highlights.html>`_.
`2023.2 Bobcat Highlights <https://releases.openstack.org/bobcat/highlights.html>`_.
`2024.1 Caracal Highlights <https://releases.openstack.org/caracal/highlights.html>`_.

.. _Project Team Guide: https://docs.openstack.org/project-team-guide/release-management.html#cycle-highlights


Project-specific events
=======================

Oslo
----

.. _e-oslo-feature-freeze:

Oslo Feature Freeze
^^^^^^^^^^^^^^^^^^^

All new Oslo features must be proposed and substantially complete, with unit
tests by the end of the week.


Manila
------

.. _e-manila-spec-freeze:

Manila Spec Freeze
^^^^^^^^^^^^^^^^^^

All Manila specs targeted to 2025.1 Epoxy must be approved by the end of
the week.

.. _e-manila-new-driver-deadline:

Manila New Driver Deadline
^^^^^^^^^^^^^^^^^^^^^^^^^^

By the end of the week all new backend drivers for Manila must be substantially
complete, with unit tests, and passing 3rd party CI. Drivers do not have to
actually merge until feature freeze.

.. _e-manila-fpfreeze:

Manila Feature Proposal Freeze
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All new Manila features must be proposed and substantially completed, with
unit, functional and integration tests by the end of the week. Collaborative
review sessions must be proposed at this timeline, in order to speed up the
review process.

.. _e-manila-bugsquash:

Manila Bugsquash
^^^^^^^^^^^^^^^^

Manila community event promoted in order to fast-track the closure of bugs.

.. _e-manila-mid-cycle:

Manila Mid Cycle
^^^^^^^^^^^^^^^^

Manila community mid cycle checkpoint on features and deliverables planned
for the release.


Nova
----

.. _e-nova-spec-review-day:

Nova Spec Review Day
^^^^^^^^^^^^^^^^^^^^

On 12 Nov 2024 and 11 Dec 2024, Nova specifications targeting 2025.1 Epoxy
implementation will be prioritized for reviews by the Nova core team.


.. _e-nova-spec-soft-freeze:

Nova Spec Soft Freeze
^^^^^^^^^^^^^^^^^^^^^

After 12 December 2024 (23:59 UTC), no new specs will be accepted.

.. _e-nova-spec-freeze:

Nova Spec Freeze
^^^^^^^^^^^^^^^^

All Nova Specs for features to be implemented in 2025.1 Epoxy must be
approved by 9 January 2025 (23:59 UTC).

.. _e-nova-review-day:

Nova Implementation Review Day
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

On 9 January 2025, Nova prioritized code changes will be reviewed by the Nova
core team.


OpenStackSDK
------------

.. _e-openstackclient-freeze:

python-openstackclient Feature Freeze
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All new python-openstackclient features should be proposed and completed,
with unit tests by the end of the week. Support for new microversions may be
added after this date, but no breaking changes will be permitted.


2025.2 TC and PTL Elections
===========================

.. _f-election-email-deadline:

2025.2 Election Email Deadline
------------------------------
Contributors that will be in the electorate for the upcoming election
should confirm their gerrit email addresses by this date (February 19th, 2025
at 00:00 UTC). Electorate rolls are generated after this date and ballots will
be sent to the listed gerrit email address.

.. _f-election-nominations:

2025.2 Election Nomination Begins
---------------------------------
Candidates interested in serving for the next calendar year (TC), or
development cycle (PTL) should announce their candidacies and platforms during
this week.  Please see the `Election site`_ for specific timing information.

.. _f-election-campaigning:

2025.2 Election Campaigning Begins
----------------------------------
The electorate has time to ask candidates questions about their platforms
and debate topics before polling begins.  Please see the `Election site`_ for
specific timing information.

.. _f-election-voting:

2025.2 Election Polling Begins
------------------------------
Election polling for open seats on the TC and any required PTL elections.
Please see the `Election site`_ for specific timing information.

.. _f-election-close:

2025.2 Election Polling Ends
----------------------------
All polls close in the 2025.2 Election and results announced.  Please see the
`Election site`_ for specific timing information.

.. _Election site: https://governance.openstack.org/election/
