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

3. Use ``init-series`` to create stub deliverable files based on the
   contents of the previous release.

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

5. The week before Milestone-1, include a reminder about completing
   the responses to community-wide goals in the countdown email.

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
      generated (for all release:cycle-with-milestones deliverables)
      with::

        tox -e aclmanager -- acls /path/to/openstack-infra/project-config

   2. Set the population of all $project-release-branch groups to the
      "Release Managers" group and $project-release. This can be done
      (for all release:cycle-with-milestones deliverables) by running
      ``aclmanager.py``::

        tox -e aclmanager -- groups pre_release $user

      ($user being your Gerrit username)

   3. Ask the release liaisons for the affected teams to update the
      contents of their $project-release groups. For new projects in
      some cases they will need to get the group created by Infra.

   4. Notify the Infrastructure team to `generate
      <https://docs.openstack.org/infra/system-config/signing.html#generation`_
      an artifact signing key (but not replace the current one yet), and
      begin the attestation process.

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

4. Ensure that final releases for libraries also include the
   specification to create the stable/$series branch.

5. Use the ``make-dashboard`` command to prepare the data for tracking
   the final release and import it into a Google Docs spreadsheet for
   collaborative editing and monitoring.

Milestone-3
===========

1. Verify that all projects following release:cycle-with-intermediary
   have prepared at least one release for the cycle.

2. Freeze changes to ``openstack/requirements`` by applying -2 to all
   open patches. Ensure that reviewers do not approve changes created
   by the proposal bot.

3. Ensure the stable/$series branch is requested with each client
   library final release.

4. Remind PTLs/liaisons that master should be frozen except for bug
   fixes and feature work with FFEs.

5. Remind PTL/liaisons to start preparing "prelude" release notes as
   summaries of the content of the release so that those are merged
   before their first release candidate.

6. Freeze all library releases except for release-critical bugs.

7. Include a reminder about completing the responses to community-wide
   goals in the countdown email.

Between Milestone-3 and RC1
===========================

1. Encourage liaisons to wait as long as possible to create RC1 to
   avoid immediately having to create an RC2 with a new bug fix.

2. Encourage release:independent projects to add the history for any
   releases not yet listed in their deliverable file.

3. Remind projects using all release models to prepare their new
   stable branch request around the RC1 target date.

   As soon as grenade is updated for the new branch (see the RC1
   instructions that follow), projects without stable branches may
   start seeing issues with their grenade jobs because without the
   stable branch the branch selection will cause the jobs to run
   master->master instead of previous->master. At the end of Ocata
   this caused trouble for the Ironic team, for example.

RC1
===

1. Ensure all RC1 tag requests include the info to have the
   stable/$series branch created, too.

   Branches for cycle-trailing and cycle-with-intermediary projects
   should be created when the PTL/liaison are ready, and not
   necessarily for RC1 week.

2. After the minimum set of projects used by devstack have been branched, the
   devstack branch can be created. Devstack doesn't push a tag at RC1 it is
   just branched off of HEAD

3. After devstack is branched a grenade branch can be created. As with devstack
   it will branch from HEAD instead of a tag.

4. Update the grenade settings in devstack-gate for the new branch. For
   example, https://review.openstack.org/362438.

5. For translations, create stable-$series versions in the Zanata
   translation server on https://translate.openstack.org for all
   projects that the translation team wants to handle. Create new
   translation-jobs-$series periodic jobs to import translations from
   the Zanata translation server and propose them to projects, add
   these jobs to all projects that have a stable-$series version.

   Note this work is done by translation team.

6. After all cycle-with-milestone projects have their branches
   created, use ``make_branch.sh`` to create the stable/$series
   branch for ``openstack/requirements``. Then announce that the
   requirements freeze is lifted from master.

     Note that we wait until after the other projects have branched to
     create the branch for requirements because tests for the stable
     branches of those projects will fall back to using the master
     branch of requirements until the same stable branch is created,
     but if the branch for the requirements repo exists early the
     changes happening in master on the other projects will not use it
     and we can have divergence between the requirements being tested
     and being declared as correct.

7. Create new branch specific jobs for our two branchless projects,
   devstack-gate and tempest, and configure Zuul to run them on all
   changes to those projects to protect against regressions with the
   stable branches and these tools. For example, see
   https://review.openstack.org/375110.

