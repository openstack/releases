=========================
 Mitaka release schedule
=========================

+-------------------+---------------------------+-----------------------------+
| Week              | Cross-project events      | Project-specific events     |
+============+======+===========================+=============================+
| Oct 19-23  | R-24 |                           |                             |
+------------+------+---------------------------+-----------------------------+
| Oct 26-30  | R-23 | :ref:`m-design-summit`    |                             |
+------------+------+---------------------------+-----------------------------+
| Nov 2-6    | R-22 |                           |                             |
+------------+------+---------------------------+-----------------------------+
| Nov 9-13   | R-21 |                           |                             |
+------------+------+---------------------------+-----------------------------+
| Nov 16-20  | R-20 |                           |                             |
+------------+------+---------------------------+-----------------------------+
| Nov 23-27  | R-19 |                           |                             |
+------------+------+---------------------------+-----------------------------+
| Nov 30-4   | R-18 | :ref:`m-1`                | :ref:`m-nova-bp-freeze`     |
|            |      +---------------------------+-----------------------------+
|            |      |                           | :ref:`m-key-bp-freeze`      |
+------------+------+---------------------------+-----------------------------+
| Dec 7-11   | R-17 |                           |                             |
+------------+------+---------------------------+-----------------------------+
| Dec 14-18  | R-16 |                           |                             |
+------------+------+---------------------------+-----------------------------+
| Dec 21-25  | R-15 |                           |                             |
+------------+------+---------------------------+-----------------------------+
| Dec 28-1   | R-14 |                           | :ref:`m-glance-bp-freeze`   |
+------------+------+---------------------------+-----------------------------+
| Jan 4-8    | R-13 |                           |                             |
+------------+------+---------------------------+-----------------------------+
| Jan 11-15  | R-12 |                           |                             |
+------------+------+---------------------------+-----------------------------+
| Jan 18-22  | R-11 | :ref:`m-2`                | :ref:`m-nova-npff`          |
|            |      +---------------------------+-----------------------------+
|            |      |                           | :ref:`m-cinder-nddeadline`  |
|            |      +---------------------------+-----------------------------+
|            |      |                           | :ref:`m-key-fpdeadline`     |
|            |      +---------------------------+-----------------------------+
|            |      |                           | :ref:`m-cinder-spec-freeze` |
|            |      +---------------------------+-----------------------------+
|            |      |                           | :ref:`m-glance_store-maint` |
+------------+------+---------------------------+-----------------------------+
| Jan 25-29  | R-10 |                           |                             |
+------------+------+---------------------------+-----------------------------+
| Feb 1-5    | R-9  |                           |                             |
+------------+------+---------------------------+-----------------------------+
| Feb 8-12   | R-8  |                           |                             |
+------------+------+---------------------------+-----------------------------+
| Feb 15-19  | R-7  |                           |                             |
+------------+------+---------------------------+-----------------------------+
| Feb 22-26  | R-6  | :ref:`m-final-lib`        |                             |
+------------+------+---------------------------+-----------------------------+
| Feb 29-4   | R-5  | :ref:`m-3`                | :ref:`m-cinder-ff`          |
|            |      +---------------------------+-----------------------------+
|            |      | :ref:`m-ff`               |                             |
|            |      +---------------------------+-----------------------------+
|            |      | :ref:`m-rf`               |                             |
|            |      +---------------------------+-----------------------------+
|            |      | :ref:`m-final-clientlib`  |                             |
|            |      +---------------------------+-----------------------------+
|            |      | :ref:`m-soft-sf`          |                             |
+------------+------+---------------------------+-----------------------------+
| Mar 7-11   | R-4  |                           |                             |
+------------+------+---------------------------+-----------------------------+
| Mar 14-18  | R-3  | :ref:`m-rc1`              | :ref:`n-ptl-nomination`     |
|            |      +---------------------------+-----------------------------+
|            |      | :ref:`m-hard-sf`          |                             |
+------------+------+---------------------------+-----------------------------+
| Mar 21-25  | R-2  |                           | :ref:`n-ptl-election`       |
+------------+------+---------------------------+-----------------------------+
| Mar 28-1   | R-1  | :ref:`m-finalrc`          | :ref:`n-tc-nomination`      |
+------------+------+---------------------------+-----------------------------+
| Apr 4-8    | R-0  | :ref:`m-release`          | :ref:`n-tc-election`        |
+------------+------+---------------------------+-----------------------------+


Cross-project events
====================

.. _m-design-summit:

Mitaka Design Summit
--------------------

Planning in Tokyo ! And Okonomiyaki.


.. _m-1:

mitaka-1 milestone
------------------

Dec 1-3 is the mitaka-1 milestone window for projects following the
release:cycle-with-milestones model.

.. _m-2:

mitaka-2 milestone
------------------

Jan 19-21 is the mitaka-2 milestone window for projects following the
release:cycle-with-milestones model.

.. _m-final-lib:

Final release for non-client libraries
--------------------------------------

Libraries that are not client libraries (Oslo and others) should issue their
final release during this week. That allows to give time for last-minute
changes before feature freeze.

Library releases resume around R-2.

.. _m-3:

mitaka-3 milestone
------------------

