========================
 Ocata Release Schedule
========================

31 October 2016 - 24 February 2017 (16 weeks)

.. datatemplate::
   :source: schedule.yaml
   :template: schedule_table.tmpl

.. ics::
   :source: schedule.yaml
   :name: Ocata

`Subscribe to iCalendar file <schedule.ics>`__

.. note::

   With the exception of the final release date and cycle-trailing
   release date, deadlines are generally the Thursday of the week on
   which they are noted above. For example, the Feature Freeze in week
   R-4 is on 26 January. Exceptions to this policy will be explicitly
   mentioned in the event description.

Cross-project events
====================

.. _o-goals-research:

Ocata Goals Research
--------------------

Pre-cycle planning and investigation into `the community-wide goals
for Ocata <https://governance.openstack.org/tc/goals/ocata/index.html>`__.

.. _o-design-summit:

Ocata Design Summit
--------------------

`Planning in Barcelona <https://www.openstack.org/summit/barcelona-2016/>`__

.. _p-ptg0:

Pike Project Team Gathering (PTG)
---------------------------------

`Project team gathering <https://www.openstack.org/ptg>`__ for the Pike
release 20-24 February 2017 in Atlanta, Georgia.

.. _o-1:

Ocata-1 milestone
------------------

17 November is the ocata-1 milestone window for projects following the
:ref:`model-cycle-with-milestones` model.

.. _o-goals-ack:

Ocata Community Goals Acknowledgement
-------------------------------------

Teams should prepare their acknowledgement of `the community-wide
goals for Ocata
<https://governance.openstack.org/tc/goals/ocata/index.html>`__.

.. _o-2:

Ocata-2 milestone
------------------

15 December is the ocata-2 milestone window for projects following the
:ref:`model-cycle-with-milestones` model.

.. _o-final-lib:

Final release for non-client libraries
--------------------------------------

Libraries that are not client libraries (Oslo and others) should issue their
final release during this week. That allows to give time for last-minute
changes before feature freeze.

.. _o-3:

Ocata-3 milestone
------------------

26 January is the ocata-3 milestone window for projects following the
:ref:`model-cycle-with-milestones` model.

.. _o-goals-complete:

Ocata Community Goals Completed
-------------------------------

Teams should prepare their documentation for completing `the
community-wide goals for Ocata
<https://governance.openstack.org/tc/goals/ocata/index.html>`__.

.. _o-extra-atcs:

Extra-ATCs deadline
-------------------

Project teams should identify contributors who have had a significant
impact this cycle but who would not qualify for ATC status using the
regular process because they have not submitted a patch. Those names
should be added to the governance repo for consideration as ATC for
the future.

Although extra ATCs can be nominated at any point, there is a deadline
to be included in electorate for the next release cycle.  The ATC list
needs to be approved by the TC by (TBD), and in order to appear on the
TC agenda to be discussed, the proposals need to be submitted to the
``openstack/governance`` repository by (TBD).

.. _o-ff:

Feature freeze
--------------

The ocata-3 milestone marks feature freeze for projects following the
:ref:`model-cycle-with-milestones` model. No featureful patch should be landed
after this point. Exceptions may be granted by the project PTL.

.. _o-rf:

Requirements freeze
-------------------

After the ocata-3 milestone, only critical requirements and
constraints changes will be allowed. Freezing our requirements list
gives packagers downstream an opportunity to catch up and prepare
packages for everything necessary for distributions of the upcoming
release. The requirements remain frozen until the stable branches are
created, with the release candidates.

.. _o-final-clientlib:

Final release for client libraries
----------------------------------

Client libraries should issue their final release during this week, to match
feature freeze.

.. _o-soft-sf:

Soft StringFreeze
-----------------

You are no longer allowed to accept proposed changes containing modifications
in user-facing strings. Such changes should be rejected by the review team
and postponed until the next series development opens (which should happen
when RC1 is published).

.. _o-mf:

Membership Freeze
-----------------

Projects must participate in at least two milestones in order to be
considered part of the release. Projects made official after the
second milestone, or which fail to produce milestone releases for at
least one of the first and second milestones as well as the third
milestone, are therefore not considered part of the release for the
cycle.

.. _o-rc1:

RC1 target week
---------------

The week of 30 January - 3 February is the target date for projects
following the :ref:`model-cycle-with-milestones` model to issue their
first release candidate, with a deadline of 2 February.

.. _o-hard-sf:

Hard StringFreeze
-----------------

This happens when the RC1 for the project is tagged. At this point, ideally
no strings are changed (or added, or removed), to give translator time to
finish up their efforts.

.. _o-finalrc:

