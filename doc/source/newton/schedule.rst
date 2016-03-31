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
| May 30-03  | R-18 | :ref:`n-1`                |                             |
+------------+------+---------------------------+-----------------------------+
| Jun 06-10  | R-17 |                           |                             |
+------------+------+---------------------------+-----------------------------+
| Jun 13-17  | R-16 |                           |                             |
+------------+------+---------------------------+-----------------------------+
| Jun 20-24  | R-15 |                           |                             |
+------------+------+---------------------------+-----------------------------+
| Jun 27-01  | R-14 |                           |                             |
+------------+------+---------------------------+-----------------------------+
| Jul 04-06  | R-13 |                           |                             |
+------------+------+---------------------------+-----------------------------+
| Jul 11-15  | R-12 | :ref:`n-2`                |                             |
+------------+------+---------------------------+-----------------------------+
| Jul 18-22  | R-11 |                           |                             |
+------------+------+---------------------------+-----------------------------+
| Jul 25-29  | R-10 |                           |                             |
+------------+------+---------------------------+-----------------------------+
| Aug 01-05  | R-9  |                           |                             |
+------------+------+---------------------------+-----------------------------+
| Aug 08-12  | R-8  |                           |                             |
+------------+------+---------------------------+-----------------------------+
| Aug 15-19  | R-7  |                           |                             |
+------------+------+---------------------------+-----------------------------+
| Aug 22-26  | R-6  | :ref:`n-final-lib`        |                             |
+------------+------+---------------------------+-----------------------------+
| Aug 29-02  | R-5  | :ref:`n-3`                |                             |
|            |      +---------------------------+-----------------------------+
|            |      | :ref:`n-ff`               |                             |
|            |      +---------------------------+-----------------------------+
|            |      | :ref:`n-final-clientlib`  |                             |
|            |      +---------------------------+-----------------------------+
|            |      | :ref:`n-soft-sf`          |                             |
+------------+------+---------------------------+-----------------------------+
| Sep 05-09  | R-4  |                           | :ref:`o-ptl-nomination`     |
+------------+------+---------------------------+-----------------------------+
| Sep 12-16  | R-3  | :ref:`n-rc1`              |                             |
|            |      +---------------------------+-----------------------------+
|            |      | :ref:`n-hard-sf`          |                             |
+------------+------+---------------------------+-----------------------------+
| Sep 19-23  | R-2  |                           | :ref:`o-ptl-election`       |
+------------+------+---------------------------+-----------------------------+
| Sep 26-30  | R-1  |                           | :ref:`o-tc-nomination`      |
+------------+------+---------------------------+-----------------------------+
| Oct 03-07  | R+0  | :ref:`n-release`          | :ref:`o-tc-election`        |
+------------+------+---------------------------+-----------------------------+
| Oct 10-14  | R+1  |                           |                             |
+------------+------+---------------------------+-----------------------------+
| Oct 17-21  | R+2  |                           |                             |
+------------+------+---------------------------+-----------------------------+
| Oct 24-28  | R+3  | :ref:`o-design-summit`    |                             |
+------------+------+---------------------------+-----------------------------+

Cross-project events
====================

.. _n-design-summit:

Newton Design Summit
--------------------

`Planning in Austin <https://www.openstack.org/summit/austin-2016/>`__


.. _n-1:

newton-1 milestone
------------------

XXX is the newton-1 milestone window for projects following the
`release:cycle-with-milestones`_ model.

.. _release:cycle-with-milestones: http://governance.openstack.org/reference/tags/release_cycle-with-milestones.html

.. _n-2:

newton-2 milestone
------------------

XXX is the newton-2 milestone window for projects following the
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

XXX is the newton-3 milestone window for projects following the
`release:cycle-with-milestones`_ model.

.. _n-ff:

Feature freeze
--------------

The newton-3 milestone marks feature freeze for projects following the
`release:cycle-with-milestones`_ model. No featureful patch should be landed
after this point. Exceptions may be granted by the project PTL.

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

.. _n-rc1:

RC1 target week
---------------

The week of XXX is the target date for projects following the
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

The week of XXX is the last week to issue release candidates
or intermediary releases before release week. On release week only
final-release-critical releases will be accepted (at the discretion of the
release team).

.. _n-release:

Newton release
--------------

The Newton coordinated release will happen on XXX.


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