March 1-3 is the mitaka-3 milestone window for projects following the
release:cycle-with-milestones model.

.. _m-ff:

Feature freeze
--------------

The mitaka-3 milestone marks feature freeze for projects following the
release:cycle-with-milestones model. No featureful patch should be landed
after this point. Exceptions may be granted by the project PTL.

.. _m-rf:

Requirements freeze
-------------------

After the mitaka-3 milestone, only critical requirements and
constraints changes will be allowed. Freezing our requirements list
gives packagers downstream an opportunity to catch up and prepare
packages for everything necessary for distributions of the upcoming
release. The requirements remain frozen until the stable branches are
created, with the release candidates.

.. _m-final-clientlib:

Final release for client libraries
----------------------------------

Client libraries should issue their final release during this week, to match
feature freeze.

Library releases resume around R-2.

.. _m-soft-sf:

Soft StringFreeze
-----------------

You are no longer allowed to accept proposed changes containing modifications
in user-facing strings. Such changes should be rejected by the review team
and postponed until the next series development opens (which should happen
when RC1 is published).

.. _m-rc1:

RC1 target week
---------------

The week of March 14-18 is the target date for projects following the
release:cycle-with-milestones model to issue their first release candidate.

.. _m-hard-sf:

Hard StringFreeze
-----------------

This happens when the RC1 for the project is tagged. At this point, ideally
no strings are changed (or added, or removed), to give translator time to
finish up their efforts.

.. _m-finalrc:

Final RCs and intermediary releases
-----------------------------------

The week of March 28 to April 1st is the last week to issue release candidates
or intermediary releases before release week. On release week only
final-release-critical releases will be accepted (at the discretion of the
release team).

.. _m-release:

Mitaka release
--------------

The Mitaka coordinated release will happen on April 7th.


Project-specific events
=======================

Elections
---------

.. _n-ptl-nomination:

N cycle PTLs self-nomination
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Project team lead candidates for the N cycle should announce their candidacy
during this week.

.. _n-ptl-election:

N cycle PTLs election
^^^^^^^^^^^^^^^^^^^^^

Election week for Project team leads (where an election must be held to
determine the winner).

.. _n-tc-nomination:

TC member self-nomination
^^^^^^^^^^^^^^^^^^^^^^^^^

Candidates for the partial Technical Committee member renewal should announce
their candidacy during this week.

.. _n-tc-election:

TC member election
^^^^^^^^^^^^^^^^^^

Election for partially renewing Technical Committee members will happen
during this week.

Nova
----

.. _m-nova-bp-freeze:

Nova Blueprint Freeze
^^^^^^^^^^^^^^^^^^^^^

The deadline for getting a Nova blueprint approved for Mitaka is
3rd December 2015. Please note this is also the deadline to get any
Mitaka nova-specs merged.

.. _m-nova-npff:

Nova Non-Priority Feature Freeze
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A non-priority feature is any feature that is not associated with one of the
Mitaka priorities:
http://specs.openstack.org/openstack/nova-specs/priorities/mitaka-priorities.html

The deadline for non-priority feature code to be merged into master is
21st January 2015.

Please note, the Feature Freeze for priority features is aligned with :ref:`m-ff`.

Cinder
------

.. _m-cinder-nddeadline:

Cinder New Backend Driver Deadline
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The deadline for getting a new backend driver added to Cinder is 19th January
2015. All review issues must be addressed and third party CI must be reporting
and stable with enough time for reviewers prior to the deadline. Meeting these
requirements on the 19th does not guarantee core reviewers will have enough
time to merge the driver.

.. _m-cinder-spec-freeze:

Cinder Spec/Blueprint Freeze
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All Cinder specs and blueprints must be approved by 19th January 2015.

.. _m-cinder-ff:

Cinder Feature Freeze
^^^^^^^^^^^^^^^^^^^^^

The deadline for new features and driver functionality is 1st March 2016. Any
changes past that date will be at the discretion of the core team.

Glance
------

.. _m-glance-bp-freeze:

Glance Blueprints Freeze
^^^^^^^^^^^^^^^^^^^^^^^^

All Glance new feature requests must be approved by Jan 1st.

.. _m-glance_store-maint:

Glance Store maintainers deadline
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Glance store drivers without maintainers will be marked as deprecated
and then removed in N. Please, refer to this email thread for some
more information:

http://lists.openstack.org/pipermail/openstack-dev/2015-December/081966.html

Keystone
--------

.. _m-key-bp-freeze:

Keystone Spec/Blueprint Freeze
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The deadline for getting a Keystone blueprint approved for Mitaka is 3rd
December 2015. Please note this is also the deadline to get any
Mitaka keystone-specs merged. Specs that wish to land past this deadline must
send an email to the dev mailing list asking for an exemption.

.. _m-key-fpdeadline:

Keystone Feature Proposal Deadline
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All approved features must have a patch that shows most functionality ready for
review by 18th January 2016. Approved features that do not have a patch ready
for review by the deadline must send an email to the dev mailing list asking
for an exemption. Approved features that miss the deadline or do not receive an
exemption will be moved to the backlog or the first milestone of the next
release.

Please note, the Keystone Feature Freeze date is aligned with :ref:`m-ff`.
