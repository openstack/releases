=====================
Yoga Release Schedule
=====================

.. note::

   Deadlines are generally the Thursday of the week on which they are noted
   below. Exceptions to this policy will be explicitly mentioned in the event
   description.

06 October 2021 - 30 March 2022 (25 weeks)

.. datatemplate::
   :source: schedule.yaml
   :template: schedule_table.tmpl

.. ics::
   :source: schedule.yaml
   :name: Yoga

`Subscribe to iCalendar file <schedule.ics>`_

Cross-project events
====================

.. _y-goals-research:

Yoga Goals Research
-------------------

Pre-cycle planning and investigation into `the community-wide goals
for Yoga
<https://governance.openstack.org/tc/goals/selected/yoga/index.html>`__.

.. _y-ptg:

Virtual PTG
-----------

.. This needs to be added to the schedule once we know when the event will be

A virtual PTG will be held during this week (October 18-22, 2021). The Project
Teams Gathering provides and opportunity for teams to collaborate
and plan, and discuss requirements for future releases.

.. _y-1:

Yoga-1 milestone
----------------

18 November, 2021 is the Yoga-1 milestone. See project-specific notes for
relevant deadlines.

.. _y-cycle-trail:

Yoga Cycle-Trailing Release Deadline
------------------------------------

All projects following the cycle-trailing release model must release
their Xena deliverables by 16 December, 2021.

.. _y-2:

Yoga-2 milestone
----------------

06 January, 2022 is the Yoga-2 milestone. See project-specific notes for
relevant deadlines.

.. _y-mf:

Membership Freeze
-----------------

Projects must participate in at least two milestones in order to be considered
part of the release. Projects made official after the second milestone, or
which fail to produce milestone releases for at least one of the first and
second milestones as well as the third milestone, are therefore not considered
part of the release for the cycle. This does not apply to cycle-trailing
packaging / lifecycle management projects.

.. _y-extra-atc-freeze:

Extra-ATC freeze
--------------------------------------

All contributions to OpenStack are valuable, but some are not expressed as
Gerrit code changes. That allow teams to list active contributors to their
projects and who do not have a code contribution this cycle, and therefore won't
automatically be considered an Active Technical Contributor and allowed
to vote. This is done by adding extra-atcs to
https://opendev.org/openstack/governance/src/branch/master/reference/projects.yaml
before the Extra-ATC freeze on 10 February, 2022.

.. _y-final-lib:

Final release for non-client libraries
--------------------------------------

Libraries that are not client libraries (Oslo and others) should issue their
final release during this week. That allows to give time for last-minute
changes before feature freeze.

.. _y-3:

Yoga-3 milestone
----------------

24 February, 2022 is the Yoga-3 milestone. See project-specific notes for
relevant deadlines.

.. _y-ff:

Feature freeze
--------------

The Yoga-3 milestone marks feature freeze for projects following the
`release:cycle-with-rc`_ model. No featureful patch should be landed
after this point. Exceptions may be granted by the project PTL.

.. _release:cycle-with-rc: https://releases.openstack.org/reference/release_models.html#cycle-with-rc

.. _y-final-clientlib:

Final release for client libraries
----------------------------------

Client libraries should issue their final release during this week, to match
feature freeze.

.. _y-soft-sf:

Soft StringFreeze
-----------------

You are no longer allowed to accept proposed changes containing modifications
in user-facing strings. Such changes should be rejected by the review team and
postponed until the next series development opens (which should happen when RC1
is published).

.. _y-rf:

Requirements freeze
-------------------

After the Yoga-3 milestone, only critical requirements and constraints
changes will be allowed. Freezing our requirements list gives packagers
downstream an opportunity to catch up and prepare packages for everything
necessary for distributions of the upcoming release. The requirements remain
frozen until the stable branches are created, with the release candidates.

.. _y-goals-complete:

Yoga Community Goals Completed
------------------------------

Teams should prepare their documentation for completing `the
community-wide goals for Yoga
<https://governance.openstack.org/tc/goals/selected/yoga/index.html>`__.

.. _y-rc1:

RC1 target week
---------------

The week of 07 March, 2022 is the target date for projects following the
`release:cycle-with-rc`_ model to issue their first release candidate.

.. _y-hard-sf:

Hard StringFreeze
-----------------

This happens when the RC1 for the project is tagged. At this point, ideally
no strings are changed (or added, or removed), to give translators time to
finish up their efforts.

.. _y-finalrc:

Final RCs and intermediary releases
-----------------------------------

The week of 21st-25th March, 2022 is the last week to issue release candidates
or intermediary releases before release week. During release week, only
final-release-critical releases will be accepted (at the discretion of the
release team).

.. _y-final:

Yoga release
------------

The Yoga coordinated release will happen on Wednesday, 30 March, 2022.

.. _y-summit:

Open Infrastructure Summit
--------------------------

The Open Infrastructure Summit is expected to take place some time in October.
Exact event dates are yet to be determined.

.. _y-cycle-highlights:

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
`Xena Highlights <https://releases.openstack.org/xena/highlights.html>`_.

.. _Project Team Guide: https://docs.openstack.org/project-team-guide/release-management.html#cycle-highlights

Project-specific events
=======================

Oslo
----

.. _y-oslo-feature-freeze:

Oslo Feature Freeze
^^^^^^^^^^^^^^^^^^^

All new Oslo features must be proposed and substantially complete, with unit
tests by the end of the week.

Manila
------

.. _y-manila-spec-freeze:

Manila Spec Freeze
^^^^^^^^^^^^^^^^^^

All Manila specs targeted to Yoga must be approved by the end of the week.

.. _y-manila-new-driver-deadline:

Manila New Driver Deadline
^^^^^^^^^^^^^^^^^^^^^^^^^^

By the end of the week all new backend drivers for Manila must be substantially
complete, with unit tests, and passing 3rd party CI. Drivers do not have to
actually merge until feature freeze.

.. _y-manila-fpfreeze:

Manila Feature Proposal Freeze
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All new Manila features must be proposed and substantially completed, with
unit, functional and integration tests by the end of the week.
