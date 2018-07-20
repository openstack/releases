===================
 Release Processes
===================

This document describes the relative ordering and rough timeline for
all of the steps related to preparing the release.

Before PTG (after closing previous release)
===========================================

1. Set up the release schedule for the newly opened cycle by creating
   the required pages in openstack/releases.

2. Update the link to the documentation on the newly opened cycle page
   to point to the right place on docs.openstack.org.

3. Create the $series-relmgt-plan and $series-relmgt-tracking
   etherpads.

4. Use ``init-series`` to create stub deliverable files based on the
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

4. Start weekly countdown emails, sent on Thursday afternoon (US)
   or Friday morning (EU/APAC) with information needed about the
   following week (deadlines, instructions, etc.).

5. The week before Milestone-1, include a reminder about completing
   the responses to community-wide goals in the countdown email.

Milestone-1
===========

1. Include the deadline for the milestone in the countdown emails but
   do not send extra reminders to liaisons. Missing the first
   milestone isn't important in terms of the release, so we want to
   encourage everyone to pay attention on their own.

2. Run tools/aclissues.py to detect potential leftovers in Gerrit ACLs
   allowing official deliverables to directly tag or branch without
   going through openstack/releases. You need to specify the location
   of up-to-date checkouts for the governance and the project-config
   repositories. For example::

     tools/aclissues.py ../project-config ../governance

Between Milestone-1 and Milestone-2
===================================

1. Follow up with PTLs and liaisons for projects that missed the first
   milestone.

2. Use the countdown emails to list which projects have not done any
   stable release yet, to encourage them to do so.

3. Use the countdown emails to list which intermediary-released (or
   independent) projects haven't done a release yet. Remind teams that
   we need at least one library release before milestone-2.

4. The week before Milestone-2 include a reminder of the deadline in
   the countdown emails. Mention the MembershipFreeze deadline as well.
   List teams that still haven't done a library release yet and remind
   them of the milestone-2 deadline.

Milestone-2
===========

1. Run the following to get a report of which libraries have unreleased
   changes::

     tools/list_library_unreleased_changes.sh

   Filter out libraries that have insignificant changes (Updates to .gitreview,
   etc.) and include list in the weekly countdown email.

2. Run tools/aclissues.py to detect potential leftovers in Gerrit ACLs
   allowing official deliverables to directly tag or branch without
   going through openstack/releases. You need to specify the location
   of up-to-date checkouts for the governance and the project-config
   repositories. For example::

     tools/aclissues.py ../project-config ../governance

Between Milestone-2 and Milestone-3
===================================

1. Follow up with PTLs and liaisons for projects that missed the second
   milestone, or still haven't done their library releases yet.

2. In the countdown email immediately after Milestone-2, include a
   reminder about the various freezes that happen around Milestone-3.

3. Two weeks before Milestone-3, include a reminder about the final
   library release freeze coming the week before Milestone-3.

   1. Run the command from milestone-2 again to get a list of libraries::

        tools/list_library_unreleased_changes.sh

   2. Include list of unreleased libraries in the email to increase visibility.

4. Two weeks before Milestone-3, prepare other teams to the final release
   rush.

   1. Ask the release liaisons for the affected teams to update the
      contents of their $project-stable-maint groups, as that group
      will control the stable/$series branch prior to release. They
      should reach out to the stable-maint-core group for additions.

   2. Notify the Infrastructure team to `generate an artifact signing key`_
      (but not replace the current one yet), and
      begin the attestation process.

      .. _generate an artifact signing key: https://docs.openstack.org/infra/system-config/signing.html#generation

5. Two weeks before milestone 3, warn cycle-with-intermediary projects
   that had changes over the cycle but no release yet that the release
   team will tag HEAD of master for their project if they have not prepared
   a release by the following week so that there is a fallback release to
   use for the cycle and as a place to create their stable branch.

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

5. Tag HEAD of master for any cycle-with-intermediary project with
   changes merged over the cycle but no release yet. Do not create
   branches for non-library projects.

6. Tag HEAD of master for any cycle-with-intermediary project that has
   unreleased CI configuration changes that would not have triggered a
   release earlier in the cycle. Failing to tag means those CI changes
   will not be on the stable branch and so the stable branch may start
   out broken. Do not create branches for non-library projects.

7. For stable libraries that did not have any change merged over the
   cycle, create a stable branch from the last available release.


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

