=============================
2027.1 Indri Release Schedule
=============================

.. note::

   Deadlines are generally the Thursday of the week on which they are noted
   below. Exceptions to this policy will be explicitly mentioned in the event
   description.

1 October, 2026 - 24 March, 2027 (25 weeks)

.. datatemplate::
   :source: schedule.yaml
   :template: schedule_table.tmpl

.. ics::
   :source: schedule.yaml
   :name: Indri

`Subscribe to iCalendar file <schedule.ics>`_

Cross-project events
====================

.. _i-vptg:

PTG (virtual)
-------------

From 12 to 16 October, 2026 we'll have a virtual PTG to plan the
2027.1 Indri release schedule.

.. _i-1:

Indri-1 milestone
-----------------

19 November, 2026 is the Indri-1 milestone. See project-specific notes
for relevant deadlines.

.. _i-cycle-trail:

2026.2 Hibiscus Cycle-Trailing Release Deadline
-----------------------------------------------

All projects following the cycle-trailing release model must release
their 2026.2 Hibiscus deliverables by 3 December, 2026.

.. _i-2:

Indri-2 milestone
-----------------

14 January, 2027 is the Indri-2 milestone. See project-specific notes
for relevant deadlines.

.. _i-mf:

Membership Freeze
-----------------

Projects must participate in at least two milestones in order to be considered
part of the release. Projects made official after the second milestone, or
which fail to produce milestone releases for at least one of the first and
second milestones as well as the third milestone, are therefore not considered
part of the release for the cycle. This does not apply to cycle-trailing
packaging / lifecycle management projects.

.. _i-extra-acs:

Extra-AC freeze
---------------

All contributions to OpenStack are valuable, but some are not expressed as
Gerrit code changes. That allow teams to list active contributors to their
projects and who do not have a code contribution this cycle, and therefore won't
automatically be considered an Active Contributor and allowed
to vote. This is done by adding extra-acs to
https://opendev.org/openstack/governance/src/branch/master/reference/projects.yaml
before the Extra-AC freeze date.

.. _i-final-lib:

Final release for non-client libraries
--------------------------------------

Libraries that are not client libraries (Oslo and others) should issue their
final release during this week. That allows to give time for last-minute
changes before feature freeze.

.. _i-3:

Indri-3 milestone
-----------------

18 February, 2027 is the Indri-3 milestone. See project-specific notes
for relevant deadlines.

.. _i-ff:

Feature freeze
--------------

The Indri-3 milestone marks feature freeze for projects following the
`release:cycle-with-rc`_ model. No featureful patch should be landed
after this point. Exceptions may be granted by the project PTL.

.. _release:cycle-with-rc: https://releases.openstack.org/reference/release_models.html#cycle-with-rc

.. _i-final-clientlib:

Final release for client libraries
----------------------------------

Client libraries should issue their final release during this week, to match
feature freeze.

.. _i-soft-sf:

Soft StringFreeze
-----------------

You are no longer allowed to accept proposed changes containing modifications
in user-facing strings. Such changes should be rejected by the review team and
postponed until the next series development opens (which should happen when RC1
is published).

.. _i-rf:

Requirements freeze
-------------------

After the Indri-3 milestone, only critical requirements and constraints
changes will be allowed. Freezing our requirements list gives packagers
downstream an opportunity to catch up and prepare packages for everything
necessary for distributions of the upcoming release. The requirements remain
frozen until the stable branches are created, with the release candidates.

.. _i-rc1:

RC1 target week
---------------

The week of 1 March, 2027 is the target date for projects following the
`release:cycle-with-rc`_ model to issue their first release candidate.

.. _i-hard-sf:

Hard StringFreeze
-----------------

This happens when the RC1 for the project is tagged. At this point, ideally
no strings are changed (or added, or removed), to give translators time to
finish up their efforts.

.. _i-finalrc:

Final RCs and intermediary releases
-----------------------------------

The week of 15 March, 2027 is the last week to issue release
candidates or intermediary releases before release week. During release week,
only final-release-critical releases will be accepted (at the discretion of
the release team).

.. _i-final:

2027.1 Indri release
--------------------

The 2027.1 Indri coordinated release will happen on Wednesday, 24 March, 2027.

.. _i-cycle-highlights:

Cycle Highlights
----------------

Cycle highlights need to be added to the release deliverables after the
feature freeze to be included in any marketing release messaging.
Highlights may be added after this point, but they will likely only be
useful for historical purposes.

See the `Project Team Guide`_ for more details and instructions on adding
these highlights.

For examples of previous release highlights:
`2025.2 Flamingo Highlights <https://releases.openstack.org/flamingo/highlights.html>`_.
`2026.1 Gazpacho Highlights <https://releases.openstack.org/gazpacho/highlights.html>`_.

.. _Project Team Guide: https://docs.openstack.org/project-team-guide/release-management.html#cycle-highlights


Project-specific events
=======================

