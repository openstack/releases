========================
 Pike Release Schedule
========================

.. note::

   All deadlines are generally the Thursday of the week on which they
   are noted above. For example, the Feature Freeze in week XXX is on
   XXX. Exceptions to this policy will be explicitly mentioned
   in the event description.

Cross-project events
====================

.. _p-goals-research:

Pike Goals Research
--------------------

Pre-cycle planning and investigation into `the community-wide goals
for Pike <http://governance.openstack.org/goals/pike/index.html>`__.

.. _p-design-summit:

Pike Design Summit
------------------

TBD

.. _p-ptg:

Pike Project Team Gathering (PTG)
---------------------------------

TBD

.. _p-1:

Pike-1 milestone
----------------

XXX is the Pike-1 milestone window for projects following the
`release:cycle-with-milestones`_ model.

.. _release:cycle-with-milestones: http://governance.openstack.org/reference/tags/release_cycle-with-milestones.html

.. _p-2:

Pike-2 milestone
----------------

XXX is the Pike-2 milestone window for projects following the
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

XXX is the Pike-3 milestone window for projects following the
`release:cycle-with-milestones`_ model.

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

The week of XXX - XXX is the target date for projects
following the `release:cycle-with-milestones`_ model to issue their
first release candidate, with a deadline of XXX.

.. _p-hard-sf:

Hard StringFreeze
-----------------

This happens when the RC1 for the project is tagged. At this point, ideally
no strings are changed (or added, or removed), to give translator time to
finish up their efforts.

.. _p-finalrc:

Final RCs and intermediary releases
-----------------------------------

The week of XXX is the last week to issue release candidates or
intermediary releases before release week. During release week, only
final-release-critical releases will be accepted (at the discretion of
the release team).

.. _p-release:

Pike release
------------

The Pike coordinated release will happen on XXX.

.. _p-trailing:

Pike cycle-trailing Deadline
----------------------------

The deadline for projects using the release:cycle-trailing model that
follow the main release cycle.

Project-specific events
=======================

Elections
---------

.. _q-ptl-nomination:

Queens PTLs self-nomination
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Project team lead candidates for the Pike cycle should announce their
candidacy during this week.

.. _q-ptl-election:

Queens cycle PTLs election
^^^^^^^^^^^^^^^^^^^^^^^^^^

Election week for Project team leads (where an election must be held to
determine the winner).

.. _q-tc-nomination:

TC member self-nomination
^^^^^^^^^^^^^^^^^^^^^^^^^

Candidates for the partial Technical Committee member renewal should announce
their candidacy during this week.

.. _q-tc-election:

TC member election
^^^^^^^^^^^^^^^^^^

Election for partially renewing Technical Committee members will happen
during this week.
