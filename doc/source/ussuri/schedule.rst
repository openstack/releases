=======================
Ussuri Release Schedule
=======================

.. note::

   Deadlines are generally the Thursday of the week on which they are noted
   below. Exceptions to this policy will be explicitly mentioned in the event
   description.

21 October 2019 - 15 May 2020 (30 weeks)

.. datatemplate::
   :source: schedule.yaml
   :template: schedule_table.tmpl

.. ics::
   :source: schedule.yaml
   :name: Ussuri

`Subscribe to iCalendar file <schedule.ics>`_

Cross-project events
====================

.. _u-goals-research:

Ussuri Goals Research
---------------------

Pre-cycle planning and investigation into `the community-wide goals
for Ussuri
<https://governance.openstack.org/tc/goals/selected/ussuri/index.html>`__.

.. _u-summit:

Open Infrastructure Summit
--------------------------

The Open Infrastructure Summit happens during this week in Shanghai, China. It
will include a “Forum” in which people from all parts of our community will
gather to give feedback on the last release (Train) and discuss requirements
for future releases.

.. _u-1:

Ussuri-1 milestone
------------------

12 December, 2019 is the Ussuri-1 milestone. See project-specific notes for
relevant deadlines.

.. _u-py-drop-1:

Services Drop python 2 Completed
--------------------------------

OpenStack Services `dropped the python 2.7 support and testing
<https://governance.openstack.org/tc/goals/selected/ussuri/drop-py27.html>`__.
Project needs to coordinate with third party CI or any backend drivers.

.. _u-py-drop-2:

Common libraries & QA Start dropping python 2
---------------------------------------------

Common libraries & QA start `dropping the python 2.7 support and testing
<https://governance.openstack.org/tc/goals/selected/ussuri/drop-py27.html>`__.
This includes Oslo, QA tools (including Tempest plugins or any other
testing tools), common lib used among projects (os-brick), Client
libraries. Tempest will drop the support during Feb as discussed
with TripleO.

.. _u-goals-ack:

Ussuri Community Goals Acknowledgement
--------------------------------------

Teams should prepare their acknowledgement of `the community-wide
goals for Ussuri
<https://governance.openstack.org/tc/goals/selected/ussuri/index.html>`__.

.. _u-cycle-trail:

Train Cycle-Trailing Release Deadline
-------------------------------------

All projects following the cycle-trailing release model must release
their Train deliverables by 9 January, 2020.

.. _u-2:

Ussuri-2 milestone
------------------

13 February, 2020 is the Ussuri-2 milestone. See project-specific notes for
relevant deadlines.

.. _u-py-drop-3:

Common libraries & QA Drop python 2 Completed
----------------------------------------------

Common libraries & QA `dropped the python 2.7 support and testing
<https://governance.openstack.org/tc/goals/selected/ussuri/drop-py27.html>`__.

.. _u-py-drop-final:

Requirement Drop python 2 & Audit
---------------------------------

Requirement to `drop the python 2.7 support and testing
<https://governance.openstack.org/tc/goals/selected/ussuri/drop-py27.html>`__.
Audit that every project except Swift have dropped the python 2 support.

.. _u-final-lib:

Final release for non-client libraries
--------------------------------------

Libraries that are not client libraries (Oslo and others) should issue their
final release during this week. That allows to give time for last-minute
changes before feature freeze.

.. _u-3:

Ussuri-3 milestone
------------------

9 April, 2020 is the Ussuri-3 milestone. See project-specific notes for
relevant deadlines.

.. _u-goals-complete:

Ussuri Community Goals Completed
--------------------------------

Teams should prepare their documentation for completing `the
community-wide goals for Ussuri
<https://governance.openstack.org/tc/goals/selected/ussuri/index.html>`__.

.. _u-extra-atcs:

Extra-ATCs deadline
-------------------
Project teams should identify contributors who have had a significant impact
this cycle but who would not qualify for ATC status using the regular process
because they have not submitted a patch. Those names should be added to the
governance repo for consideration as ATC for the future.

.. _u-ff:

Feature freeze
--------------

The Ussuri-3 milestone marks feature freeze for projects following the
`release:cycle-with-rc`_ model. No featureful patch should be landed
after this point. Exceptions may be granted by the project PTL.

.. _release:cycle-with-rc: https://releases.openstack.org/reference/release_models.html#cycle-with-rc

.. _u-rf:

Requirements freeze
-------------------

After the Ussuri-3 milestone, only critical requirements and constraints changes
will be allowed. Freezing our requirements list gives packagers downstream an
opportunity to catch up and prepare packages for everything necessary for
distributions of the upcoming release. The requirements remain frozen until the
stable branches are created, with the release candidates.

.. _u-final-clientlib:

Final release for client libraries
----------------------------------

Client libraries should issue their final release during this week, to match
feature freeze.

.. _u-soft-sf:

Soft StringFreeze
-----------------

You are no longer allowed to accept proposed changes containing modifications
in user-facing strings. Such changes should be rejected by the review team and
postponed until the next series development opens (which should happen when RC1
is published).

.. _u-mf:

Membership Freeze
-----------------

Projects must participate in at least two milestones in order to be considered
part of the release. Projects made official after the second milestone, or
which fail to produce milestone releases for at least one of the first and
second milestones as well as the third milestone, are therefore not considered
part of the release for the cycle. This does not apply to cycle-trailing
packaging / lifecycle management projects.

.. _u-rc1:

RC1 target week
---------------

The week of 20 April is the target date for projects following the
`release:cycle-with-rc`_ model to issue their first release candidate.

.. _u-hard-sf:

Hard StringFreeze
-----------------

