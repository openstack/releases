================================
2025.2 Flamingo Release Schedule
================================

.. note::

   Deadlines are generally the Thursday of the week on which they are noted
   below. Exceptions to this policy will be explicitly mentioned in the event
   description.

April 2, 2024 - October 1, 2025 (26 weeks)

.. datatemplate::
   :source: schedule.yaml
   :template: schedule_table.tmpl

.. ics::
   :source: schedule.yaml
   :name: Flamingo

`Subscribe to iCalendar file <schedule.ics>`_

Cross-project events
====================

.. _f-vptg:

PTG (virtual)
-------------

From April 7 to 11, 2025 we'll have a virtual PTG to plan the
2025.2 Flamingo release schedule.

.. _f-1:

Flamingo-1 milestone
---------------------

May 15, 2025 is the Flamingo-1 milestone. See project-specific notes
for relevant deadlines.

.. _f-cycle-trail:

2025.1 Epoxy Cycle-Trailing Release Deadline
----------------------------------------------

All projects following the cycle-trailing release model must release
their 2025.1 Epoxy deliverables by June 5, 2025.

.. _f-2:

Flamingo-2 milestone
---------------------

July 3, 2025 is the Flamingo-2 milestone. See project-specific notes
for relevant deadlines.

.. _f-mf:

Membership Freeze
-----------------

Projects must participate in at least two milestones in order to be considered
part of the release. Projects made official after the second milestone, or
which fail to produce milestone releases for at least one of the first and
second milestones as well as the third milestone, are therefore not considered
part of the release for the cycle. This does not apply to cycle-trailing
packaging / lifecycle management projects.

.. _f-extra-acs:

Extra-AC freeze
---------------

All contributions to OpenStack are valuable, but some are not expressed as
Gerrit code changes. That allow teams to list active contributors to their
projects and who do not have a code contribution this cycle, and therefore won't
automatically be considered an Active Contributor and allowed
to vote. This is done by adding extra-acs to
https://opendev.org/openstack/governance/src/branch/master/reference/projects.yaml
before the Extra-AC freeze date.

.. _f-final-lib:

Final release for non-client libraries
--------------------------------------

Libraries that are not client libraries (Oslo and others) should issue their
final release during this week. That allows to give time for last-minute
changes before feature freeze.

.. _f-3:

Flamingo-3 milestone
---------------------

August 28, 2025 is the Flamingo-3 milestone. See project-specific notes
for relevant deadlines.

.. _f-ff:

Feature freeze
--------------

The Flamingo-3 milestone marks feature freeze for projects following the
`release:cycle-with-rc`_ model. No featureful patch should be landed
after this point. Exceptions may be granted by the project PTL.

.. _release:cycle-with-rc: https://releases.openstack.org/reference/release_models.html#cycle-with-rc

.. _f-final-clientlib:

Final release for client libraries
----------------------------------

Client libraries should issue their final release during this week, to match
feature freeze.

.. _f-soft-sf:

Soft StringFreeze
-----------------

You are no longer allowed to accept proposed changes containing modifications
in user-facing strings. Such changes should be rejected by the review team and
postponed until the next series development opens (which should happen when RC1
is published).

.. _f-rf:

Requirements freeze
-------------------

After the Flamingo-3 milestone, only critical requirements and constraints
changes will be allowed. Freezing our requirements list gives packagers
downstream an opportunity to catch up and prepare packages for everything
necessary for distributions of the upcoming release. The requirements remain
frozen until the stable branches are created, with the release candidates.

.. _f-rc1:

RC1 target week
---------------

The week of September 8, 2025 is the target date for projects following the
`release:cycle-with-rc`_ model to issue their first release candidate.

.. _f-hard-sf:

Hard StringFreeze
-----------------

This happens when the RC1 for the project is tagged. At this point, ideally
no strings are changed (or added, or removed), to give translators time to
finish up their efforts.

.. _f-finalrc:

Final RCs and intermediary releases
-----------------------------------

The week of September 22, 2025 is the last week to issue release
candidates or intermediary releases before release week. During release week,
only final-release-critical releases will be accepted (at the discretion of
the release team).

.. _f-final:

2025.2 Flamingo release
-----------------------

The 2025.2 Flamingo coordinated release will happen on Wednesday, October 1, 2025.

.. _f-cycle-highlights:

Cycle Highlights
----------------

Cycle highlights need to be added to the release deliverables after the
feature freeze to be included in any marketing release messaging.
Highlights may be added after this point, but they will likely only be
useful for historical purposes.

See the `Project Team Guide`_ for more details and instructions on adding
these highlights.

For examples of previous release highlights:
`2024.1 Caracal Highlights <https://releases.openstack.org/caracal/highlights.html>`_.
`2024.2 Dalmatian Highlights <https://releases.openstack.org/dalmatian/highlights.html>`_.

.. _Project Team Guide: https://docs.openstack.org/project-team-guide/release-management.html#cycle-highlights


Project-specific events
=======================

OpenStackSDK
------------

.. _f-openstackclient-freeze:

python-openstackclient Feature Freeze
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All new python-openstackclient features should be proposed and completed,
with unit tests by the end of the week. Support for new microversions may be
added after this date, but no breaking changes will be permitted.

