================================
2024.1 Caracal Release Schedule
================================

.. note::

   Deadlines are generally the Thursday of the week on which they are noted
   below. Exceptions to this policy will be explicitly mentioned in the event
   description.

October 5, 2023 - April 3, 2024 (26 weeks)

.. datatemplate::
   :source: schedule.yaml
   :template: schedule_table.tmpl

.. ics::
   :source: schedule.yaml
   :name: Caracal

`Subscribe to iCalendar file <schedule.ics>`_

Cross-project events
====================

.. _c-vptg:

PTG (virtual)
-------------

From October 23 to October 27 we'll have a virtual PTG to plan the Caracal
release schedule.

.. _c-1:

Caracal-1 milestone
-------------------

November 16, 2023 is the Caracal-1 milestone. See project-specific notes
for relevant deadlines.

.. _c-cycle-trail:

Bobcat Cycle-Trailing Release Deadline
--------------------------------------

All projects following the cycle-trailing release model must release
their Bobcat deliverables by 7 December, 2023.

.. _c-2:

Caracal-2 milestone
-------------------

January 11, 2024 is the Caracal-2 milestone. See project-specific notes
for relevant deadlines.

.. _c-mf:

Membership Freeze
-----------------

Projects must participate in at least two milestones in order to be considered
part of the release. Projects made official after the second milestone, or
which fail to produce milestone releases for at least one of the first and
second milestones as well as the third milestone, are therefore not considered
part of the release for the cycle. This does not apply to cycle-trailing
packaging / lifecycle management projects.

.. _c-extra-atcs:

Extra-ATC freeze
----------------

All contributions to OpenStack are valuable, but some are not expressed as
Gerrit code changes. That allow teams to list active contributors to their
projects and who do not have a code contribution this cycle, and therefore won't
automatically be considered an Active Technical Contributor and allowed
to vote. This is done by adding extra-atcs to
https://opendev.org/openstack/governance/src/branch/master/reference/projects.yaml
before the Extra-ATC freeze date.

.. _c-final-lib:

Final release for non-client libraries
--------------------------------------

Libraries that are not client libraries (Oslo and others) should issue their
final release during this week. That allows to give time for last-minute
changes before feature freeze.

.. _c-3:

Caracal-3 milestone
-------------------

February 29, 2024 is the Caracal-3 milestone. See project-specific notes
for relevant deadlines.

.. _c-ff:

Feature freeze
--------------

The Caracal-3 milestone marks feature freeze for projects following the
`release:cycle-with-rc`_ model. No featureful patch should be landed
after this point. Exceptions may be granted by the project PTL.

.. _release:cycle-with-rc: https://releases.openstack.org/reference/release_models.html#cycle-with-rc

.. _c-final-clientlib:

Final release for client libraries
----------------------------------

Client libraries should issue their final release during this week, to match
feature freeze.

.. _c-soft-sf:

Soft StringFreeze
-----------------

You are no longer allowed to accept proposed changes containing modifications
in user-facing strings. Such changes should be rejected by the review team and
postponed until the next series development opens (which should happen when RC1
is published).

.. _c-rf:

Requirements freeze
-------------------

After the Caracal-3 milestone, only critical requirements and constraints
changes will be allowed. Freezing our requirements list gives packagers
downstream an opportunity to catch up and prepare packages for everything
necessary for distributions of the upcoming release. The requirements remain
frozen until the stable branches are created, with the release candidates.

.. _c-rc1:

RC1 target week
---------------

The week of March 11, 2024 is the target date for projects following the
`release:cycle-with-rc`_ model to issue their first release candidate.

.. _c-hard-sf:

Hard StringFreeze
-----------------

This happens when the RC1 for the project is tagged. At this point, ideally
no strings are changed (or added, or removed), to give translators time to
finish up their efforts.

.. _c-finalrc:

Final RCs and intermediary releases
-----------------------------------

The week of March 25, 2024 is the last week to issue release
candidates or intermediary releases before release week. During release week,
only final-release-critical releases will be accepted (at the discretion of
the release team).

.. _c-final:

Caracal release
---------------

The Caracal coordinated release will happen on Wednesday, April 3, 2024.

.. _c-cycle-highlights:

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

.. _Project Team Guide: https://docs.openstack.org/project-team-guide/release-management.html#cycle-highlights