Final RCs and intermediary releases
-----------------------------------

The week of 13-17 February is the last week to issue release
candidates or intermediary releases before release week. During
release week, only final-release-critical releases will be accepted
(at the discretion of the release team).

.. _o-release:

Ocata release
--------------

The Ocata coordinated release will happen on 22 February.

.. _o-trailing:

Ocata cycle-trailing Deadline
-----------------------------

The deadline for projects using the release:cycle-trailing model that
follow the main release cycle is 9 March.

Project-specific events
=======================

Elections
---------

.. _p-ptl-nomination:

Pike PTLs self-nomination
^^^^^^^^^^^^^^^^^^^^^^^^^

Project team lead candidates for the Pike cycle should announce their
candidacy during this week. Those dates should be confirmed by the Pike
PTL election officials.

.. _p-ptl-election:

Pike cycle PTLs election
^^^^^^^^^^^^^^^^^^^^^^^^

Election week for Project team leads (where an election must be held to
determine the winner). Those dates should be confirmed by the Pike PTL
election officials.

Cinder
------

.. _o-cinder-nddeadline:

Cinder New Backend Driver Deadline
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The deadline for getting a new backend driver added to Cinder is 14th
December, 2016. All review issues must be addressed and third party CI
must be reporting and stable with enough time for reviewers prior to the
deadline. Meeting these requirements on the 14th does not guarantee core
reviewers will have enough time to merge the driver.

.. _o-cinder-spec-freeze:

Cinder Spec Freeze
^^^^^^^^^^^^^^^^^^

All Cinder specs must be approved by 14th December, 2016.

Glance
------

The following deadlines are specific to the Glance project.

.. _o-glance-spec-prop:

Glance Spec Proposal Freeze
^^^^^^^^^^^^^^^^^^^^^^^^^^^

All Glance, python-glanceclient, and glance_store specs must be
proposed as patches to the glance-specs repository by 23:59 UTC
on Thursday 10 November 2016.

.. _o-glance-spec-freeze:

Glance Spec Freeze
^^^^^^^^^^^^^^^^^^

All Glance, python-glanceclient, and glance_store specs must be
merged into the glance-specs repository by 23:59 UTC on Friday
25 November 2016.

Nova
----

The deadlines below are specific to the Nova project.

.. _o-nova-spec-freeze:

Nova Spec Freeze
^^^^^^^^^^^^^^^^

All Nova specs must be approved by 17th November, 2016.


Manila
------

.. _o-manila-spec-frz1:

Manila Low-Priority Spec Freeze
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All Manila specs must be approved by 17th November, 2016, unless they
are officially designated high-priority.

.. _o-manila-spec-frz2:

Manila High-Priority Spec Freeze
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All high-priority Manila specs must be approved by 15th December, 2016.

.. _o-manila-drv-freeze:

Manila Driver Proposal Freeze
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All new Manila drivers must be proposed by 19th December, 2016.

Horizon
-------

.. _o-horizon-ff:

Horizon Feature Freeze
^^^^^^^^^^^^^^^^^^^^^^

Horizon will enter feature freeze a week before other projects
to allow plugin authors an additional week to react to feature
changes.

Trove
-----

The deadlines below are specific to the Trove project.

.. _o-trove-spec-prop:

Trove Spec Proposal Deadline
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Submit all Trove specs for the release by the end of this week (for
review) in trove-specs repository.

.. _o-trove-spec-freeze:

Trove Spec Freeze
^^^^^^^^^^^^^^^^^

All Trove specs for the release must be approved by the end of this
week.

.. _o-trove-guest-req:

Trove Guest Requirements Freeze
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Freeze the requirements for all guest agents by this date and make the
requirements file for guests.

.. _o-trove-client-soft:

Trove Client Soft Freeze
^^^^^^^^^^^^^^^^^^^^^^^^

All major features for the python-troveclient must be reviewed and
approved by the end of this week, this gives us one additional week to
address any issues with dependencies.

Keystone
--------

The deadlines below are specific to the Keystone project.

.. _o-key-spec-prop:

Keystone Spec Proposal Deadline
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Submit all keystone specs for the release by the end of this week (for review)
in keystone-specs repository.

.. _o-key-spec-freeze:

Keystone Spec Freeze
^^^^^^^^^^^^^^^^^^^^

All keystone specs for the release must be approved by the end of this week.

.. _o-key-feature-prop:

Keystone Feature Proposal Deadline
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All major keystone features for the release must be proposed by the end of
this week.

.. _o-key-feature-freeze:

Keystone Feature Proposal Freeze
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All major features for keystone must be reviewed and approved by the end of
this week.
