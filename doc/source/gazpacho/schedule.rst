================================
2026.1 Gazpacho Release Schedule
================================

.. note::

   Deadlines are generally the Thursday of the week on which they are noted
   below. Exceptions to this policy will be explicitly mentioned in the event
   description.

October 2, 2025 - April 1, 2026 (26 weeks)

.. datatemplate::
   :source: schedule.yaml
   :template: schedule_table.tmpl

.. ics::
   :source: schedule.yaml
   :name: Gazpacho

`Subscribe to iCalendar file <schedule.ics>`_

Cross-project events
====================

.. _g-vptg:

PTG (virtual)
-------------

From October 27 to 31, 2025 we'll have a virtual PTG to plan the
2026.1 Gazpacho release.

.. _g-1:

Gazpacho-1 milestone
--------------------

November 13, 2025 is the Gazpacho-1 milestone. See project-specific notes
for relevant deadlines.

.. _g-cycle-trail:

2025.2 Flamingo Cycle-Trailing Release Deadline
-----------------------------------------------

All projects following the cycle-trailing release model must release
their 2025.2 Flamingo deliverables by December 4, 2025.

.. _g-2:

Gazpacho-2 milestone
--------------------

January 8, 2026 is the Gazpacho-2 milestone. See project-specific notes
for relevant deadlines.

.. _g-mf:

Membership Freeze
-----------------

Projects must participate in at least two milestones in order to be considered
part of the release. Projects made official after the second milestone, or
which fail to produce milestone releases for at least one of the first and
second milestones as well as the third milestone, are therefore not considered
part of the release for the cycle. This does not apply to cycle-trailing
packaging / lifecycle management projects.

.. _g-extra-acs:

Extra-AC freeze
---------------

All contributions to OpenStack are valuable, but some are not expressed as
Gerrit code changes. That allow teams to list active contributors to their
projects and who do not have a code contribution this cycle, and therefore won't
automatically be considered an Active Contributor and allowed
to vote. This is done by adding extra-acs to
https://opendev.org/openstack/governance/src/branch/master/reference/projects.yaml
before the Extra-AC freeze date.

.. _g-final-lib:

Final release for non-client libraries
--------------------------------------

Libraries that are not client libraries (Oslo and others) should issue their
final release during this week. That allows to give time for last-minute
changes before feature freeze.

.. _g-3:

Gazpacho-3 milestone
---------------------

February 26, 2026 is the Gazpacho-3 milestone. See project-specific notes
for relevant deadlines.

.. _g-ff:

Feature freeze
--------------

The Gazpacho-3 milestone marks feature freeze for projects following the
`release:cycle-with-rc`_ model. No featureful patch should be landed
after this point. Exceptions may be granted by the project PTL.

.. _release:cycle-with-rc: https://releases.openstack.org/reference/release_models.html#cycle-with-rc

.. _g-final-clientlib:

Final release for client libraries
----------------------------------

Client libraries should issue their final release during this week, to match
feature freeze.

.. _g-soft-sf:

Soft StringFreeze
-----------------

You are no longer allowed to accept proposed changes containing modifications
in user-facing strings. Such changes should be rejected by the review team and
postponed until the next series development opens (which should happen when RC1
is published).

.. _g-rf:

Requirements freeze
-------------------

After the Gazpacho-3 milestone, only critical requirements and constraints
changes will be allowed. Freezing our requirements list gives packagers
downstream an opportunity to catch up and prepare packages for everything
necessary for distributions of the upcoming release. The requirements remain
frozen until the stable branches are created, with the release candidates.

.. _g-rc1:

RC1 target week
---------------

The week of March 9, 2026 is the target date for projects following the
`release:cycle-with-rc`_ model to issue their first release candidate.

.. _g-hard-sf:

Hard StringFreeze
-----------------

This happens when the RC1 for the project is tagged. At this point, ideally
no strings are changed (or added, or removed), to give translators time to
finish up their efforts.

.. _g-finalrc:

Final RCs and intermediary releases
-----------------------------------

The week of March 23, 2026 is the last week to issue release
candidates or intermediary releases before release week. During release week,
only final-release-critical releases will be accepted (at the discretion of
the release team).

.. _g-final:

2026.1 Gazpacho release
-----------------------

The 2026.1 Gazpacho coordinated release will happen on Wednesday, April 1, 2026.

.. _g-cycle-highlights:

Cycle Highlights
----------------

Cycle highlights need to be added to the release deliverables after the
feature freeze to be included in any marketing release messaging.
Highlights may be added after this point, but they will likely only be
useful for historical purposes.

See the `Project Team Guide`_ for more details and instructions on adding
these highlights.

For examples of previous release highlights:
`2024.2 Dalmatian Highlights <https://releases.openstack.org/dalmatian/highlights.html>`_.
`2025.1 Epoxy Highlights <https://releases.openstack.org/epoxy/highlights.html>`_.

.. _Project Team Guide: https://docs.openstack.org/project-team-guide/release-management.html#cycle-highlights


Project-specific events
=======================

Nova
----

.. _g-nova-spec-review-day:

Nova Spec Review Day
^^^^^^^^^^^^^^^^^^^^

On 27 November 2025 and 02 December 2025, Nova specifications targeting 2026.1 Gazpacho
implementation will be prioritized for reviews by the Nova core team.


.. _g-nova-spec-soft-freeze:

Nova Spec Soft Freeze
^^^^^^^^^^^^^^^^^^^^^

After 20 November 2025 (23:59 UTC), no new specs will be accepted.

.. _g-nova-spec-freeze:

Nova Spec Freeze
^^^^^^^^^^^^^^^^

All Nova Specs for features to be implemented in 2026.1 Gazpacho must be
approved by 4 December 2025 (23:59 UTC).

.. _g-nova-review-day:

Nova Implementation Review Day
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

On 15 January 2026 and 19 February 2026, Nova prioritized code changes will be reviewed by the Nova
core team.

