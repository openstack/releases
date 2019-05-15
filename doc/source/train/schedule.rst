======================
Train Release Schedule
======================

15 April 2019 - 16 October 2019 (27 weeks)

.. datatemplate::
   :source: schedule.yaml
   :template: schedule_table.tmpl

.. ics::
   :source: schedule.yaml
   :name: Train

`Subscribe to iCalendar file <schedule.ics>`_

.. note::

   Deadlines are generally the Thursday of the week on which they are noted
   above. Exceptions to this policy will be explicitly mentioned in the event
   description.

Cross-project events
====================

.. _t-goals-research:

Train Goals Research
--------------------

Pre-cycle planning and investigation into `the community-wide goals
for Train <https://governance.openstack.org/tc/goals/train/index.html>`__.

.. _t-1:

Train-1 milestone
-----------------

6 June, 2019 is the Train-1 milestone. See project-specific notes for relevant
deadlines.

.. _t-goals-ack:

Train Community Goals Acknowledgement
-------------------------------------

Teams should prepare their acknowledgement of `the community-wide
goals for
<https://governance.openstack.org/tc/goals/train/index.html>`__.

.. _t-summit:

Open Infrastructure Summit
--------------------------

The Open Infrastructure Summit happens during this week in Shanghai, China. It
will include a "Forum" in which people from all parts of our community will
gather to give feedback on the last release (Stein) and discuss requirements
for the next development cycle (U).

.. _t-2:

Train-2 milestone
-----------------

25 July, 2019 is the Train-2 milestone. See project-specific notes for relevant
deadlines.

.. _t-final-lib:

Final release for non-client libraries
--------------------------------------

Libraries that are not client libraries (Oslo and others) should issue their
final release during this week. That allows to give time for last-minute
changes before feature freeze.

.. _t-3:

Train-3 milestone
-----------------

12 September, 2019 is the Train-3 milestone. See project-specific notes for
relevant deadlines.

.. _t-goals-complete:

Train Community Goals Completed
-------------------------------

Teams should prepare their documentation for completing `the
community-wide goals for Train
<https://governance.openstack.org/tc/goals/train/index.html>`__.

.. _t-extra-atcs:

Extra-ATCs deadline
-------------------
Project teams should identify contributors who have had a significant impact
this cycle but who would not qualify for ATC status using the regular process
because they have not submitted a patch. Those names should be added to the
governance repo for consideration as ATC for the future.

.. _t-ff:

Feature freeze
--------------

The Train-3 milestone marks feature freeze for projects following the
`release:cycle-with-rc`_ model. No featureful patch should be landed
after this point. Exceptions may be granted by the project PTL.

.. _release:cycle-with-rc: https://releases.openstack.org/reference/release_models.html#cycle-with-rc

.. _t-rf:

Requirements freeze
-------------------

After the Train-3 milestone, only critical requirements and constraints changes
will be allowed. Freezing our requirements list gives packagers downstream an
opportunity to catch up and prepare packages for everything necessary for
distributions of the upcoming release. The requirements remain frozen until the
stable branches are created, with the release candidates.

.. _t-final-clientlib:

Final release for client libraries
----------------------------------

Client libraries should issue their final release during this week, to match
feature freeze.

.. _t-soft-sf:

Soft StringFreeze
-----------------

You are no longer allowed to accept proposed changes containing modifications
in user-facing strings. Such changes should be rejected by the review team and
postponed until the next series development opens (which should happen when RC1
is published).

.. _t-mf:

Membership Freeze
-----------------

Projects must participate in at least two milestones in order to be considered
part of the release. Projects made official after the second milestone, or
which fail to produce milestone releases for at least one of the first and
second milestones as well as the third milestone, are therefore not considered
part of the release for the cycle. This does not apply to cycle-trailing
packaging / lifecycle management projects.

.. _t-rc1:

RC1 target week
---------------

The week of September 23-27 is the target date for projects following the
`release:cycle-with-rc`_ model to issue their first release candidate.

.. _t-hard-sf:

Hard StringFreeze
-----------------

This happens when the RC1 for the project is tagged. At this point, ideally
no strings are changed (or added, or removed), to give translators time to
finish up their efforts.

.. _t-finalrc:

Final RCs and intermediary releases
-----------------------------------

The week of October 7-11 is the last week to issue release candidates or
intermediary releases before release week. During release week, only
final-release-critical releases will be accepted (at the discretion of the
release team).

.. _t-cycle-highlights:

Cycle highlights marketing deadline
-----------------------------------

