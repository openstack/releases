=======================
 Pike Release Schedule
=======================

20 February 2017 - 1 September 2017 (27 weeks)

.. datatemplate::
   :source: schedule.yaml
   :template: schedule_table.tmpl

.. ics::
   :source: schedule.yaml
   :name: Pike

`Subscribe to iCalendar file <schedule.ics>`__

.. note::

   With the exception of the final release date and cycle-trailing
   release date, deadlines are generally the Thursday of the week on
   which they are noted above. For example, the Feature Freeze in week
   R-5 is on 27 July. Exceptions to this policy will be explicitly
   mentioned in the event description.

Cross-project events
====================

.. _p-goals-research:

Pike Goals Research
--------------------

Pre-cycle planning and investigation into `the community-wide goals
for Pike <https://governance.openstack.org/tc/goals/pike/index.html>`__.

.. _p-ptg:

Pike Project Team Gathering (PTG)
---------------------------------

`Project team gathering <https://www.openstack.org/ptg>`__ for the Pike
release 20-24 February 2017 in Atlanta, Georgia.

.. _p-1:

Pike-1 milestone
----------------

13 April 2017 is the Pike-1 milestone window for projects following the
`release:cycle-with-milestones`_ model.

.. _release:cycle-with-milestones: https://governance.openstack.org/tc/reference/tags/release_cycle-with-milestones.html

.. _p-goals-ack:

Pike Community Goals Acknowledgement
------------------------------------

Teams should prepare their acknowledgement of `the community-wide
goals for Pike
<https://governance.openstack.org/tc/goals/pike/index.html>`__.

.. _p-summit:

OpenStack Summit
----------------

The OpenStack Summit happens during this week in Boston, USA. It will include
a "Forum" in which people from all parts of our community will gather to give
feedback on the last release (Ocata) and discuss requirements for the next
development cycle (Queens).

.. _p-2:

Pike-2 milestone
----------------

8 June 2017 is the Pike-2 milestone window for projects following the
`release:cycle-with-milestones`_ model.

.. _p-final-lib:

Final release for non-client libraries
--------------------------------------

Libraries that are not client libraries (Oslo and others) should issue their
final release during this week. That allows to give time for last-minute
changes before feature freeze.

.. _p-3:

Pike-3 milestone
----------------

27 July 2017 is the Pike-3 milestone window for projects following the
`release:cycle-with-milestones`_ model.

.. _p-goals-complete:

Pike Community Goals Completed
------------------------------

Teams should prepare their documentation for completing `the
community-wide goals for Pike
<https://governance.openstack.org/tc/goals/pike/index.html>`__.

.. _p-extra-atcs:

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

.. _p-ff:

Feature freeze
--------------

The Pike-3 milestone marks feature freeze for projects following the
`release:cycle-with-milestones`_ model. No featureful patch should be landed
after this point. Exceptions may be granted by the project PTL.

.. _p-rf:

Requirements freeze
-------------------

After the Pike-3 milestone, only critical requirements and
constraints changes will be allowed. Freezing our requirements list
gives packagers downstream an opportunity to catch up and prepare
packages for everything necessary for distributions of the upcoming
release. The requirements remain frozen until the stable branches are
created, with the release candidates.

.. _p-final-clientlib:

Final release for client libraries
----------------------------------

Client libraries should issue their final release during this week, to
match feature freeze.

.. _p-soft-sf:

Soft StringFreeze
-----------------

You are no longer allowed to accept proposed changes containing
modifications in user-facing strings. Such changes should be rejected
by the review team and postponed until the next series development
opens (which should happen when RC1 is published).

.. _p-mf:

Membership Freeze
-----------------

Projects must participate in at least two milestones in order to be
considered part of the release. Projects made official after the
second milestone, or which fail to produce milestone releases for at
least one of the first and second milestones as well as the third
milestone, are therefore not considered part of the release for the
cycle.

.. _p-rc1:

RC1 target week
---------------

The week of 7-11 August 2017 is the target date for projects
following the `release:cycle-with-milestones`_ model to issue their
first release candidate, with a deadline of 10 August 2017.

.. _p-hard-sf:

Hard StringFreeze
-----------------

This happens when the RC1 for the project is tagged. At this point, ideally
no strings are changed (or added, or removed), to give translator time to
finish up their efforts.

.. _p-finalrc:

Final RCs and intermediary releases
-----------------------------------

