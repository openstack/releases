===================
 Release Processes
===================

This document describes the relative ordering and rough timeline for
all of the steps related to preparing the release.

Before PTG (after closing previous release)
===========================================

#. Set up the release schedule for the newly opened cycle by creating
   the required pages in openstack/releases.

#. Update the link to the documentation on the newly opened cycle page
   to point to the right place on docs.openstack.org.

#. Create the $series-relmgt-tracking etherpad using ``tools/list_weeks.py``.
   For example::

        tools/list_weeks.py t 2019-04-15 2019-10-16

#. Use ``init-series`` to create stub deliverable files based on the
   contents of the previous release.

Between Summit and Milestone-1
==============================

#. Establish liaisons by having them update
   https://wiki.openstack.org/wiki/CrossProjectLiaisons with their
   contact information.

#. Email PTLs directly one time to explain the use of the "[release][ptl]"
   email tag on the openstack-discuss list.

#. Encourage liaisons to ensure that their release model is set
   properly before the first milestone.

#. Start weekly countdown emails, sent right after the team meeting,
   with information needed about the
   following week (deadlines, instructions, etc.).

#. The week before Milestone-1, include a reminder about completing
   the responses to community-wide goals in the countdown email.

Milestone-1
===========

#. Generate a list of all cycle-with-intermediary libraries which did not
   release since the previous release. For this, run::

     tox -e venv -- list-deliverables --unreleased \
     --model cycle-with-intermediary --type client-library --type library

   Generate release requests for all cycle-with-intermediary libraries
   which had changes, but did not release since the previous release.
   That patch will be used as a base to communicate with the team:
   if a team wants to wait for a specific patch to make it to the library,
   someone from the team can -1 the patch to have it held, or update
   that patch with a different commit SHA.

#. To catch if there are acl issues in newly created repositories,
   run tools/aclissues.py to detect potential leftovers in Gerrit ACLs
   allowing official deliverables to be directly tagged or branched without
   going through openstack/releases. You need to specify the location
   of up-to-date checkouts for the governance and the project-config
   repositories. For example::

     tools/aclissues.py ../project-config ../governance

   If the tool reports any violation, you can re-run it with ``--patch`` to
   generate needed changes in ../project-config to align ACLs with governance,
   and propose the changes for review.

Between Milestone-1 and Milestone-2
===================================

#. Use the countdown emails to list which projects have not done any
   stable release yet, to encourage them to do so.

#. Use the countdown emails to list which intermediary-released deliverables
   haven't done a release yet. Remind teams that intermediary-released
   deliverables that have not done a release by milestone-2 should be
   switched to the cycle-with-rc model.

   For this, run::

     tox -e venv -- list-deliverables --unreleased \
     --model cycle-with-intermediary \
     --type horizon-plugin --type other --type service

#. Mention the upcoming MembershipFreeze deadline in the countdown emails.

#. Ahead of MembershipFreeze, run ``membership_freeze_test`` to check for
   any new deliverable in governance that has not been released yet::

     tox -e membership_freeze_test -- $series ~/branches/governance/reference/projects.yaml

   Those should either be tagged as a release management exception if they do
   not need to be released (see ``release-management`` key in the governance
   projects.yaml file) or an empty deliverable file should be added to the
   series so that we can properly track it. Leftovers are considered too young
   to be released in the next release and will be reconsidered at the next
   cycle.

Milestone-2
===========

#. Generate a list of all cycle-with-intermediary libraries which did not
   release since the YYYY-MM-DD date of milestone-1. For this, run::

     tox -e venv -- list-deliverables --unreleased-since YYYY-MM-DD
     --model cycle-with-intermediary --type client-library --type library

   Generate release requests for all cycle-with-intermediary libraries
   which had changes, but did not release since milestone-1.
   That patch will be used as a base to communicate with the team:
   if a team wants to wait for a specific patch to make it to the library,
   someone from the team can -1 the patch to have it held, or update
   that patch with a different commit SHA.

#. To catch if there are acl issues in newly created repositories,
   run ``tools/aclissues.py`` to detect potential leftovers in Gerrit ACLs
   allowing official deliverables to be directly tagged or branched without
   going through openstack/releases. You need to specify the location
   of up-to-date checkouts for the governance and the project-config
   repositories. For example::

     tools/aclissues.py ../project-config ../governance

   If the tool reports any violation, you can re-run it with ``--patch`` to
   generate needed changes in ../project-config to align ACLs with governance,
   and propose the changes for review.

