======================
Join the release team!
======================

Communication channels
======================

The release team communicates and meets on the `#openstack-release`_ channel
on OFTC IRC, on the `openstack-discuss mailing-list`_ using the [release]
subject prefix.

.. _`#openstack-release`: https://webchat.oftc.net/?channels=openstack-release

.. _`openstack-discuss mailing-list`: http://lists.openstack.org/cgi-bin/mailman/listinfo/openstack-discuss

The engagement ladder
=====================

Getting involved with release management can feel a bit overwhelming.
To set expectations reasonably, we define 4 levels of engagement.

Stage 0 - Review release requests
---------------------------------

This stage does not require any special rights. You should just review
release requests (modifications of files in deliverables/ directory in
the releases repository), apply the release review rules and vote.

See the :doc:`reviewer_guide` for more review guidelines.

Stage 1 - Approving release requests
------------------------------------

At this stage you will be trusted with CodeReview+2 and Workflow+1 votes
on the releases repository, giving you the ability to trigger releases.
You will need a base understanding of the :doc:`release_infra`, and know
to refrain from approving when unsure.

Checklist before approving a release:

* You should only approve release requests.
* You should check that release is approved by PTL or release liaison
* You should check that infrastructure is not currently experiencing issues
* You should check that we are not in any freeze period
* If unsure, it is better to wait for a second opinion that to press
  Workflow+1 directly.


Stage 2 - Knowing the release cycle process
-------------------------------------------

At this stage you will be able to help drive the release cycle process,
send reminder emails and answer questions from release liaisons.


Stage 3 - Understanding the Release Automation Infrastructure
-------------------------------------------------------------

At this stage you will be able to debug complex :doc:`release_infra`
failures, and review/approve release tooling changes.

