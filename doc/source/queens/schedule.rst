=========================
 Queens Release Schedule
=========================

4 September 2017 - 2 March 2018 (26 weeks)

.. datatemplate::
   :source: schedule.yaml
   :template: schedule_table.tmpl

.. ics::
   :source: schedule.yaml
   :name: Queens

`Subscribe to iCalendar file <schedule.ics>`__

.. note::

   With the exception of the final release date and cycle-trailing
   release date, deadlines are generally the Thursday of the week on
   which they are noted above. For example, the Feature Freeze in week
   R-5 is on 25 January. Exceptions to this policy will be explicitly
   mentioned in the event description.

Cross-project events
====================

.. _q-goals-research:

Queens Goals Research
---------------------

Pre-cycle planning and investigation into `the community-wide goals
for Queens <https://governance.openstack.org/tc/goals/queens/index.html>`__.

.. _q-ptg:

Queens Project Team Gathering (PTG)
-----------------------------------

`Project team gathering <https://www.openstack.org/ptg>`__ for the Queens
cycle 11-15 September 2018 in Denver, Colorado.

.. _q-1:

Queens-1 milestone
------------------

19 October 2017 is the Queens-1 milestone window for projects following the
`release:cycle-with-milestones`_ model.

.. _release:cycle-with-milestones: https://governance.openstack.org/tc/reference/tags/release_cycle-with-milestones.html

.. _q-goals-ack:

Queens Community Goals Acknowledgement
--------------------------------------

Teams should prepare their acknowledgement of `the community-wide
goals for 
<https://governance.openstack.org/tc/goals/queens/index.html>`__.

.. _q-summit:

OpenStack Summit
----------------

The OpenStack Summit happens during this week in Sydney, Australia. It will
include a "Forum" in which people from all parts of our community will gather
to give feedback on the last release (Pike) and discuss requirements for the
next development cycle (Rocky).

.. _q-2:

Queens-2 milestone
------------------

7 December 2017 is the Queens-2 milestone window for projects following the
`release:cycle-with-milestones`_ model.

.. _q-final-lib:

Final release for non-client libraries
--------------------------------------

Libraries that are not client libraries (Oslo and others) should issue their
final release during this week. That allows to give time for last-minute
changes before feature freeze.

.. _q-3:

Queens-3 milestone
------------------

25 January 2018 is the Queens-3 milestone window for projects following the
`release:cycle-with-milestones`_ model.

.. _q-goals-complete:

Queens Community Goals Completed
--------------------------------

Teams should prepare their documentation for completing `the
community-wide goals for Queens
<https://governance.openstack.org/tc/goals/queens/index.html>`__.

.. _q-extra-atcs:

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

.. _q-ff:

Feature freeze
--------------

The Queens-3 milestone marks feature freeze for projects following the
`release:cycle-with-milestones`_ model. No featureful patch should be landed
after this point. Exceptions may be granted by the project PTL.

.. _q-rf:

Requirements freeze
-------------------

After the Queens-3 milestone, only critical requirements and
constraints changes will be allowed. Freezing our requirements list
gives packagers downstream an opportunity to catch up and prepare
packages for everything necessary for distributions of the upcoming
release. The requirements remain frozen until the stable branches are
created, with the release candidates.

.. _q-final-clientlib:

Final release for client libraries
----------------------------------

Client libraries should issue their final release during this week, to
match feature freeze.

.. _q-soft-sf:

Soft StringFreeze
-----------------

You are no longer allowed to accept proposed changes containing
modifications in user-facing strings. Such changes should be rejected
by the review team and postponed until the next series development
opens (which should happen when RC1 is published).

.. _q-mf:

Membership Freeze
-----------------

Projects must participate in at least two milestones in order to be
considered part of the release. Projects made official after the
second milestone, or which fail to produce milestone releases for at
least one of the first and second milestones as well as the third
milestone, are therefore not considered part of the release for the
cycle.

.. _q-rc1:

RC1 target week
---------------

The week of 5 February 2018 is the target date for projects
following the `release:cycle-with-milestones`_ model to issue their
first release candidate, with a deadline of 8 February 2018.

.. _q-hard-sf:

Hard StringFreeze
-----------------

This happens when the RC1 for the project is tagged. At this point, ideally
no strings are changed (or added, or removed), to give translator time to
finish up their efforts.

.. _q-finalrc:

Final RCs and intermediary releases
-----------------------------------