Between Milestone-2 and Milestone-3
===================================

#. In the countdown email immediately after Milestone-2, include a
   reminder about the various freezes that happen around Milestone-3.

   Remind PTLs a heads up to start thinking about what they might want to
   include in their deliverables file as cycle-highlights
   and that feature freeze is the deadline for them.

#. Check with the election team about whether the countdown email
   needs to include any updates about the election schedule.

#. Generate a list of intermediary-released service deliverables that have
   not done a release in this cycle yet. For this, use::

     tox -e venv -- list-deliverables --unreleased \
     --model cycle-with-intermediary \
     --type horizon-plugin --type other --type service

   For intermediary-released deliverables that have not done a release yet,
   propose a change from cycle-with-intermediary to cycle-with-rc.
   Engage with PTLs and release liaisons to either get an intermediary
   release, or a confirmation of the model switch.

#. Two weeks before Milestone-3, include a reminder about the final
   library release freeze coming the week before Milestone-3.

   #. Run the command from milestone-2 again to get a list of libraries::

        tools/list_library_unreleased_changes.sh

   #. Include list of unreleased libraries in the email to increase visibility.

#. Two weeks before Milestone-3, prepare other teams to the final release
   rush.

   #. Ask the release liaisons for the affected teams to audit the
      contents of their ``$project-stable-maint`` groups, as that group
      will control the ``stable/$series`` branch prior to release. They
      should reach out to the ``stable-maint-core`` group for additions.

   #. Include a reminder about the stable branch ACLs in the countdown email.

   #. Notify the Infrastructure team to `generate an artifact signing key`_
      (but not replace the current one yet), and
      begin the attestation process.

      .. _generate an artifact signing key: https://docs.openstack.org/infra/system-config/signing.html#generation

   #. Include a reminder in the weekly countdown email reminding PTLs of the
      feature freeze deadline for cycle-highlights.

Final Library Release (week before Milestone-3)
===============================================

#. Generate a list of all cycle-with-intermediary libraries (except client
   libraries) which did not release since the YYYY-MM-DD date of milestone-2.
   For this, run::

     tox -e venv -- list-deliverables --unreleased-since YYYY-MM-DD
     --model cycle-with-intermediary --type library

   Generate release requests for all cycle-with-intermediary libraries
   (except client libraries) which had changes, but did not release since
   milestone-2. That patch will be used as a base to communicate with the
   team: if a team wants to wait for a specific patch to make it to the
   library, someone from the team can -1 the patch to have it held, or update
   that patch with a different commit SHA.

   .. note::

      At this point, we want *all* changes in the deliverables, to ensure
      that we have CI configuration up to date when the stable branch
      is created later.

#. Release libraries as quickly as possible this week to ensure they
   are all done before the freeze.

#. Update the feature list and allowed stable branch names in
   devstack-gate for the new stable branch. For
   example, https://review.opendev.org/362435 and
   https://review.opendev.org/363084

#. Allow the ``stable/$series`` branch to be requested with each library final
   release if they know they are ready. Do not require branching at this point
   in case of critical issues requiring another approved release past the
   freeze date.

Milestone-3
===========

#. Generate a list of all cycle-with-intermediary client libraries which
   did not release since the YYYY-MM-DD date of milestone-2.
   For this, run::

     tox -e venv -- list-deliverables --unreleased-since YYYY-MM-DD
     --model cycle-with-intermediary --type client-library

   Generate release requests for all client libraries which had changes,
   but did not release since milestone-2. That patch will be used as a base
   to communicate with the team: if a team wants to wait for a specific patch
   to make it to the library, someone from the team can -1 the patch to have
   it held, or update that patch with a different commit SHA.

#. Evaluate any libraries that did not have any change merged over the
   cycle to see if it is time to `transition them to the independent release
   model <https://releases.openstack.org/reference/release_models.html#openstack-related-libraries>`__.

   If it is OK to transition them, move the deliverable file to the ``_independent`` directory.

   If it is not OK to transition them, create a new stable branch from the latest release
   from the previous series.