Cycle highlights need to be added to the release deliverables by feature freeze to
be included in any marketing release messaging. Highlights may be added after
this point, but they will likely only be useful for historical purposes.

See the `project team guide <https://docs.openstack.org/project-team-guide/release-management.html#cycle-highlights>`_
for more details and instructions on adding these highlights.


.. _t-final:

Train release
-------------

The Train coordinated release will happen on 16 October 2019.

.. _t-trailing-release:

Train cycle-trailing release deadline
-------------------------------------

The release deadline for projects using the release:cycle-trailing model that
follow the main release cycle is set to 17 December, 2019.

Project-specific events
=======================

PTL Elections
-------------

Keystone
--------

.. _t-keystone-spec-proposal-freeze:

Keystone Spec Proposal Freeze
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All Keystone specs targeted to Train must be submitted to the keystone-specs
repository by the end of the week.

.. _t-keystone-spec-freeze:

Keystone Spec Freeze
^^^^^^^^^^^^^^^^^^^^

All Keystone specs targeted to Train must be approved by the end of the week.

.. _t-keystone-fpfreeze:

Keystone Feature Proposal Freeze
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All new Keystone features must be proposed and substantially completed, with
unit tests and documentation by the end of the week.

.. _t-keystone-ffreeze:

Keystone Feature Freeze
^^^^^^^^^^^^^^^^^^^^^^^

All new Keystone features must be merged by the end of the week.

Nova
----

.. _t-nova-spec-freeze:

Nova Spec Freeze
^^^^^^^^^^^^^^^^
All Nova specs targeted to Train must be approved by Thursday.

.. _t-nova-ffreeze:

Nova Feature Freeze
^^^^^^^^^^^^^^^^^^^
All new Nova features must be approved by Thursday.

Oslo
----

.. _t-oslo-feature-freeze:

Oslo Feature Freeze
^^^^^^^^^^^^^^^^^^^

All new Oslo features must be proposed and substantially complete, with unit
tests by the end of the week.

Manila
------

.. _t-manila-spec-freeze:

Manila Spec Freeze
^^^^^^^^^^^^^^^^^^

All Manila specs targeted to Train must be approved by the end of the week.

.. _t-manila-driver-deadline:

Manila Driver Deadline
^^^^^^^^^^^^^^^^^^^^^^

By the end of the week all new backend drivers for Manila must be substantially
complete, with unit tests, and passing 3rd party CI.  Drivers do not have to
actually merge until feature freeze.

.. _t-manila-fpfreeze:

Manila Feature Proposal Freeze
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All new Manila features must be proposed and substantially completed, with
unit tests and documentation by the end of the week.

.. _t-manila-ffreeze:

Manila Feature Freeze
^^^^^^^^^^^^^^^^^^^^^

All new Manila features must be merged by the end of the week.

Cinder
------

.. _t-cinder-spec-freeze:

Cinder Spec Freeze
^^^^^^^^^^^^^^^^^^

All Cinder Specs must be approved by 25 Jul 2019 (23:59 UTC).

.. _t-cinder-driver-deadline:

Cinder New Driver Merge Deadline
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The deadline for merging a new backend driver to Cinder is 25 Jul 2019 (23:59 UTC).
New drivers must be complete with unit tests at this point in time.  The backend
driver must also have a 3rd Party CI running reliably and the driver must be
merged at this point to be included in the Train release.

.. _t-cinder-target-driver-deadline:

Cinder New Target Driver Merge Deadline
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The deadline for merging a new target driver to Cinder is 25 Jul 2019 (23:59 UTC).
New target drivers must be complete with unit tests at this point in time.  The target
driver must also have a 3rd Party CI running reliably and the target driver must
be merged at this point to be included in the Train release.

.. _t-cinder-py37-ci-running:

Cinder 3rd Party CIs Running Py37
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In preparation for OpenStack's move to Python 3.x we are requiring that all
vendors demonstrate their driver running Py37 tests by 25 Jul 2019 (23:59 UTC).
Vendors who do not meet this reuqirement will have a patch marking their
driver as unsupported submitted.

.. _t-cinder-py37-ci-working:

Cinder 3rd Party CIs Passing Py37 Testing
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All vendors must demonstrate that their driver can execute 3rd Party CI
with Py37 by 12 Sep 2019 (23:59 UTC) or their driver will be marked as
unsupported.

.. _t-cinder-fp-freeze:

Cinder Feature Proposal Freeze
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All new Cinder features must be proposed and substantially complete with unit
tests by 12 Sep 2019 (23:59 UTC).
