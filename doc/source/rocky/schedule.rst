========================
 Rocky Release Schedule
========================

1 March 2018 - 29 August 2018 (26 weeks)

.. datatemplate::
   :source: schedule.yaml
   :template: schedule_table.tmpl

.. ics::
   :source: schedule.yaml
   :name: Rocky

`Subscribe to iCalendar file <schedule.ics>`__

.. note::

   With the exception of the final release date and cycle-trailing
   release date, deadlines are generally the Thursday of the week on
   which they are noted above. For example, the Feature Freeze in week
   R-5 is on 26 July. Exceptions to this policy will be explicitly
   mentioned in the event description.

Cross-project events
====================

.. _r-goals-research:

Rocky Goals Research
--------------------

Pre-cycle planning and investigation into `the community-wide goals
for Rocky <https://governance.openstack.org/tc/goals/rocky/index.html>`__.

.. _r-ptg:

Rocky Project Team Gathering (PTG)
----------------------------------

`Project team gathering <https://www.openstack.org/ptg>`__ for the Rocky
cycle 26 February - 2 March 2018 in Dublin, Ireland.

.. _r-1:

Rocky-1 milestone
-----------------

19 April 2018 is the Rocky-1 milestone window for projects following the
`release:cycle-with-milestones`_ model.

.. _release:cycle-with-milestones: https://releases.openstack.org/reference/release_models.html#cycle-with-milestones

.. _r-goals-ack:

Rocky Community Goals Acknowledgement
-------------------------------------

Teams should prepare their acknowledgement of `the community-wide
goals for
<https://governance.openstack.org/tc/goals/rocky/index.html>`__.

.. _r-summit:

OpenStack Summit
----------------

The OpenStack Summit happens during this week in Vancouver, BC. It will
include a "Forum" in which people from all parts of our community will gather
to give feedback on the last release (Queens) and discuss requirements for the
next development cycle (Stein).

.. _r-2:

Rocky-2 milestone
-----------------

7 June 2018 is the Rocky-2 milestone window for projects following the
`release:cycle-with-milestones`_ model.

.. _r-final-lib:

Final release for non-client libraries
--------------------------------------

Libraries that are not client libraries (Oslo and others) should issue their
final release during this week. That allows to give time for last-minute
changes before feature freeze.

.. _r-3:

Rocky-3 milestone
-----------------

26 July 2018 is the Rocky-3 milestone window for projects following the
`release:cycle-with-milestones`_ model.

.. _r-goals-complete:

Rocky Community Goals Completed
-------------------------------

Teams should prepare their documentation for completing `the
community-wide goals for Rocky
<https://governance.openstack.org/tc/goals/rocky/index.html>`__.

.. _r-extra-atcs:

Extra-ATCs deadline
-------------------

Project teams should identify contributors who have had a significant
impact this cycle but who would not qualify for ATC status using the
regular process because they have not submitted a patch. Those names
should be added to the governance repo for consideration as ATC for
the future.

.. _r-ff:

Feature freeze
--------------

The Rocky-3 milestone marks feature freeze for projects following the
`release:cycle-with-milestones`_ model. No featureful patch should be landed
after this point. Exceptions may be granted by the project PTL.

.. _r-rf:

Requirements freeze
-------------------

After the Rocky-3 milestone, only critical requirements and
constraints changes will be allowed. Freezing our requirements list
gives packagers downstream an opportunity to catch up and prepare
packages for everything necessary for distributions of the upcoming
release. The requirements remain frozen until the stable branches are
created, with the release candidates.

.. _r-final-clientlib:

Final release for client libraries
----------------------------------

Client libraries should issue their final release during this week, to
match feature freeze.

.. _r-soft-sf:

Soft StringFreeze
-----------------

You are no longer allowed to accept proposed changes containing
modifications in user-facing strings. Such changes should be rejected
by the review team and postponed until the next series development
opens (which should happen when RC1 is published).

.. _r-mf:

Membership Freeze
-----------------

Projects must participate in at least two milestones in order to be
considered part of the release. Projects made official after the
second milestone, or which fail to produce milestone releases for at
least one of the first and second milestones as well as the third
milestone, are therefore not considered part of the release for the
cycle. This does not apply to cycle-trailing packaging / lifecycle
management projects.