#. Remind the requirements team to freeze changes to
   ``openstack/requirements`` by applying -2 to all
   open patches. Ensure that reviewers do not approve changes created
   by the proposal bot, but do approve changes for new OpenStack deliverable
   releases.

#. Allow the ``stable/$series`` branch to be requested with each client library
   final release if they know they are ready. Do not require branching at this
   point in case of critical issues requiring another approved release past the
   freeze date.

#. Remind PTLs/liaisons that master should be frozen except for bug
   fixes and feature work with FFEs.

#. Email openstack-discuss list to remind PTLs that cycle-highlights are due
   this week so that they can be included in release marketing preparations.

#. Remind PTL/liaisons to start preparing "prelude" release notes as
   summaries of the content of the release so that those are merged
   before their first release candidate.

#. Freeze all cycle-based library releases except for release-critical
   bugs. Independently-released libraries may still be released, but
   constraint or requirement changes will be held until after the freeze
   period.

   .. note::

      Do not release libraries without a link to a message to openstack-discuss
      requesting a requirements FFE and an approval response from that team.

Between Milestone-3 and RC1
===========================

#. List cycle-with-intermediary deliverables that have not been refreshed in
   the last 2 months. For this, use the following command, with YYYY-MM-DD
   being the day two nmonths ago::

     tox -e venv -- list-deliverables --unreleased-since YYYY-MM-DD
     --model cycle-with-intermediary \
     --type horizon-plugin --type other --type service

   Warn teams with deliverables that have releases more than 2 months old
   that we will use their existing release as a point for branching if they
   have not prepared a newer release by the final RC deadline.

#. Propose ``stable/$series`` branch creation for all client and non-client
   libraries that had not requested it at freeze time. The following command
   may be used::

      tox -e venv -- propose-library-branches --include-clients

RC1 week
========

#. Early in the week, generate RC1 release requests (including the
   ``stable/$series`` branch creation) for all cycle-with-rc deliverables.
   That patch will be used as a base to communicate with the team:
   if a team wants to wait for a specific patch to make it to the RC,
   someone from the team can -1 the patch to have it held, or update
   that patch with a different commit SHA.

#. Generate release requests (without ``stable/$series`` branch creation)
   for all cycle-automatic deliverables.

#. By the end of the week, ideally we would want a +1 from the PTL and/or
   release liaison to indicate approval. However we will consider the absence
   of -1 or otherwise negative feedback as an indicator that the automatically
   proposed patches can be approved at the end of the RC deadline week.

#. After all the projects enabled in devstack by default have been branched,
   remind the QA PTL to create a branch in the devstack repository. Devstack
   doesn't push a tag at RC1 it is just branched off of HEAD.

#. After devstack is branched, remind the QA PTL to create a branch in the
   grenade repository. As with devstack, it will branch from HEAD instead of a
   tag.

#. Remind the QA PTL to update the default branch for devstack in the new
   stable branch. For example, https://review.opendev.org/#/c/493208/

#. Remind the QA PTL to update the grenade settings in devstack-gate for the
   new branch. For example, https://review.opendev.org/362438.

   .. note::

      As soon as grenade is updated for the new branch (see the RC1
      instructions that follow), projects without stable branches may
      start seeing issues with their grenade jobs because without the
      stable branch the branch selection will cause the jobs to run
      master->master instead of previous->master. At the end of Ocata
      this caused trouble for the Ironic team, for example.

#. Remind the I18n PTL to update the translation tools for the new stable
   series.

#. After all cycle-with-rc projects have their branches created, remind the
   requirements PTL to propose an update to the deliverable file to create the
   ``stable/$series`` branch for ``openstack/requirements``. Then announce that
   the requirements freeze is lifted from master.

   .. note::

      We wait until after the other projects have branched to
      create the branch for requirements because tests for the stable
      branches of those projects will fall back to using the master
      branch of requirements until the same stable branch is created,
      but if the branch for the requirements repo exists early the
      changes happening in master on the other projects will not use it
      and we can have divergence between the requirements being tested
      and being declared as correct.

#. Remind the QA PTL to create new branch specific jobs for our two branchless
   projects, devstack-gate and tempest, in the tempest repo. Configure tempest
   to run them on all changes, voting. Configure tempest to run them as
   periodic bitrot jobs as well. All this can be done in one tempest patch,
   for example, see https://review.opendev.org/521888.
   Configure devstack-gate to run the new jobs in check pipeline only,
   non-voting, for example see https://review.opendev.org/545144.

