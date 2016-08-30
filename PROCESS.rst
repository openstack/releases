===================
 Release Processes
===================

This document describes the relative ordering and rough timeline for
all of the steps related to preparing the release.

Before Summit (after closing previous release)
=============================================

1. Set up the release schedule for the newly opened cycle by creating
   the required pages in openstack/releases.

2. Create the $series-relmgt-plan and $series-relmgt-tracking
   etherpads.

Between Summit and Milestone-1
==============================

1. Establish liaisons by having them update
   https://wiki.openstack.org/wiki/CrossProjectLiaisons with their
   contact information.

2. Email PTLs directly one time to explain the use of the "[release]"
   email tag on the openstack-dev list.

3. Encourage liaisons to ensure that their release model is set
   properly before the first milestone.

4. Start weekly countdown emails, sent on Thursday with information
   needed about the following week (deadlines, instructions, etc.).

Milestone-1
===========

1. Include the deadline for the milestone in the countdown emails but
   do not send extra reminders to liaisons. Missing the first
   milestone isn't important in terms of the release, so we want to
   encourage everyone to pay attention on their own.

Between Milestone-1 and Milestone-2
===================================

1. Follow up with PTLs and liaisons for projects that missed the first
   milestone.

2. The week before Milestone-2 include a reminder of the deadline in
   the countdown emails. Also remind release:independent and
   release:cycle-with-intermediary projects to prepare releases.

Milestone-2
===========

n/a

Between Milestone-2 and Milestone-3
===================================

1. In the countdown email immediately after Milestone-2, include a
   reminder about the various freezes that happen around Milestone-3.

2. Two weeks before Milestone-3, include a reminder about the final
   library release freeze coming the week before Milestone-3.

3. Two weeks before Milestone-3, set up the gerrit ACLs for the
   yet-to-be-created stable/$series branches.

   (The timing for this is meant to postpone it until all projects
   that will be included in the current release are accepted but not
   put it off for so long that we have to rush to merge the changes in
   order to avoid having the release blocked.)

   1. Update ACLs for refs/heads/stable/$series so that members of
      $project-release-branch can approve changes. The patch can be
      generated (for all release:cycle-with-milestones deliverables) with:
      ``aclmanager.py acls /path/to/openstack-infra/project-config $series``

   2. Set the population of all $project-release-branch groups to the
      "Release Managers" group and $project-release. This can be done
      (for all release:cycle-with-milestones deliverables) by running
      ``aclmanager.py groups pre_release $user`` ($user being your Gerrit
      username)

   3. Ask the release liaisons for the affected teams to update the
      contents of their $project-release groups. For new projects in
      some cases they will need to get the group created by Infra.

Final Library Release (week before Milestone-3)
===============================================

1. Release libraries as quickly as possible this week to ensure they
   are all done before the freeze. Consider relaxing the "not on
   Friday" release rule if absolutely necessary.

2. Remind liaisons to prepare releases for client libraries at
   Milestone-3.

3. Update the feature list and allowed stable branch names in
   devstack-gate for the new stable branch. For
   example, https://review.openstack.org/362435 and
   https://review.openstack.org/363084

4. Create stable/$series branches for the libraries after their final
   release is prepared using ``branch_from_yaml.sh``.

Milestone-3
===========

1. Verify that all projects following release:cycle-with-intermediary
   have prepared at least one release for the cycle.

2. Freeze changes to openstack/requirements by applying -2 to all open
   patches. Ensure that reviewers do not approve changes created by
   the proposal bot.

3. Create stable/$series branches for the client libraries after their
   final release is prepared using ``branch_from_yaml.sh``.

4. Remind PTLs/liaisons that master should be frozen except for bug
   fixes and feature work with FFEs.

5. Freeze all library releases except for release-critical bugs.

Between Milestone-3 and RC1
===========================

1. Encourage liaisons to wait as long as possible to create RC1 to
   avoid immediately having to create an RC2 with a new bug fix.

2. Use the ``dashboard`` command to prepare the data for tracking the
   final release and import it into a Google Docs spreadsheet for
   collaborative editing and monitoring.

3. Encourage release:independent projects to add the history for any
   releases not yet listed in their deliverable file.

RC1
===

1. Create stable/$series branches for projects after their RC1 is
   tagged using ``branch_from_yaml.sh``.

2. Update the grenade settings in devstack-gate for the new branch. For
   example, https://review.openstack.org/362438.

3. After all cycle-with-milestone projects have their branches
   created, use ``make_stable_branch.sh`` to create the stable/$series
   branch for openstack/requirements. Then announce that the
   requirements freeze is lifted from master.

     Note that we wait until after the other projects have branched to
     create the branch for requirements because tests for the stable
     branches of those projects will fall back to using the master
     branch of requirements until the same stable branch is created,
     but if the branch for the requirements repo exists early the
     changes happening in master on the other projects will not use it
     and we can have divergence between the requirements being tested
     and being declared as correct.

4. Create new branch specific jobs for our two branchless projects,
   devstack-gate and tempest, and configure Zuul to run them on all
   changes to those projects to protect against regressions with the
   stable branches and these tools.

5. Create periodic bitrot jobs for the new branch in Jenkins Job Builder
   and add them to Zuul's periodic pipeline.

Between RC1 and Final
=====================

Try to avoid creating more than 3 release candidates so we are not
creating candidates that consumers are then trained to ignore. Each
release candidate should be kept for at least 1 day, so if there is a
proposal to create RCX but clearly a reason to create another one,
delay RCX to include the additional patches. Teams that know they will
need additional release candidates can submit the requests and mark
them WIP until actually ready, so the release team knows that more
candidates are coming.

1. Encourage liaisons to merge all translation patches.

2. When all translations and bug fixes are merged for a project,
   prepare a new release candidate.

3. Ensure that the final release candidate for each project is
   prepared at least one week before the final release date.

Final Release
=============

1. Use ``propose-final-releases`` to tag the existing most recent
   release candidates as the final release for projects using the
   cycle-with-milestone model

2. Reset gerrit ACLs

   1. Update all of the $project-release-branch groups to have
      $project-stable-maint as members instead of "Release Managers"
      and $project-release. This can be done (for all
      release:cycle-with-milestones deliverables) by running
      ``aclmanager.py groups post_release $user`` ($user being your
      Gerrit username)

   2. Remove the refs/heads/stable/$series from the project gerrit
      ACLs. This can be done by reverting the original ACL patch.
