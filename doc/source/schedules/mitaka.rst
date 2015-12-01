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
| Nov 30-4   | R-18 | :ref:`m-1`                |                             |
+------------+------+---------------------------+-----------------------------+
| Dec 7-11   | R-17 |                           |                             |
+------------+------+---------------------------+-----------------------------+
| Dec 14-18  | R-16 |                           |                             |
+------------+------+---------------------------+-----------------------------+
| Dec 21-25  | R-15 |                           |                             |
+------------+------+---------------------------+-----------------------------+
| Dec 28-1   | R-14 |                           |                             |
+------------+------+---------------------------+-----------------------------+
| Jan 4-8    | R-13 |                           |                             |
+------------+------+---------------------------+-----------------------------+
| Jan 11-15  | R-12 |                           |                             |
+------------+------+---------------------------+-----------------------------+
| Jan 16-22  | R-11 | :ref:`m-2`                |                             |
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
| Feb 29-4   | R-5  | :ref:`m-3`                |                             |
|            |      +---------------------------+-----------------------------+
|            |      | :ref:`m-ff`               |                             |
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

.. _m-final-clientlib:

Final release for client libraries
----------------------------------

Client libraries should issue their final release during this week, to match
feature freeze.

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
