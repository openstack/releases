========================
Wallaby Release Schedule
========================

.. note::

   Deadlines are generally the Thursday of the week on which they are noted
   below. Exceptions to this policy will be explicitly mentioned in the event
   description.

.. note::
    All projects following the cycle-trailing release model must release
    their Wallaby deliverables by 02 July, 2021.

    `Xena schedule <https://releases.openstack.org/xena/schedule.html>`

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

.. _w-extra-atc-freeze:

Extra-ATC freeze
--------------------------------------

All contributions to OpenStack are valuable, but some are not expressed as
Gerrit code changes. That allow teams to list active contributors to their
projects and who do not have a code contribution this cycle, and therefore won't
automatically be considered an Active Technical Contributor and allowed
to vote. This is done by adding extra-atcs to
https://opendev.org/openstack/governance/src/branch/master/reference/projects.yaml
before the Extra-ATC freeze on 25 February, 2021.

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

.. _w-cycle-highlights:

Cycle Highlights
---------------------

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

.. _Project Team Guide: https://docs.openstack.org/project-team-guide/release-management.html#cycle-highlights

Project-specific events
=======================

Cinder
------

.. _w-cinder-spec-freeze:

Cinder Spec Freeze
^^^^^^^^^^^^^^^^^^

All Cinder Specs for features to be implemented in Wallaby must be approved by
Friday 18 December 2020 (23:59 UTC).

.. _w-cinder-driver-deadline:

Cinder New Driver Merge Deadline
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The deadline for merging a new backend driver to Cinder for the Wallaby
release is Thursday 21 January 2021 (20:00 UTC).  New drivers must be (a) code
complete including unit tests, (b) merged into the code repository, and (c)
must have a 3rd Party CI running reliably.  (The idea is that new drivers will
be included in a release at the second milestone and thus be easily available
for downstream testing, documentation feedback, etc.)

.. _w-cinder-target-driver-deadline:

Cinder New Target Driver Merge Deadline
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The deadline for merging a new target driver to Cinder for the Wallaby release
is Thursday 21 January 2021 (20:00 UTC).  New target drivers must be (a) code
complete including unit tests, (b) merged into the code repository, and (c)
must have a 3rd Party CI running reliably.  (The idea is that new drivers will
be included in a release at the second milestone and thus be easily available
for downstream testing, documentation feedback, etc.)

.. _w-cinder-feature-checkpoint:

Cinder New Feature Status Checkpoint
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If your new Cinder feature requires client support, keep in mind that the final
release for client libraries is in four weeks.  Thus your Cinder feature
should be substantially complete with unit tests by this time so that any
client changes can be reviewed, tested, and merged before 11 March 2021.

.. _w-cinder-driver-features-declaration:

Cinder Driver Features Declaration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

New features added to Cinder drivers must be merged at the time of the
OpenStack-wide Feature Freeze, which is coming up in three weeks.  Before
the Cinder meeting this week, you should post a blueprint in Launchpad listing
the Gerrit reviews of features you'd like to land in Wallaby.  (You can look
among the Ussuri and Victoria blueprints for examples; contact the PTL if you
have any questions.)  This will help the team prioritize reviews and give you
candid early feedback on whether the features look ready.

.. _w-cinder-ci-checkpoint:

Cinder 3rd Party CI Compliance Checkpoint
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This is a reminder that in order for a Cinder driver to be considered
'supported' in the Wallaby release, its third party CI must be running
properly when the Cinder team does a final compliance check around the
time of the third milestone.  See the `Driver Compliance
<https://docs.openstack.org/cinder/latest/drivers-all-about.html#driver-compliance>`_
section of the Cinder Documentation for details.

Manila
------

.. _w-manila-spec-freeze:

Manila Spec Freeze
^^^^^^^^^^^^^^^^^^

All Manila specs targeted to Wallaby must be approved by the end of the week.

.. _w-manila-new-driver-deadline:

Manila New Driver Deadline
^^^^^^^^^^^^^^^^^^^^^^^^^^

By the end of the week all new backend drivers for Manila must be substantially
complete, with unit tests, and passing 3rd party CI.  Drivers do not have to
actually merge until feature freeze.

.. _w-manila-fpfreeze:

Manila Feature Proposal Freeze
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All new Manila features must be proposed and substantially completed, with
unit, functional and integration tests by the end of the week.

Oslo
----

.. _w-oslo-feature-freeze:

Oslo Feature Freeze
^^^^^^^^^^^^^^^^^^^

All new Oslo features must be proposed and substantially complete, with unit
tests by the end of the week.
