=========================
Victoria Release Schedule
=========================

.. note::

   Deadlines are generally the Thursday of the week on which they are noted
   below. Exceptions to this policy will be explicitly mentioned in the event
   description.

18 May 2020 - 16 October 2020 (22 weeks)

.. datatemplate::
   :source: schedule.yaml
   :template: schedule_table.tmpl

.. ics::
   :source: schedule.yaml
   :name: Victoria

`Subscribe to iCalendar file <schedule.ics>`_

Cross-project events
====================

.. _v-goals-research:

Victoria Goals Research
-----------------------

Pre-cycle planning and investigation into `the community-wide goals
for Victoria
<https://governance.openstack.org/tc/goals/selected/victoria/index.html>`__.

.. _v-ptg:

Virtual PTG
-----------

A virtual PTG will be held during this week. The Project Teams Gathering
provides and opportunity for teams to collaborate
and plan, and discuss requirements for future releases.

.. _v-1:

Victoria-1 milestone
--------------------

18 June, 2020 is the Victoria-1 milestone. See project-specific notes for
relevant deadlines.

.. _v-cycle-trail:

Ussuri Cycle-Trailing Release Deadline
--------------------------------------

All projects following the cycle-trailing release model must release
their Ussuri deliverables by 13 August, 2020.

.. _v-2:

Victoria-2 milestone
--------------------

30 July, 2020 is the Victoria-2 milestone. See project-specific notes for
relevant deadlines.

.. _v-final-lib:

Final release for non-client libraries
--------------------------------------

Libraries that are not client libraries (Oslo and others) should issue their
final release during this week. That allows to give time for last-minute
changes before feature freeze.

.. _v-3:

Victoria-3 milestone
--------------------

10 September, 2020 is the Victoria-3 milestone. See project-specific notes for
relevant deadlines.

.. _v-goals-complete:

Victoria Community Goals Completed
----------------------------------

Teams should prepare their documentation for completing `the
community-wide goals for Victoria
<https://governance.openstack.org/tc/goals/selected/victoria/index.html>`__.

.. _v-ff:

Feature freeze
--------------

The Victoria-3 milestone marks feature freeze for projects following the
`release:cycle-with-rc`_ model. No featureful patch should be landed
after this point. Exceptions may be granted by the project PTL.

.. _release:cycle-with-rc: https://releases.openstack.org/reference/release_models.html#cycle-with-rc

.. _v-rf:

Requirements freeze
-------------------

After the Victoria-3 milestone, only critical requirements and constraints
changes will be allowed. Freezing our requirements list gives packagers
downstream an opportunity to catch up and prepare packages for everything
necessary for distributions of the upcoming release. The requirements remain
frozen until the stable branches are created, with the release candidates.

.. _v-final-clientlib:

Final release for client libraries
----------------------------------

Client libraries should issue their final release during this week, to match
feature freeze.

.. _v-soft-sf:

Soft StringFreeze
-----------------

You are no longer allowed to accept proposed changes containing modifications
in user-facing strings. Such changes should be rejected by the review team and
postponed until the next series development opens (which should happen when RC1
is published).

.. _v-mf:

Membership Freeze
-----------------

Projects must participate in at least two milestones in order to be considered
part of the release. Projects made official after the second milestone, or
which fail to produce milestone releases for at least one of the first and
second milestones as well as the third milestone, are therefore not considered
part of the release for the cycle. This does not apply to cycle-trailing
packaging / lifecycle management projects.

.. _v-rc1:

RC1 target week
---------------

The week of 21 September is the target date for projects following the
`release:cycle-with-rc`_ model to issue their first release candidate.

.. _v-hard-sf:

Hard StringFreeze
-----------------

This happens when the RC1 for the project is tagged. At this point, ideally
no strings are changed (or added, or removed), to give translators time to
finish up their efforts.

.. _v-finalrc:

Final RCs and intermediary releases
-----------------------------------

The week of 5 October is the last week to issue release candidates or
intermediary releases before release week. During release week, only
final-release-critical releases will be accepted (at the discretion of the
release team).