8. Add the new release series to the stable-compat jobs used by the Oslo
   libraries. For example, see https://review.openstack.org/375111.

9. Create periodic bitrot jobs for the new branch in Jenkins Job
   Builder and add them to Zuul's periodic pipeline. For example, see
   https://review.openstack.org/#/c/375092.

10. Add periodic bitrot jobs to tempest. For example, see
   https://review.openstack.org/#/c/375271.

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

1. Ensure that all projects that are publishing release notes have the
   notes link included in their deliverable file. See
   ``tools/add_release_note_links.sh``.

2. Encourage liaisons to merge all translation patches.

3. When all translations and bug fixes are merged for a project,
   prepare a new release candidate.

4. Ensure that the final release candidate for each project is
   prepared at least one week before the final release date.

5. After final releases for release:cycle-with-intermediary projects
   are tagged, create their stable branches.

6. On the morning of the deadline for final release candidates, check
   the list of unreleased changes for milestone projects and verify
   with the PTLs and liaisons that they are planning a release or that
   they do not need one.

   In the release-tools repository working directory, run::

     $ ./list_unreleased_changes.sh stable/newton $(list-repos --tag release:cycle-with-milestones) 2>&1 | tee unreleased.log

7. As soon as the last release candidate is tagged and the freeze
   period is entered, use ``propose-final-releases`` to tag the
   existing most recent release candidates as the final release for
   projects using the cycle-with-milestone model.

8. Ask liaisons and PTLs of milestone-based projects to review and +1
   the final release proposal from the previous step so their approval
   is included in the metadata that goes onto the signed tag.

9. The week before final release test the release process using the
   openstack/release-test repository.

Final Release
=============

1. Approve the final release patch created earlier.

2. Reset gerrit ACLs

   1. Update all of the $project-release-branch groups to have
      $project-stable-maint as members instead of "Release Managers"
      and $project-release. This can be done (for all
      release:cycle-with-milestones deliverables) by running::

        tox -e aclmanager -- groups post_release $user

      ($user being your Gerrit username)

   2. Remove the refs/heads/stable/$series from the project gerrit
      ACLs. This can be done by reverting the original ACL patch.

3. Add documentation links on the series page on releases.o.o.
   See https://review.openstack.org/#/c/381005 for an example.

4. Notify the documentation team that the final release has been
   tagged so they can update the documentation landing page. (They
   might wait to do that until the press release is published.)

5. Mark series as released on releases.o.o, by updating doc/source/index.rst
   and doc/source/$series/index.rst.
   See https://review.openstack.org/#/c/381006 for an example.

6. Update the default series name in
   ``openstack/releases/openstack_releases/defaults.py`` to use the
   new series name.

7. Send release announcement email to
   ``openstack-announce@lists.openstack.org``, based on
   ``templates/final.txt``. Coordinate the timing of the email with
   the press release from the Foundation staff.

8. Declare ``openstack/releases`` unfrozen.

Post-Final Release
==================

1. The week after the final release, process any late or blocked
   release requests for deliverables for any branch (treating the new
   series branch as stable).

2. The week after the final releases for milestone-based projects are
   tagged, use ``propose-final-releases --all`` to tag the existing
   most recent release candidates as the final release for projects
   using the cycle-trailing model.

3. Ask liaisons and PTLs of cycle-trailing projects to review and +1
   the final release proposal from the previous step so their approval
   is included in the metadata that goes onto the signed tag.

cycle-trailing Final Release
============================

1. Two weeks after the final release for milestone-based projects,
   approve the final release patch created earlier.

2. Reset gerrit ACLs

   1. Update all of the $project-release-branch for cycle-trailing
      groups to have $project-stable-maint as members instead of
      "Release Managers" and $project-release. This can be done (for
      all release:cycle-with-milestones deliverables) by running
      ``aclmanager.py groups post_release $user`` ($user being your
      Gerrit username)

   2. Remove the refs/heads/stable/$series from the project gerrit
      ACLs. This can be done by reverting the original ACL patch.

R+4 Branch Documentation Repos
==============================

1. The documentation team waits to branch their repositories until a
   few weeks after the final release. Be available to help with
   creating the branches if needed.
