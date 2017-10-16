=========================
 Newton release schedule
=========================

+-------------------+---------------------------+-----------------------------+
| Week              | Cross-project events      | Project-specific events     |
+============+======+===========================+=============================+
| Apr 04-08  |      | :ref:`m-release`          |                             |
+------------+------+---------------------------+-----------------------------+
| Apr 11-15  | R-25 |                           |                             |
+------------+------+---------------------------+-----------------------------+
| Apr 18-22  | R-24 |                           |                             |
+------------+------+---------------------------+-----------------------------+
| Apr 25-29  | R-23 | :ref:`n-design-summit`    |                             |
+------------+------+---------------------------+-----------------------------+
| May 02-06  | R-22 |                           |                             |
+------------+------+---------------------------+-----------------------------+
| May 09-13  | R-21 |                           |                             |
+------------+------+---------------------------+-----------------------------+
| May 16-20  | R-20 |                           |                             |
+------------+------+---------------------------+-----------------------------+
| May 23-27  | R-19 |                           |                             |
+------------+------+---------------------------+-----------------------------+
| May 30-03  | R-18 | :ref:`n-1`                | :ref:`n-nova-non-prio-s-fr` |
|            |      +---------------------------+-----------------------------+
|            |      |                           | :ref:`n-key-spec-pfreeze`   |
+------------+------+---------------------------+-----------------------------+
| Jun 06-10  | R-17 |                           |                             |
+------------+------+---------------------------+-----------------------------+
| Jun 13-17  | R-16 |                           | :ref:`n-trove-spec-prop`    |
+------------+------+---------------------------+-----------------------------+
| Jun 20-24  | R-15 |                           |                             |
+------------+------+---------------------------+-----------------------------+
| Jun 27-01  | R-14 |                           | :ref:`n-nova-non-prio-ff`   |
+------------+------+---------------------------+-----------------------------+
| Jul 04-08  | R-13 |                           | :ref:`n-key-spec-freeze`    |
+------------+------+---------------------------+-----------------------------+
| Jul 11-15  | R-12 | :ref:`n-2`                | :ref:`n-cinder-nddeadline`  |
|            |      +---------------------------+-----------------------------+
|            |      | :ref:`n-mf`               | :ref:`n-cinder-spec-freeze` |
|            |      +---------------------------+-----------------------------+
|            |      |                           | :ref:`n-trove-spec-freeze`  |
|            |      +---------------------------+-----------------------------+
|            |      |                           | :ref:`n-key-fpf`            |
+------------+------+---------------------------+-----------------------------+
| Jul 18-22  | R-11 |                           |                             |
+------------+------+---------------------------+-----------------------------+
| Jul 25-29  | R-10 |                           |                             |
+------------+------+---------------------------+-----------------------------+
| Aug 01-05  | R-9  |                           | :ref:`n-nova-prio-spec-frz` |
+------------+------+---------------------------+-----------------------------+
| Aug 08-12  | R-8  | :ref:`n-extra-atcs`       |                             |
+------------+------+---------------------------+-----------------------------+
| Aug 15-19  | R-7  |                           |                             |
+------------+------+---------------------------+-----------------------------+
| Aug 22-26  | R-6  | :ref:`n-final-lib`        | :ref:`n-trove-cl-soft`      |
|            |      +---------------------------+-----------------------------+
|            |      |                           | :ref:`n-trove-guest-req`    |
|            |      +---------------------------+-----------------------------+
|            |      |                           | :ref:`n-horizon-ff`         |
+------------+------+---------------------------+-----------------------------+
| Aug 29-02  | R-5  | :ref:`n-3`                | :ref:`n-cinder-ff`          |
|            |      +---------------------------+-----------------------------+
|            |      | :ref:`n-ff`               | :ref:`n-trove-ff`           |
|            |      +---------------------------+-----------------------------+
|            |      | :ref:`n-final-clientlib`  | :ref:`n-key-ff`             |
|            |      +---------------------------+-----------------------------+
|            |      | :ref:`n-soft-sf`          |                             |
|            |      +---------------------------+-----------------------------+
|            |      | :ref:`n-rf`               |                             |
+------------+------+---------------------------+-----------------------------+
| Sep 05-09  | R-4  |                           |                             |
+------------+------+---------------------------+-----------------------------+
| Sep 12-16  | R-3  | :ref:`n-rc1`              | :ref:`o-ptl-nomination`     |
|            |      +---------------------------+-----------------------------+
|            |      | :ref:`n-hard-sf`          |                             |
+------------+------+---------------------------+-----------------------------+
| Sep 19-23  | R-2  |                           | :ref:`o-ptl-election`       |
+------------+------+---------------------------+-----------------------------+
| Sep 26-30  | R-1  | :ref:`n-finalrc`          | :ref:`o-tc-nomination`      |
+------------+------+---------------------------+-----------------------------+
| Oct 03-07  | R+0  | :ref:`n-release`          | :ref:`o-tc-election`        |
+------------+------+---------------------------+-----------------------------+
| Oct 10-14  | R+1  |                           |                             |
+------------+------+---------------------------+-----------------------------+
| Oct 17-21  | R+2  | :ref:`n-trailing`         |                             |
+------------+------+---------------------------+-----------------------------+
| Oct 24-28  | R+3  | :ref:`o-design-summit`    |                             |
+------------+------+---------------------------+-----------------------------+