The week of 19 February 2018 is the last week to issue release candidates or
intermediary releases before release week. During release week, only
final-release-critical releases will be accepted (at the discretion of
the release team).

.. _q-release:

Queens release
--------------

The Queens coordinated release will happen on 28 February 2018.

.. _q-trailing-ff:

Queens cycle-trailing feature freeze
------------------------------------

The release deadline for projects using the release:cycle-trailing model that
follow the main release cycle.

.. _q-trailing-rc:

Queens cycle-trailing RC deadline
---------------------------------

The deadline for publishing a first release candidate for projects using the
release:cycle-trailing model that follow the main release cycle.

.. _q-trailing-release:

Queens cycle-trailing release deadline
--------------------------------------

The release deadline for projects using the release:cycle-trailing model that
follow the main release cycle.

.. _n-final-library-releases:

Newton library releases
-----------------------

Last week for libraries to be released, integrated in upper-constraints to be tested before Newton
EOL.

.. _n-eol:

Newton EOL
----------

Newton projects will be EOL'd this week.

Project-specific events
=======================

Elections
---------

.. _r-ptl-nomination:

Rocky PTLs self-nomination
^^^^^^^^^^^^^^^^^^^^^^^^^^

Project team lead candidates for the Queens cycle should announce their
candidacy during this week. Those dates should be confirmed by the Rocky
PTL election officials.

.. _r-ptl-election:

Rocky cycle PTLs election
^^^^^^^^^^^^^^^^^^^^^^^^^

Election week for Project team leads (where an election must be held to
determine the winner). Those dates should be confirmed by the Rocky PTL
election officials.

Manila
------

.. _q-manila-driver-deadline:

Manila New Driver Submission Deadline
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The deadline for submitting new backend drivers to to Manila is 4 Dec 2017
(23:59 UTC). New drivers must be substantially complete, with unit tests, and
passing 3rd party CI by this date. Drivers do not need to be merged until the
feature freeze date, but drivers that don't meet this deadline will not be
considered at all for Queens.

.. _q-manila-spec-freeze:

Manila Spec Freeze
^^^^^^^^^^^^^^^^^^

All Manila specs must be approved by 19 Oct 2017 (23:59 UTC).

.. _q-manila-fp-freeze:

Manila Feature Proposal Freeze
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All new Manila features must be proposed and substantially complete, with unit
tests by 8 Jan 2018 (23:59 UTC).


Glance
------

.. _q-glance-spec-proposal-freeze:

Glance Spec Proposal Freeze
^^^^^^^^^^^^^^^^^^^^^^^^^^^

All Glance, python-glanceclient, and glance_store specs must be proposed as
patches to the glance-specs repository by 13:00 UTC on Thursday 28 September
2017 (that is, one hour before the weekly Glance meeting begins).  While this
only allows one week for review and revisions before the Glance Spec Freeze,
you can make sure you have extra review time by submitting your patch early.

.. _q-glance-spec-freeze:

Glance Spec Freeze
^^^^^^^^^^^^^^^^^^

All Glance, python-glanceclient, and glance_store specs must be merged into
the glance-specs repository by 23:59 on Friday 6 October 2017.  This is a
necessary but not sufficient condition for inclusion in the Queens release.

Cinder
------

.. _q-cinder-driver-deadline:

Cinder New Driver Submission Deadline
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The deadline for submitting new backend drivers to Cinder is 4 Dec, 2017
(23:59 UTC). New drivers must be complete, with unit tests, passing 3rd party
CI and be merged by this date.

.. _q-cinder-spec-freeze:

Cinder Spec Freeze
^^^^^^^^^^^^^^^^^^

All Cinder specs must be approved by 4 Dec, 2017 (23:59 UTC).

.. _q-cinder-fp-freeze:

Cinder Feature Proposal Freeze
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All new Cinder features must be proposed and substantially complete, with unit
tests by 19 Jan, 2018 (23:59 UTC).


Sahara
------

.. _q-sahara-plugin-deadline:

Sahara Plugin Deadline
^^^^^^^^^^^^^^^^^^^^^^

The deadline for submitting new plugins or plugin versions to Sahara is
8 Dec 2017 (23:59 UTC). The motivation for this deadline is to ensure
sufficient time for testing plugins and ensuring their stability. Also, due to
the unpredictable release schedule of Hadoop components, we should avoid the
practice of delaying plugin upgrades too far into the cycle. Exemptions to this
deadline may be granted by the PTL.