This happens when the RC1 for the project is tagged. At this point, ideally
no strings are changed (or added, or removed), to give translators time to
finish up their efforts.

.. _u-finalrc:

Final RCs and intermediary releases
-----------------------------------

The week of 4 May is the last week to issue release candidates or
intermediary releases before release week. During release week, only
final-release-critical releases will be accepted (at the discretion of the
release team).

.. _u-final:

Ussuri release
--------------

The Ussuri coordinated release will happen on Wednesday, 13 May, 2020.

.. _v-election-email-deadline:

Election Email Deadline
-----------------------
Contributors that will be in the electorate for the upcoming elections
should confirm their gerrit email addresses by this date (April 7th, 2020
at 00:00 UTC). Electorate rolls are generated after this date and ballots will
be sent to the listed gerrit email address.

TC Elections
------------
.. _v-tc-nominations:

TC Election Nomination Begins
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Technical committee candidates interested in serving for the next calendar year
should announce their candidacies and platforms during this week.  Please see
the `Election site`_ for specific timing imformation.

.. _v-tc-campaigning:

TC Election Campaigning Begins
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The electorate has time to ask candidates questions about their platforms
and debate topics before polling begins.  Please see the `Election site`_ for
specific timing information.

.. _v-tc-polling:

TC Election Polling Begins
^^^^^^^^^^^^^^^^^^^^^^^^^^
Election polling week for open seats on the TC.  Please see the
`Election site`_ for specific timing imformation.

Project-specific events
=======================

Cinder
------
.. _u-cinder-spec-freeze:

Cinder Spec Freeze
^^^^^^^^^^^^^^^^^^

All Cinder Specs for features to be implemented in Ussuri must be approved
by 31 Jan 2020 (23:59 UTC).

.. _u-cinder-driver-deadline:

Cinder New Driver Merge Deadline
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The deadline for merging a new backend driver to Cinder for the Ussuri release
is 13 February 2020 (23:59 UTC).  New drivers must be (a) code complete
including unit tests, (b) merged into the code repository, and (c) must have
a 3rd Party CI running reliably.  (The idea is that new drivers will be
included in a release at the second milestone and thus be easily available
for downstream testing, documentation feedback, etc.)

.. _u-cinder-target-driver-deadline:

Cinder New Target Driver Merge Deadline
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The deadline for merging a new target driver to Cinder for the Ussuri release
is 13 February 2020 (23:59 UTC).  New target drivers must be (a) code complete
including unit tests, (b) merged into the code repository, and (c) must have
a 3rd Party CI running reliably.  (The idea is that new drivers will be
included in a release at the second milestone and thus be easily available
for downstream testing, documentation feedback, etc.)

.. _u-cinder-feature-checkpoint:

Cinder New Feature Status Checkpoint
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If your new Cinder feature requires client support, keep in mind that
the final release for client libraries is in three weeks.  Thus your Cinder
feature should be substantially complete with unit tests by this time so
that any client changes can be reviewed, tested, and merged before 9 April.

.. _u-cinder-ci-checkpoint:

Cinder 3rd Party CI Compliance Checkpoint
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This is a reminder that in order for a Cinder driver to be considered
'supported' in the Ussuri release, its third party CI must be running
properly when the Cinder team does a final compliance check around the
time of the third milestone.  See the `Driver Compliance
<https://docs.openstack.org/cinder/latest/drivers-all-about.html#driver-compliance>`_
section of the Cinder Documentation for details.

Manila
------

.. _u-manila-spec-freeze:

Manila Spec Freeze
^^^^^^^^^^^^^^^^^^

All Manila specs targeted to Ussuri must be approved by the end of the week.

.. _u-manila-driver-deadline:

Manila Driver Deadline
^^^^^^^^^^^^^^^^^^^^^^

By the end of the week all new backend drivers for Manila must be substantially
complete, with unit tests, and passing 3rd party CI.  Drivers do not have to
actually merge until feature freeze.

.. _u-manila-fpfreeze:

Manila Feature Proposal Freeze
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All new Manila features must be proposed and substantially completed, with
unit, functional and integration tests by the end of the week.


Oslo
----

.. _u-oslo-feature-freeze:

Oslo Feature Freeze
^^^^^^^^^^^^^^^^^^^

All new Oslo features must be proposed and substantially complete, with unit
tests by the end of the week.


PTL Elections
-------------

Keystone
--------

.. _u-keystone-spec-proposal-freeze:

Keystone Spec Proposal Freeze
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All Keystone specs targeted to Ussuri must be submitted to the keystone-specs
repository by the end of the week.

.. _u-keystone-spec-freeze:

Keystone Spec Freeze
^^^^^^^^^^^^^^^^^^^^

All Keystone specs targeted to Ussuri must be approved by the end of the week.

.. _u-keystone-fpfreeze:

Keystone Feature Proposal Freeze
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All new Keystone features must be proposed and substantially completed, with
unit tests and documentation by the end of the week.

.. _u-keystone-ffreeze:

Keystone Feature Freeze
^^^^^^^^^^^^^^^^^^^^^^^

All new Keystone features must be merged by the end of the week.

PTL Elections
-------------

.. _v-ptl-nominations:

'U' PTL self-nomination
^^^^^^^^^^^^^^^^^^^^^^^

Project team lead candidates for the 'U' cycle should announce their
candidacy during this week.  Refer to the `Election Site`_ for exact details.

.. _v-ptl-polling:

'U' PTL Election Polling Begins
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Election week for Project team leads (where an election must be held to
determine the winner).  Refer to the `Election Site`_ for exact details.

.. _Election site: https://governance.openstack.org/election/