.. _v-final:

Victoria release
----------------

The Victoria coordinated release will happen on Wednesday, 14 October, 2020.

.. _v-summit:

Open Infrastructure Summit
--------------------------

The virtual Open Infrastructure Summit will take place October 19-23.

Project-specific events
=======================

Cinder
------

.. _v-cinder-spec-freeze:

Cinder Spec Freeze
^^^^^^^^^^^^^^^^^^

All Cinder Specs for features to be implemented in Victoria must be approved by
Wednesday 1 July 2020 (23:59 UTC).

.. _v-cinder-driver-deadline:

Cinder New Driver Merge Deadline
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The deadline for merging a new backend driver to Cinder for the Victoria
release is Thursday 30 July 2020 (23:59 UTC).  New drivers must be (a) code
complete including unit tests, (b) merged into the code repository, and (c)
must have a 3rd Party CI running reliably.  (The idea is that new drivers will
be included in a release at the second milestone and thus be easily available
for downstream testing, documentation feedback, etc.)

.. _v-cinder-target-driver-deadline:

Cinder New Target Driver Merge Deadline
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The deadline for merging a new target driver to Cinder for the Victoria release
is Thursday 30 July 2020 (23:59 UTC).  New target drivers must be (a) code
complete including unit tests, (b) merged into the code repository, and (c)
must have a 3rd Party CI running reliably.  (The idea is that new drivers will
be included in a release at the second milestone and thus be easily available
for downstream testing, documentation feedback, etc.)

.. _v-cinder-feature-checkpoint:

Cinder New Feature Status Checkpoint
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If your new Cinder feature requires client support, keep in mind that the final
release for client libraries is in three weeks.  Thus your Cinder feature
should be substantially complete with unit tests by this time so that any
client changes can be reviewed, tested, and merged before 10 September.  Keep
in mind that 7 September is a holiday for many Cinder core reviewers, so we
will have reduced bandwith around the time of the Feature Freeze.  So please
plan ahead.

.. _v-cinder-driver-features-declaration:

Cinder Driver Features Declaration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

New features added to Cinder drivers must be merged at the time of the
OpenStack-wide Feature Freeze, which is coming up in three weeks.  During this
week, you should post a blueprint in Launchpad listing the Gerrit reviews of
features you'd like to land in Victoria.  (You can look among the Ussuri
blueprints for examples; contact the PTL if you have any questions.)  This will
help the team prioritize reviews and give you candid early feedback on whether
the features look ready.  Due to the 7 September holiday in the USA, there will
be reduced reviewing bandwidth right around the Feature Freeze, so it will pay
to plan ahead.

.. _v-cinder-ci-checkpoint:

Cinder 3rd Party CI Compliance Checkpoint
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This is a reminder that in order for a Cinder driver to be considered
'supported' in the Victoria release, its third party CI must be running
properly when the Cinder team does a final compliance check around the
time of the third milestone.  See the `Driver Compliance
<https://docs.openstack.org/cinder/latest/drivers-all-about.html#driver-compliance>`_
section of the Cinder Documentation for details.

Manila
------

.. _v-manila-spec-freeze:

Manila Spec Freeze
^^^^^^^^^^^^^^^^^^

All Manila specs targeted to Victoria must be approved by the end of the week.

.. _v-manila-new-driver-deadline:

Manila New Driver Deadline
^^^^^^^^^^^^^^^^^^^^^^^^^^

By the end of the week all new backend drivers for Manila must be substantially
complete, with unit tests, and passing 3rd party CI.  Drivers do not have to
actually merge until feature freeze.

.. _v-manila-fpfreeze:

Manila Feature Proposal Freeze
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All new Manila features must be proposed and substantially completed, with
unit, functional and integration tests by the end of the week.


Oslo
----

.. _v-oslo-feature-freeze:

Oslo Feature Freeze
^^^^^^^^^^^^^^^^^^^

All new Oslo features must be proposed and substantially complete, with unit
tests by the end of the week.