.. _r-rc1:

RC1 target week
---------------

The week of 6 August 2018 is the target date for projects following the
`release:cycle-with-milestones`_ model to issue their first release candidate,
with a deadline of 9 August 2018.

.. _r-hard-sf:

Hard StringFreeze
-----------------

This happens when the RC1 for the project is tagged. At this point, ideally
no strings are changed (or added, or removed), to give translator time to
finish up their efforts.

.. _r-finalrc:

Final RCs and intermediary releases
-----------------------------------

The week of 20 August 2018 is the last week to issue release candidates or
intermediary releases before release week. During release week, only
final-release-critical releases will be accepted (at the discretion of
the release team).

.. _r-release:

Rocky release
-------------

The Rocky coordinated release will happen on 30 August 2018.

.. _r-trailing-release:

Rocky cycle-trailing release deadline
-------------------------------------

The release deadline for projects using the release:cycle-trailing model that
follow the main release cycle is set to November 28, 2018.

.. _r-tc-email-deadline:

TC Election Email Deadline
--------------------------
Contributors that will be in the electorate for the upcoming election
should confirm their gerrit email addresses by this date (April 18th, 2018 at
00:00 UTC). Electorate rolls are generated after this date and ballots will
be sent to the listed gerrit email address.

.. _r-tc-nominations:

TC Election Nomination Begins
-----------------------------
Technical committee candidates interested in serving for the next calendar year
should announce their candidacies and platforms during this week.

.. _r-tc-campaigning:

TC Election Campaigning Begins
------------------------------
The electorate has time to ask candidates questions about their platforms
and debate topics before polling begins.

.. _r-tc-polling:

TC Election Polling Begins
--------------------------
Election polling week for open seats on the TC.

Project-specific events
=======================

PTL Elections
-------------

Keystone
--------

.. _r-keystone-spec-proposal-freeze:

Keystone Spec Proposal Freeze
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All Keystone specs targeted to Rocky must be submitted to the keystone-specs
repository by the end of the week.

.. _r-keystone-spec-freeze:

Keystone Spec Freeze
^^^^^^^^^^^^^^^^^^^^

All Keystone specs targeted to Rocky must be approved by the end of the week.

.. _r-keystone-fpfreeze:

Keystone Feature Proposal Freeze
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All new Keystone features must be proposed and substantially completed, with
unit tests and documentation by the end of the week.

.. _r-keystone-ffreeze:

Keystone Feature Freeze
^^^^^^^^^^^^^^^^^^^^^^^

All new Keystone features must be merged by the end of the week.

Manila
------

.. _r-manila-spec-freeze:

Manila Spec Freeze
^^^^^^^^^^^^^^^^^^

All Manila specs must be approved by 19 Apr 2018 (23:59 UTC).

.. _r-manila-driver-deadline:

Manila New Driver Submission Deadline
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The deadline for submitting new backend drivers to to Manila is 4 Jun 2018
(23:59 UTC). New drivers must be substantially complete, with unit tests, and
passing 3rd party CI by this date. Drivers do not need to be merged until the
feature freeze date, but drivers that don't meet this deadline will not be
considered at all for Rocky.


.. _r-manila-fp-freeze:

Manila Feature Proposal Freeze
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All new Manila features must be proposed and substantially complete, with unit
tests by 9 Jul 2018 (23:59 UTC).

Cinder
------

.. _r-cinder-spec-freeze:

Cinder Spec Freeze
^^^^^^^^^^^^^^^^^^

All Cinder specs must be approved by 4 Jun 2018 (23:59 UTC).

.. _r-cinder-driver-deadline:

Cinder New Driver Submission Deadline
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The deadline for submitting new backend drivers to Cinder is 4 Jun 2018
(23:59 UTC).  New drivers must be complete, with unit tests, passing
3rd Party CI and be merged by this date.

.. _r-cinder-feature-freeze:

Cinder Feature Proposal Freeze
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All new Cinder features must be proposed and substantially complete,
with unit test by 16 Jul 2018 (23:59 UTC).

Oslo
----

.. _r-oslo-feature-freeze:

Oslo Feature Freeze
^^^^^^^^^^^^^^^^^^^

All new Oslo features must be proposed and substantially complete, with unit
tests by the end of the week.