.. note::

   All deadlines are generally the Thursday of the week on which they
   are noted above. For example, The Feature Freeze in week R-5 is on
   1 September. Exceptions to this policy will be explicitly mentioned
   in the event description.

Cross-project events
====================

.. _n-design-summit:

Newton Design Summit
--------------------

`Planning in Austin <https://www.openstack.org/summit/austin-2016/>`__


.. _n-1:

newton-1 milestone
------------------

May 31 - June 2 is the newton-1 milestone window for projects following the
`release:cycle-with-milestones`_ model.

.. _release:cycle-with-milestones: https://releases.openstack.org/reference/release_models.html#cycle-with-milestones

.. _n-2:

newton-2 milestone
------------------

July 12-14 is the newton-2 milestone window for projects following the
`release:cycle-with-milestones`_ model.

.. _n-final-lib:

Final release for non-client libraries
--------------------------------------

Libraries that are not client libraries (Oslo and others) should issue their
final release during this week. That allows to give time for last-minute
changes before feature freeze.

.. _n-3:

newton-3 milestone
------------------

August 30 - Sept 1 is the newton-3 milestone window for projects following the
`release:cycle-with-milestones`_ model.

.. _n-extra-atcs:

extra-atcs deadline
-------------------

Project teams should identify contributors who have had a significant
impact this cycle but who would not qualify for ATC status using the
regular process because they have not submitted a patch. Those names
should be added to the governance repo for consideration as ATC for
the future.

Although extra ATCs can be nominated at any point, there is a deadline
to be included in electorate for the next release cycle.  The ATC list
needs to be approved by the TC by 25 Aug, and in order to appear on
the TC agenda to be discussed, the proposals need to be submitted to
the ``openstack/governance`` repository by 16 Aug.

.. _n-ff:

Feature freeze
--------------

The newton-3 milestone marks feature freeze for projects following the
`release:cycle-with-milestones`_ model. No featureful patch should be landed
after this point. Exceptions may be granted by the project PTL.

.. _n-rf:

Requirements freeze
-------------------

After the newton-3 milestone, only critical requirements and
constraints changes will be allowed. Freezing our requirements list
gives packagers downstream an opportunity to catch up and prepare
packages for everything necessary for distributions of the upcoming
release. The requirements remain frozen until the stable branches are
created, with the release candidates.

.. _n-final-clientlib:

Final release for client libraries
----------------------------------

Client libraries should issue their final release during this week, to match
feature freeze.

.. _n-soft-sf:

Soft StringFreeze
-----------------

You are no longer allowed to accept proposed changes containing modifications
in user-facing strings. Such changes should be rejected by the review team
and postponed until the next series development opens (which should happen
when RC1 is published).

.. _n-mf:

Membership Freeze
-----------------

Projects must participate in at least two milestones in order to be
considered part of the release. Projects made official after the
second milestone, or which fail to produce milestone releases for at
least one of the first and second milestones as well as the third
milestone, are therefore not considered part of the release for the
cycle.

.. _n-rc1:

RC1 target week
---------------

The week of September 12 is the target date for projects following the
`release:cycle-with-milestones`_ model to issue their first release candidate.

.. _n-hard-sf:

Hard StringFreeze
-----------------

This happens when the RC1 for the project is tagged. At this point, ideally
no strings are changed (or added, or removed), to give translator time to
finish up their efforts.

.. _n-finalrc:

Final RCs and intermediary releases
-----------------------------------

The week of September 26 is the last week to issue release candidates
or intermediary releases before release week. On release week only
final-release-critical releases will be accepted (at the discretion of the
release team).

.. _n-release:

Newton release
--------------

The Newton coordinated release will happen on October 6th, 2016.

.. _n-trailing:

Newton cycle-trailing Deadline
------------------------------

The deadline for projects using the release:cycle-trailing model that
follow the main release cycle.

