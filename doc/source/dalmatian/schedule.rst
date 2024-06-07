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

May 16, 2024 is the Dalmatian-1 milestone. See project-specific notes
for relevant deadlines.

.. _d-cycle-trail:

2024.1 Caracal Cycle-Trailing Release Deadline
----------------------------------------------

All projects following the cycle-trailing release model must release
their 2024.1 Caracal deliverables by June 6, 2024.

.. _d-2:

Dalmatian-2 milestone
---------------------

July 4, 2024 is the Dalmatian-2 milestone. See project-specific notes
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

August 29, 2024 is the Dalmatian-3 milestone. See project-specific notes
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

The week of September 9, 2024 is the target date for projects following the
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

The week of September 23, 2024 is the last week to issue release
candidates or intermediary releases before release week. During release week,
only final-release-critical releases will be accepted (at the discretion of
the release team).

.. _d-final:

Dalmatian release
-----------------

The Dalmatian coordinated release will happen on Wednesday, October 2, 2024.

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

Cinder
------

.. _d-cinder-mid-cycle-ptg-1:

Cinder Mid Cycle PTG - 1
^^^^^^^^^^^^^^^^^^^^^^^^

We will be conducting a mid-cycle PTG on 12 June, 2024 (Wednesday) which
is a continuation of 2024.2 Dalmatian PTG to track progress and discuss
new topics in a similar manner as of PTG.  We will start at 1400 UTC and
conclude at 1600 UTC.

.. _d-cinder-spec-freeze:

Cinder Spec Freeze
^^^^^^^^^^^^^^^^^^

All Cinder Specs for features to be implemented in 2024.2 Dalmatian must
be approved by Friday 21 June 2024 (23:59 UTC).

.. _d-cinder-driver-deadline:

Cinder New Driver Merge Deadline
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The deadline for merging a new backend driver to Cinder for the 2024.2
Dalmatian release is Friday 5 July 2024 (20:00 UTC).  New drivers must
be (a) code complete including unit tests, (b) merged into the code
repository, and (c) must have a 3rd Party CI running reliably.  (Note
that because of where some holidays fall this cycle, this is later than
the usual Milestone-2 deadline.)

.. _d-cinder-target-driver-deadline:

Cinder New Target Driver Merge Deadline
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The deadline for merging a new target driver to Cinder for the 2024.2
Dalmatian release is Friday 5 July 2024 (20:00 UTC).  New target drivers
must be (a) code complete including unit tests, (b) merged into the code
repository, and (c) must have a 3rd Party CI running reliably.

.. _d-cinder-feature-checkpoint:

Cinder New Feature Status Checkpoint
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If your new Cinder feature requires client support, keep in mind that the final
release for client libraries is in four weeks.  Thus your Cinder feature
should be substantially complete with unit tests by this time so that any
client changes can be reviewed, tested, and merged before 26 August 2024.

.. _d-cinder-driver-features-declaration:

Cinder Driver Features Declaration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

New features added to Cinder drivers must be merged at the time of the
OpenStack-wide Feature Freeze, which is coming up in two weeks.  Before
the Cinder meeting this week, you should post a blueprint in Launchpad listing
the Gerrit reviews of features you'd like to land in 2024.2 Dalmatian.  (You
can look among the 2023.2 and 2024.1 blueprints for examples; contact the PTL
if you have any questions.)  This will help the team prioritize reviews and
give you candid early feedback on whether the features look ready.

.. _d-cinder-mid-cycle-ptg-2:

Cinder Mid Cycle PTG - 2
^^^^^^^^^^^^^^^^^^^^^^^^

We will be conducting Midcycle-2 PTG on 14th August, 2024 (Wednesday) which
is a continuation of 2024.2 Dalmatian Midcycle-1 PTG to track progress and
discuss new topics in a similar manner as of Midcycle-1 PTG.  We will start
at 1400 UTC and conclude at 1600 UTC.

.. _d-cinder-ci-checkpoint:

Cinder 3rd Party CI Compliance Checkpoint
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This is a reminder that in order for a Cinder driver to be considered
'supported' in the 2024.2 Dalmatian release, its third party CI must be
running properly when the Cinder team does a final compliance check around the
time of the third milestone.  See the `Driver Compliance
<https://docs.openstack.org/cinder/latest/drivers-all-about.html#driver-compliance>`_
section of the Cinder Documentation for details.

Manila
------

.. _d-manila-spec-freeze:

Manila Spec Freeze
^^^^^^^^^^^^^^^^^^

All Manila specs targeted to 2024.2 Dalmatian must be approved by the end of
the week.

.. _d-manila-new-driver-deadline:

Manila New Driver Deadline
^^^^^^^^^^^^^^^^^^^^^^^^^^

By the end of the week all new backend drivers for Manila must be substantially
complete, with unit tests, and passing 3rd party CI. Drivers do not have to
actually merge until feature freeze.

.. _d-manila-fpfreeze:

Manila Feature Proposal Freeze
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All new Manila features must be proposed and substantially completed, with
unit, functional and integration tests by the end of the week. Collaborative
review sessions must be proposed at this timeline, in order to speed up the
review process.

.. _d-manila-bugsquash:

Manila Bugsquash
^^^^^^^^^^^^^^^^

Manila community event promoted in order to fast-track the closure of bugs.


Nova
----

.. _d-nova-spec-review-day:

Nova Spec Review Day
^^^^^^^^^^^^^^^^^^^^

On 14 May 2024 and 2 July 2024, Nova specifications targeting 2024.2 Dalmatian
implementation will be prioritized for reviews by the Nova core team.


.. _d-nova-spec-freeze:

Nova Spec Freeze
^^^^^^^^^^^^^^^^

All Nova Specs for features to be implemented in 2024.2 Dalmatian must be
approved by 18 July 2024 (23:59 UTC).

.. _d-nova-review-day:

Nova Implementation Review Day
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

On 23 July 2024, Nova "quickwin" patches (small code changes) will be reviewed
by the Nova core team.


2025.1 TC and PTL Elections
===========================

.. _e-election-nominations:

2025.1 Election Nominations Open
--------------------------------
Candidates interested in serving for the next calendar year (TC), or
development cycle (PTL) should announce their candidacies and platforms during
this two week window. The nomination period runs between 2024-08-14 23:45 UTC
and 2024-08-28 23:45 UTC. Please see the `Election site`_ for
more information.

.. _e-election-email-deadline:

2025.1 Election Email Deadline
------------------------------
Contributors that will be in the electorate for the upcoming election
should confirm their gerrit email addresses by 2024-08-28 00:00 UTC.
Electorate rolls are generated after this date and ballots will
be sent to the listed preferred gerrit email address.

.. _e-election-campaigning:

2025.1 Election Campaigning Week
--------------------------------
Election Campaigning window is between 2024-08-28 23:45 UTC and 2024-09-04
23:45 UTC. The electorate can use this time to ask candidates questions about
their platforms and debate topics before polling begins. Please see the
`Election site`_ for specific timing information.

.. _e-election-voting:

2025.1 Election Polling Open
----------------------------
Election polling for open seats on the TC and any required PTL elections
begins at 2024-09-04 23:45 UTC. Please see the `Election site`_ for
more information.

.. _e-election-close:

2025.1 Election Polling End
---------------------------
All polls close in the 2025.1 Election at 2024-09-18 23:45 UTC and
results are announced. Please see the `Election site`_ for more information.

.. _Election site: https://governance.openstack.org/election/