The week of 21 August 2017 is the last week to issue release candidates or
intermediary releases before release week. During release week, only
final-release-critical releases will be accepted (at the discretion of
the release team).

.. _p-release:

Pike release
------------

The Pike coordinated release will happen on 30 August 2017.

.. _p-trailing-ff:

Pike cycle-trailing feature freeze
----------------------------------

The release deadline for projects using the release:cycle-trailing model that
follow the main release cycle.

.. _p-trailing-rc:

Pike cycle-trailing RC deadline
-------------------------------

The deadline for publishing a first release candidate for projects using the
release:cycle-trailing model that follow the main release cycle.

.. _p-trailing-release:

Pike cycle-trailing release deadline
------------------------------------

The release deadline for projects using the release:cycle-trailing model that
follow the main release cycle.

Project-specific events
=======================

Elections
---------

.. _q-ptl-nomination:

Queens PTLs self-nomination
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Project team lead candidates for the Queens cycle should announce their
candidacy during this week. Those dates should be confirmed by the Pike
PTL election officials.

.. _q-ptl-election:

Queens cycle PTLs election
^^^^^^^^^^^^^^^^^^^^^^^^^^

Election week for Project team leads (where an election must be held to
determine the winner). Those dates should be confirmed by the Queens PTL
election officials.


Cinder
------

.. _p-cinder-nddeadline:

Cinder New Backend Driver Deadline
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The deadline for getting a new backend driver added to Cinder is the 7th of
June, 2017. All review issues must be addressed and third party CI must be
reporting and stable with enough time for reviewers prior to the deadline.
Meeting these requirements on the 14th does not guarantee core reviewers will
have enough time to merge the driver.

Note: This is the Wednesday of the milestone week, while the milestone itself
is typically targeted for Thursday.

.. _p-cinder-spec-freeze:

Cinder Spec Freeze
^^^^^^^^^^^^^^^^^^

All Cinder specs must be approved by the 7th of June, 2017.

Note: This is the Wednesday of the milestone week, while the milestone itself
is typically targeted for Thursday.

Glance
------

.. _p-glance-spec-prop:

Glance Spec Proposal Freeze
^^^^^^^^^^^^^^^^^^^^^^^^^^^

All Glance, python-glanceclient, and glance_store specs must be proposed as
patches to the glance-specs repository by 13:59 UTC on Thursday 30 March 2017
(that is, before the weekly Glance meeting begins).  This allows two weeks to
make revisions and work out problems before the Glance Spec Freeze.

.. _p-glance-spec-freeze:

Glance Spec Freeze
^^^^^^^^^^^^^^^^^^

All Glance, python-glanceclient, and glance_store specs must be merged into
the glance-specs repository by 23:59 on Friday 14 April 2017.  This is
necessary but not sufficient condition for inclusion in the Pike release.

Keystone
--------

.. _p-keystone-spec-proposal-freeze:

Keystone Spec Proposal Freeze
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All Keystone specs targeted to Pike must be submitted to the keystone-specs
repository by the end of the week.

.. _p-keystone-spec-freeze:

Keystone Spec Freeze
^^^^^^^^^^^^^^^^^^^^

All Keystone specs targeted to Pike must be approved by the end of the week.

.. _p-keystone-fpfreeze:

Keystone Feature Proposal Freeze
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All new Keystone features must be proposed and substantially completed, with
unit tests and documentation by the end of the week.

.. _p-keystone-ffreeze:

Keystone Feature Freeze
^^^^^^^^^^^^^^^^^^^^^^^

All new Keystone features must be merged by the end of the week.

Manila
------

.. _p-manila-nddeadline:

Manila New Driver Submission Deadline
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The deadline for submitting new backend drivers to to Manila is 5 June 2017
(23:59 UTC). New drivers must be substantially complete, with unit tests, and
passing 3rd party CI by this date. Drivers do not need to be merged until the
feature freeze date, but drivers that don't meet this deadline will not be
considered at all for Pike.

.. _p-manila-spec-freeze:

Manila Spec Freeze
^^^^^^^^^^^^^^^^^^

All Manila specs must be approved by 13 Apr 2017 (23:59 UTC).

.. _p-manila-fpfreeze:

Manila Feature Proposal Freeze
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All new Manila features must be proposed and substantially complete, with unit
tests by 10 July 2017 (23:59 UTC).

Nova
----

.. _p-nova-spec-freeze:

Nova Spec Freeze
^^^^^^^^^^^^^^^^

All Nova specs must be approved by Thursday April 13th, 2017.
