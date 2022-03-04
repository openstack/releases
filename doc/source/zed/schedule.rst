====================
Zed Release Schedule
====================

.. note::

   Deadlines are generally the Thursday of the week on which they are noted
   below. Exceptions to this policy will be explicitly mentioned in the event
   description.

30 March 2022 - 05 October 2022 (27 weeks)

.. datatemplate::
   :source: schedule.yaml
   :template: schedule_table.tmpl

.. ics::
   :source: schedule.yaml
   :name: Zed

`Subscribe to iCalendar file <schedule.ics>`_

Cross-project events
====================

.. _z-ptg:

Virtual PTG
-----------

.. This needs to be added to the schedule once we know when the event will be

A virtual PTG will be held during this week (April 04-08, 2022). The Project
Teams Gathering provides an opportunity for teams to collaborate
and plan, and discuss requirements for future releases.

.. _z-1:

Zed-1 milestone
---------------

19 May, 2022 is the Zed-1 milestone. See project-specific notes for
relevant deadlines.

.. _z-cycle-trail:

Yoga Cycle-Trailing Release Deadline
------------------------------------

All projects following the cycle-trailing release model must release
their Yoga deliverables by 23 June, 2022.

.. _z-2:

Zed-2 milestone
---------------

14 July, 2022 is the Zed-2 milestone. See project-specific notes for
relevant deadlines.

.. _z-mf:

Membership Freeze
-----------------

Projects must participate in at least two milestones in order to be considered
part of the release. Projects made official after the second milestone, or
which fail to produce milestone releases for at least one of the first and
second milestones as well as the third milestone, are therefore not considered
part of the release for the cycle. This does not apply to cycle-trailing
packaging / lifecycle management projects.

.. _z-extra-atc-freeze:

Extra-ATC freeze
----------------

All contributions to OpenStack are valuable, but some are not expressed as
Gerrit code changes. That allow teams to list active contributors to their
projects and who do not have a code contribution this cycle, and therefore won't
automatically be considered an Active Technical Contributor and allowed
to vote. This is done by adding extra-atcs to
https://opendev.org/openstack/governance/src/branch/master/reference/projects.yaml
before the Extra-ATC freeze on 18 August, 2022.

.. _z-final-lib:

Final release for non-client libraries
--------------------------------------

Libraries that are not client libraries (Oslo and others) should issue their
final release during this week. That allows to give time for last-minute
changes before feature freeze.

.. _z-3:

Zed-3 milestone
---------------

01 September, 2022 is the Zed-3 milestone. See project-specific notes for
relevant deadlines.

.. _z-ff:

Feature freeze
--------------

The Zed-3 milestone marks feature freeze for projects following the
`release:cycle-with-rc`_ model. No featureful patch should be landed
after this point. Exceptions may be granted by the project PTL.

.. _release:cycle-with-rc: https://releases.openstack.org/reference/release_models.html#cycle-with-rc

.. _z-final-clientlib:

Final release for client libraries
----------------------------------

Client libraries should issue their final release during this week, to match
feature freeze.

.. _z-soft-sf:

Soft StringFreeze
-----------------

You are no longer allowed to accept proposed changes containing modifications
in user-facing strings. Such changes should be rejected by the review team and
postponed until the next series development opens (which should happen when RC1
is published).

.. _z-rf:

Requirements freeze
-------------------

After the Zed-3 milestone, only critical requirements and constraints
changes will be allowed. Freezing our requirements list gives packagers
downstream an opportunity to catch up and prepare packages for everything
necessary for distributions of the upcoming release. The requirements remain
frozen until the stable branches are created, with the release candidates.

.. _z-rc1:

RC1 target week
---------------

The week of 12 September, 2022 is the target date for projects following the
`release:cycle-with-rc`_ model to issue their first release candidate.

.. _z-hard-sf:

Hard StringFreeze
-----------------

This happens when the RC1 for the project is tagged. At this point, ideally
no strings are changed (or added, or removed), to give translators time to
finish up their efforts.

.. _z-finalrc:

Final RCs and intermediary releases
-----------------------------------

The week of 26th - 30th September, 2022 is the last week to issue release
candidates or intermediary releases before release week. During release week,
only final-release-critical releases will be accepted (at the discretion of
the release team).

.. _z-final:

Zed release
-----------

The Zed coordinated release will happen on Wednesday, 05 October, 2022.

.. _z-summit:

Open Infrastructure Summit
--------------------------

The Open Infrastructure Summit happens in this week, 7th - 9th June, 2022
in Berlin, Germany. See details at the official `OpenInfra Summit Page`_.

.. _OpenInfra Summit Page: https://openinfra.dev/summit/

.. _z-cycle-highlights:

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
`Yoga Highlights <https://releases.openstack.org/yoga/highlights.html>`_.

.. _Project Team Guide: https://docs.openstack.org/project-team-guide/release-management.html#cycle-highlights

Project-specific events
=======================

