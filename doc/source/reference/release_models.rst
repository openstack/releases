================
 Release Models
================

Development in OpenStack is organized around 6-month cycles (like
"kilo").  At the end of every 6-month cycle, a synchronized release
of all OpenStack components is produced, along with a common stable
branch, providing a convenient reference point for downstream teams
(stable branch maintenance, vulnerability management) and downstream
users (in particular packagers of OpenStack distributions).

Most deliverables follow the cycle. If their "final" release is their
only release of the development cycle, they can produce release
candidates in the final stages of the release cycle (`cycle-with-rc`_
release model). Otherwise they can opt to release directly and
whenever appropriate (`cycle-with-intermediary`_ release model).

The deadline for producing this "final" release varies depending on
the type of the deliverable. In a development cycle, non-client
libraries ("library" type) are first, then client libraries
("client-library" type), then services and other main deliverables
("service" and "other" types), then release-trailing deliverables
("trailing" type).

Finally, some deliverables that are generally useful and not strictly
tied to the OpenStack development cycle can release independently
from it using the `independent`_ release model.

A number of rules apply based on what the deliverable is and which
bucket of the OpenStack map it falls in:

* Components appearing in the *openstack* bucket in the `OpenStack map`_
  form the main components of an OpenStack cloud, and therefore must follow
  the release cycle. They need to pick between `cycle-with-rc`_
  or `cycle-with-intermediary`_ models.
* Libraries cannot use RCs. They need to pick between
  `cycle-with-intermediary`_ and `independent`_ release models. Libraries
  with strong ties to OpenStack should prefer the `cycle-with-intermediary`_
  model, while generally-useful libraries should prefer the `independent`_
  model.
* Trailing deliverables trail the release, so they cannot, by definition,
  be independent. They need to pick between `cycle-with-rc`_ or
  `cycle-with-intermediary`_ models.

.. _`OpenStack map`: https://www.openstack.org/openstack-map

.. _cycle-with-rc:

cycle-with-rc
=============

The "cycle-with-rc" model describes projects that produce a single release at
the end of the cycle, with one or more release candidates (RC) close to the end
of the cycle and optional development milestone betas published on a
per-project need.

* "cycle-with-rc" projects commit to publish at least one release candidate
  following a predetermined schedule published by the Release Management team
  before the start of the cycle.
* "cycle-with-rc" projects commit to produce a release to match the end of the
  development cycle.
* Release tags for deliverables using this tag are reviewed and applied by the
  Release Management team.

.. _cycle-with-intermediary:

cycle-with-intermediary
=======================

The "cycle-with-intermediary" model describes projects that produce
multiple full releases during the development cycle, with a final
release to match the end of the cycle.

* "cycle-with-intermediary" projects commit to produce a
  release near the end of the 6-month development cycle to be used
  with projects using the other cycle-based release models that are
  required to produce a release at that time.
* Release tags for deliverables using this tag are reviewed and
  applied by the Release Management team.

.. _independent:

independent
===========

Some projects opt to completely bypass the 6-month cycle and release
independently. For example, that is the case of projects that support
the development infrastructure. The "independent" model describes such
projects.

* "independent" projects produce releases from time to time.
* Release tags for deliverables using this tag are managed without
  oversight from the Release Management team.

.. _abandoned:

abandoned
=========

As time passes, some deliverables are abandoned, as they are
no longer useful, or their functionality is absorbed by another deliverable.
For cycle-tied release models they just disappear in the next cycle. However
deliverables with a cycle-independent model just stay around.

The 'abandoned' release model describes a formally-independent deliverable
that will no longer be released, because it changed release models or
because it was abandoned.

* "abandoned" deliverables never produce new releases.

.. _untagged:

untagged
========

Some CI tools are used only from source and never tag releases, but
need to create stable branches.

Transition between release models
=================================

OpenStack-related libraries
---------------------------

Libraries with strong ties with OpenStack are released with a
`cycle-with-intermediary`_ model, so that:

* they can be released early and often
* services consuming those libraries can take advantage of their new
  features
* we detect integration bugs early rather than late

This works well while libraries see lots of changes, however it is a bit
heavy-handed for feature-complete, stable libraries: it forces those to
release multiple times per year even if they have not seen any change.

Once libraries are deemed feature-complete and stable, they should be
switched to an `independent`_ release model (like all our third-party
libraries). Those would see releases purely as needed for the occasional
corner case bugfix. They won't be released early and often, there is no
new feature to take advantage of, and new integration bugs should be
very rare.

This transition should be definitive in most cases. In rare cases where
a library were to need large feature development work again, we'd have
two options: develop the new feature in a new library depending on the
stable one, or grant an exception and switch it back to the
`cycle-with-intermediary`_ model.

Legacy release models
=====================

Those models were available in previous development cycles, but were
replaced or abandoned.

.. _cycle-trailing:

cycle-trailing
--------------

.. note::

   The cycle-trailing release model has been replaced by a specific
   "trailing" deliverable type that can be applied to cycle-with-rc
   or cycle-with-intermediary release models.

The "cycle-trailing" model was used by projects producing OpenStack
packaging, installation recipes or lifecycle management tools. Those
still do one release for every development cycle, but they can't
release until OpenStack itself is released.

* "cycle-trailing" projects commit to produce a release no later than
  3 months after the main release.
* Release tags for deliverables using this tag are reviewed and
  applied by the Release Management team.

.. _cycle-automatic:

cycle-automatic
---------------

.. note::

   The cycle-automatic release model is now better described by the
   cycle-with-intermediary model combined with stable-branch-type: none

The "cycle-automatic" model is used by specific technical deliverables
that need to be automatically released once at the end of a cycle.
Those may, optionally, also be released in the middle of the cycle.
Those do not need a stable branch created. This may be applied only
to "tempest-plugin" or "other" deliverables.

* "cycle-automatic" deliverables will be automatically released by the
  release team once at the end of a cycle, using the current HEAD of the
  repository. No stable branch will be automatically created.
* Release tags for deliverables using this model are reviewed and
  applied by the Release Management team.


.. _cycle-with-milestones:

cycle-with-milestones
---------------------

.. note::

   The cycle-with-milestones release model has been replaced by the
   cycle-with-rc model.

The "cycle-with-milestones" model described projects that produced a
single release at the end of the cycle, with development milestones
published at predetermined times in the cycle schedule.

* "cycle-with-milestones" projects committed to publish development
  milestones following a predetermined schedule published by the Release
  Management team before the start of the 6-month cycle.
* "cycle-with-milestones" projects committed to produce a release to
  match the end of the 6-month development cycle.
* Release tags for deliverables using this tag were reviewed and
  applied by the Release Management team.
* Projects using milestones were expected to tag at least 2 out of the
  3 for each cycle, or risk being dropped as an official project. The
  release team would remind projects that miss the first milestone, and
  create tags on any later milestones for the project team by tagging
  HEAD at the time of the deadline. If the release team force-created
  2 tags for a project in the same given development cycle, the
  project would be treated as inactive and the release team would
  recommend dropping it from the official project list.