6. Freeze all cycle-based library releases except for release-critical
   bugs. Independently-released libraries may still be released, but
   constraint or requirement changes will be held until after the freeze
   period.

7. Include a reminder about completing the responses to community-wide
   goals in the countdown email.

8. Run tools/aclissues.py to detect potential leftovers in Gerrit ACLs
   allowing official deliverables to directly tag or branch without
   going through openstack/releases. You need to specify the location
   of up-to-date checkouts for the governance and the project-config
   repositories. For example::

     tools/aclissues.py ../project-config ../governance

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

4. Warn cycle-with-intermediary projects that have releases more than
   2 months old that we will use their existing release as a point for
   branching if they have not prepared a newer release by the RC1
   deadline.

5. Warn cycle-with-intermediary projects that did not have any change
   over the cycle that no release will be tagged for them. A stable
   branch will be created, though, from the last available release.

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

3. After devstack is branched a grenade branch can be created. As with
   devstack it will branch from HEAD instead of a tag.

4. Update the default branch for devstack in the new stable
   branch. For example, https://review.openstack.org/#/c/493208/

5. Update the grenade settings in devstack-gate for the new branch. For
   example, https://review.openstack.org/362438.

6. For translations, create stable-$series versions in the Zanata
   translation server on https://translate.openstack.org for all
   projects that the translation team wants to handle. Create new
   translation-jobs-$series periodic jobs to import translations from
   the Zanata translation server and propose them to projects, add
   these jobs to all projects that have a stable-$series version.

   Note this work is done by translation team.

7. After all cycle-with-milestone projects have their branches
   created, someone from the requirements core team (preferably the
   requirements PTL) needs to propose an update the deliverable file to
   create the stable/$series branch for ``openstack/requirements``.
   Then announce that the requirements freeze is lifted from master.

   .. note::

     We wait until after the other projects have branched to
     create the branch for requirements because tests for the stable
     branches of those projects will fall back to using the master
     branch of requirements until the same stable branch is created,
     but if the branch for the requirements repo exists early the
     changes happening in master on the other projects will not use it
     and we can have divergence between the requirements being tested
     and being declared as correct.

8. In the tempest repo, create new branch specific jobs for our two branchless
   projects, devstack-gate and tempest. Configure tempest to run them on all
   changes, voting. Configure tempest to run them as periodic bitrot jobs as
   well. All this can be done in one tempest patch, like for example, see
   https://review.openstack.org/521888.
   Configure devstack-gate to run the new jobs in check pipeline only,
   non-voting, for example see https://review.openstack.org/545144.

9. Add the new branch to the list of branches in the periodic-stable job
   templates in openstack-zuul-jobs. For example, see
   https://review.openstack.org/545268/.


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

7. After the deadline for final release candidates has passed, create
   stable branches for cycle-with-intermediary projects that did not
   have any change merged over the cycle. Those branches should be
   created from the last available release.

8. As soon as the last release candidate is tagged and the freeze
   period is entered, use ``propose-final-releases`` to tag the
   existing most recent release candidates as the final release for
   projects using the cycle-with-milestone model.

9. Ask liaisons and PTLs of milestone-based projects to review and +1
   the final release proposal from the previous step so their approval
   is included in the metadata that goes onto the signed tag.

10. The week before final release test the release process using the
    openstack/release-test repository.

11. Notify the documentation team that it should be safe to apply
    their process to create the new release series landing pages for
    docs.openstack.org. Their process works better if they wait until
    most of the projects have their stable branches created, but they
    can do the work before the final release date to avoid having to
    synchronize with the release team on that day.

Final Release
=============

1. Approve the final release patch created earlier.

2. Run the missing-releases script to check for missing tarballs on the
   release page before the announcement::

      tox -e venv -- missing-releases --series $SERIES

3. Mark series as released on releases.o.o, by updating doc/source/index.rst
   and doc/source/$series/index.rst.
   See https://review.openstack.org/#/c/381006 for an example.

4. Update the default series name in
   ``openstack/releases/openstack_releases/defaults.py`` to use the
   new series name.

5. Send release announcement email to
   ``openstack-announce@lists.openstack.org``, based on
   ``templates/final.txt``. Coordinate the timing of the email with
   the press release from the Foundation staff.

6. Send an email to the openstack-dev list to point to the official
   release announcement, and declare ``openstack/releases`` unfrozen for
   releases on the new series.

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