Project-specific events
=======================

Elections
---------

.. _o-ptl-nomination:

Ocata cycle PTLs self-nomination
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Project team lead candidates for the Ocata cycle should announce their
candidacy during this week.

.. _o-ptl-election:

Ocata cycle PTLs election
^^^^^^^^^^^^^^^^^^^^^^^^^

Election week for Project team leads (where an election must be held to
determine the winner).

.. _o-tc-nomination:

TC member self-nomination
^^^^^^^^^^^^^^^^^^^^^^^^^

Candidates for the partial Technical Committee member renewal should announce
their candidacy during this week.

.. _o-tc-election:

TC member election
^^^^^^^^^^^^^^^^^^

Election for partially renewing Technical Committee members will happen
during this week.

Cinder
------

.. _n-cinder-nddeadline:

Cinder New Backend Driver Deadline
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The deadline for getting a new backend driver added to Cinder is 12th July,
2016. All review issues must be addressed and third party CI must be reporting
and stable with enough time for reviewers prior to the deadline. Meeting these
requirements on the 12th does not guarantee core reviewers will have enough
time to merge the driver.

.. _n-cinder-spec-freeze:

Cinder Spec Freeze
^^^^^^^^^^^^^^^^^^

All Cinder specs must be approved by 12th July, 2016.

.. _n-cinder-ff:

Cinder Feature Freeze
^^^^^^^^^^^^^^^^^^^^^

The deadline for new features and driver functionality is 31 August, 2016. Any
changes past that date will be at the discretion of the core team.

Nova
----

For reference, these are the `Nova review priorities for Newton`_.

.. _Nova review priorities for Newton: https://specs.openstack.org/openstack/nova-specs/priorities/newton-priorities.html

.. _n-nova-non-prio-s-fr:

Nova non-priority spec approval freeze
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All non-priority Nova specs must be approved by June 2nd, 2016.

.. _n-nova-non-prio-ff:

Nova non-priority feature freeze
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The deadline for non-priority features is June 30th, 2016. There may be a round
of feature freeze exceptions but that will be at the discretion of the Nova
core team.

.. _n-nova-prio-spec-frz:

Nova priority spec approval freeze
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All priority Nova specs must be approved by August 4th, 2016. This is
intentionally after the Nova midcycle meetup for Newton so there is some time
for last minute adjustments to priority features.

Trove
-----

The deadlines below are specific to the Trove project.

.. _n-trove-spec-prop:

Trove Spec Proposal Deadline
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Submit all Trove specs for the Newton release by the end of this week
(for review) in trove-specs repository.

.. _n-trove-spec-freeze:

Trove Spec Freeze
^^^^^^^^^^^^^^^^^

All Trove specs for the Newton release must be approved by the end of
this week.

.. _n-trove-guest-req:

Trove Guest Requirements Freeze:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Freeze the requirements for all guest agents by this date and make the
newton requirements file for guests.

.. _n-trove-cl-soft:

Trove Client Soft Freeze
^^^^^^^^^^^^^^^^^^^^^^^^

All major features for the python-troveclient must be reviewed and
approved by the end of this week, this gives us one additional week to
address any issues with dependencies.

.. _n-trove-ff:

Trove Feature Freeze
^^^^^^^^^^^^^^^^^^^^

All major Trove features and projects for Newton must be approved by
the end of this week.

This is the deadline for the Trove server, the python-troveclient and
all trove-dashboard changes.

Horizon
-------

The deadlines below are specific to the Horizon project.

.. _n-horizon-ff:

Horizon Feature Freeze
^^^^^^^^^^^^^^^^^^^^^^

The deadline for Horizon features for Newton. This is a week earlier than
the standard milestone to allow plugins time to sync before the standard
release.

Keystone
--------

.. _n-key-spec-pfreeze:

Keystone Spec Proposal Freeze
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The deadline for proposing a Keystone specification that will land in the
Newton development cycle.

.. _n-key-spec-freeze:

Keystone Spec Freeze
^^^^^^^^^^^^^^^^^^^^

The deadline for merging a Keystone Spec and approving a blueprint.

.. _n-key-fpf:

Keystone Feature Proposal Freeze
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The deadline for proposing code for an approved feature. The code must: show
functionality and be ready for review. Approved features that miss the deadline
will be moved to the backlog or the first milestone of the next release.

.. _n-key-ff:

Keystone Feature Freeze
^^^^^^^^^^^^^^^^^^^^^^^

All approved features must be merged by this week. Please note, the Keystone
Feature Freeze date is aligned with :ref:`n-ff`.