Project-specific events
=======================

Oslo
----

.. _c-oslo-feature-freeze:

Oslo Feature Freeze
^^^^^^^^^^^^^^^^^^^

All new Oslo features must be proposed and substantially complete, with unit
tests by the end of the week.

Cinder
------

.. _c-cinder-mid-cycle-ptg-1:

Cinder Mid Cycle PTG - 1
^^^^^^^^^^^^^^^^^^^^^^^^

We will be conducting a mid-cycle PTG on 6th December, 2023 (Wednesday) which
is a continuation of 2024.1 Caracal PTG to track progress and discuss new
topics in a similar manner as of PTG.

Wednesday 6th December 2023 (1400-1600 UTC).

.. _c-cinder-spec-freeze:

Cinder Spec Freeze
^^^^^^^^^^^^^^^^^^

All Cinder Specs for features to be implemented in 2024.1 Caracal must be
approved by Friday 22 December 2022 (23:59 UTC).

.. _c-cinder-driver-deadline:

Cinder New Driver Merge Deadline
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The deadline for merging a new backend driver to Cinder for the 2024.1
Caracal release is Friday 26 January 2024 (20:00 UTC).  New drivers must be
(a) code complete including unit tests, (b) merged into the code repository,
and (c) must have a 3rd Party CI running reliably.  (Note that because of
where some holidays fall this cycle, this is later than the usual Milestone-2
deadline.)

.. _c-cinder-target-driver-deadline:

Cinder New Target Driver Merge Deadline
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The deadline for merging a new target driver to Cinder for the 2024.1 Caracal
release is Friday 26 January 2024 (20:00 UTC).  New target drivers must be
(a) code complete including unit tests, (b) merged into the code repository,
and (c) must have a 3rd Party CI running reliably.

.. _c-cinder-feature-checkpoint:

Cinder New Feature Status Checkpoint
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If your new Cinder feature requires client support, keep in mind that the final
release for client libraries is in four weeks.  Thus your Cinder feature
should be substantially complete with unit tests by this time so that any
client changes can be reviewed, tested, and merged before 01 March 2024.

.. _c-cinder-driver-features-declaration:

Cinder Driver Features Declaration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

New features added to Cinder drivers must be merged at the time of the
OpenStack-wide Feature Freeze, which is coming up in two weeks.  Before
the Cinder meeting this week, you should post a blueprint in Launchpad listing
the Gerrit reviews of features you'd like to land in 2024.1 Caracal.  (You
can look among the 2023.1 and 2023.2 blueprints for examples; contact the PTL
if you have any questions.)  This will help the team prioritize reviews and
give you candid early feedback on whether the features look ready.

.. _c-cinder-mid-cycle-ptg-2:

Cinder Mid Cycle PTG - 2
^^^^^^^^^^^^^^^^^^^^^^^^

We will be conducting Midcycle-2 PTG on 14th February, 2024 (Wednesday) which
is a continuation of 2024.1 Caracal Midcycle-1 PTG to track progress and
discuss new topics in a similar manner as of Midcycle-1 PTG.

Wednesday 14th February 2024 (1400-1600 UTC).

.. _c-cinder-ci-checkpoint:

Cinder 3rd Party CI Compliance Checkpoint
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This is a reminder that in order for a Cinder driver to be considered
'supported' in the 2024.1 Caracal release, its third party CI must be
running properly when the Cinder team does a final compliance check around the
time of the third milestone.  See the `Driver Compliance
<https://docs.openstack.org/cinder/latest/drivers-all-about.html#driver-compliance>`_
section of the Cinder Documentation for details.


Nova
----

.. _c-nova-spec-review-day:

Nova Spec Review Day
^^^^^^^^^^^^^^^^^^^^

On 7 November 2023 and 5 December 2023, Nova specifications targeting 2024.1
implementation will be prioritized for reviews by the Nova core team.


.. _c-nova-spec-freeze:

Nova Spec Freeze
^^^^^^^^^^^^^^^^

All Nova Specs for features to be implemented in 2024.1 Caracal must be
approved by 11 January 2024 (23:59 UTC).


.. _c-nova-review-day:

Nova Implementation Review Day
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

On 15 November 2023 and 10 January 2024, Nova prioritized blueprints and
bugfixes with open changes will be reviewed by the Nova core team.