#. Remind the QA PTL to add the new branch to the list of branches in the
   periodic-stable job templates in openstack-zuul-jobs. For example, see
   https://review.opendev.org/545268/.

Between RC1 and Final
=====================

#. In the countdown email, remind everyone that the latest RC (for
   cycle-with-rc deliverables) or the latest intermediary release (for
   cycle-with-intermediary deliverables) will automatically be used as
   the final $series release on release day.

#. Let cycle-with-rc projects iterate on RCs as needed. The final release
   candidate for each project needs to be prepared at least one week before
   the final release date.

   .. note::

      Try to avoid creating more than 3 release candidates so we are not
      creating candidates that consumers are then trained to ignore. Each
      release candidate should be kept for at least 1 day, so if there is a
      proposal to create RCx but clearly a reason to create another one,
      delay RCX to include the additional patches. Teams that know they will
      need additional release candidates can submit the requests and mark
      them WIP until actually ready, so the release team knows that more
      candidates are coming.

#. Ensure that all projects that are publishing release notes have the
   notes link included in their deliverable file. See
   ``tools/add_release_note_links.sh``.

#. Encourage liaisons to merge all translation patches.

#. When all translations and bug fixes are merged for a project,
   prepare a new release candidate.

#. After final releases for release:cycle-with-intermediary projects
   are tagged, create their stable branches.

#. On the morning of the deadline for final release candidates, check
   the list of unreleased changes for cycle-with-rc projects and verify
   with the PTLs and liaisons that they are planning a release or that
   they do not need one.

   In the releases repository working directory, run::

     $ ./tools/list_rc_updates.sh

#. Propose stable/$series branch creation for deliverables that have not
   requested it yet.

#. As soon as the last release candidate is tagged and the freeze
   period is entered, use ``propose-final-releases`` to tag the
   existing most recent release candidates as the final release for
   projects using the cycle-with-rc model.

#. Ask liaisons and PTLs of milestone-based projects to review and +1
   the final release proposal from the previous step so their approval
   is included in the metadata that goes onto the signed tag.

#. The week before final release test the release process using the
   ``openstack/release-test`` repository to ensure our machinery is functional.

#. Notify the documentation team that it should be safe to apply
   their process to create the new release series landing pages for
   docs.openstack.org. Their process works better if they wait until
   most of the projects have their stable branches created, but they
   can do the work before the final release date to avoid having to
   synchronize with the release team on that day.

Final Release
=============

#. Approve the final release patch created earlier.

   .. note::

      This needs to happen several hours before the press release
      from the foundation (to give us time to handle failures) but not
      too far in advance (to avoid releasing the day before the press
      release).

#. Run the ``missing-releases`` script to check for missing tarballs on the
   release page before the announcement::

      tox -e venv -- missing-releases --series $SERIES

   If there are any missing deliverables, fix them.

#. Mark series as released on releases.o.o, by updating doc/source/index.rst
   and doc/source/$series/index.rst.
   See https://review.opendev.org/#/c/381006 for an example.

   .. note::

      This item can be staged as a patch on top of the final release patch.

#. Update the default series name in
   ``openstack/releases/openstack_releases/defaults.py`` to use the
   new series name.

   .. note::

      This item can be staged as a patch on top of the previous patch.
      Only workflow when previous step *fully* ready

#. Send release announcement email to
   ``openstack-announce@lists.openstack.org``, based on
   ``templates/final.txt``. Coordinate the timing of the email with
   the press release from the Foundation staff.

#. Send an email to the openstack-discuss list to point to the official
   release announcement from the previous step, and declare
   ``openstack/releases`` unfrozen for releases on the new series.

Post-Final Release
==================

#. The week after the final release, process any late or blocked
   release requests for deliverables for any branch (treating the new
   series branch as stable).

#. Prepare for the next release cycle by adding deliverable files under the
   next cycle's directory. Remove any deliverable files from the current cycle
   that ended up not having any releases. Then run the following command to use
   the current cycle deliverables to generate placeholders for the next cycle::

      tox -e venv -- init-series $SERIES $NEXT_SERIES

#. Remind PTLs of cycle-trailing projects to prepare their releases.

