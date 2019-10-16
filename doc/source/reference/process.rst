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

#. Create the $series-relmgt-tracking etherpad using the
   ``make-tracking-etherpad`` command.
   For example::

       tox -e venv -- make-tracking-pad ussuri

   The output from this command can be pasted into a
   ``$SERIES-relmgt-tracking`` etherpad. Set title formatting for the top
   sections. Then highlight all listed weeks and set to **Heading 3** style.
   Fill in the contents of one of the weeks with the typical items, then copy
   and past that into each subsequent week to prepare for the rest of the
   cycle.

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

   Intermediary-released deliverables that did release only once during
   the last cycle, and have not done a release yet are good candidates to
   switch to the cycle-with-rc model, which is much more suitable for
   deliverables that are only released once per cycle.

   Propose a release model change for all deliverables meeting that criteria.
   PTLs and release liaisons may decide to:

   - immediately release an intermediary release (and -1 the proposed change)
   - confirm the release model change (+1 the proposed change)
   - stay uncertain for this cycle of how many releases will be made, but
     acknowledge that they need to do a release before RC1 (-1 the proposed
     change)

#. Two weeks before Milestone-3, include a reminder about the final
   library release freeze coming the week before Milestone-3.

   #. Run the following command to get a list of libraries::

        tools/list_library_unreleased_changes.sh

   #. Include list of unreleased libraries in the email to increase visibility.

#. One week before Milestone-3, include a reminder about the final
   client library release freeze coming the week of Milestone-3.

   #. Run the following command to get a list of client libraries::

        tools/list_client_library_unreleased_changes.sh

   #. Include list of unreleased client libraries in the email to increase
      visibility.

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

R-6 week (Final Library Release deadline)
=========================================

#. Propose autoreleases for cycle-with-intermediary libraries (excluding
   client libraries) which had commits that have not been included in a
   release.

   - List them using::

      ./tools/list_library_unrelease_changes.sh

   - That patch will be used as a base to communicate with the
     team: if a team wants to wait for a specific patch to make it to the
     library, someone from the team can -1 the patch to have it held, or update
     that patch with a different commit SHA.

     .. note::

      At this point, we want *all* changes in the deliverables, to ensure
      that we have CI configuration up to date when the stable branch
      is created later.

   - Allow the ``stable/$series`` branch to be requested with each library
     final release if they know they are ready. Do not require branching at
     this point in case of critical issues requiring another approved release
     past the freeze date.

   - Between Tuesday and Thursday, merge as soon as possible the patches that
     get +1 from the PTL or the release liaison.

   - On the Friday, merge patches that did not get any feedback from PTL or
     release liaison. Discuss standing -1s to see if they should be granted
     an exception and wait until next week.

#. Update the feature list and allowed stable branch names in
   devstack-gate for the new stable branch. For
   example, https://review.opendev.org/362435 and
   https://review.opendev.org/363084

#. At the end of the week, send weekly email content preparing for R-5 week::

    Development Focus
    -----------------

    We are getting close to the end of the $series cycle! Next week on
    $milestone3 is the $series-3 milestone, also known as feature freeze.
    It's time to wrap up feature work in the services and their client
    libraries, and defer features that won't make it to the $next-series cycle.

    General Information
    -------------------

    This coming week is the deadline for client libraries: their last feature
    release needs to happen before "Client library freeze" on $milestone3.
    Only bugfix releases will be allowed beyond this point.

    When requesting those library releases, you can also include the
    stable/$series branching request with the review. As an example, see the
    "branches" section here:
    https://opendev.org/openstack/releases/src/branch/master/deliverables/pike/os-brick.yaml#n2

    $milestone3 is also the deadline for feature work in all OpenStack
    deliverables following the cycle-with-rc model. To help those projects
    produce a first release candidate in time, only bugfixes should be allowed
    in the master branch beyond this point. Any feature work past that deadline
    has to be raised as a Featur Freeze Exception (FFE) and approved by the
    team PTL.

    Finally, feature freeze is also the deadline for submitting a first version
    of your cycle-highlights. Cycle highlights are the raw data hat helps shape
    what is communicated in press releases and other release activity at the
    end of the cycle, avoiding direct contacts from marketing folks. See
    https://docs.openstack.org/project-team-guide/release-management.html#cycle-highlights
    for more details.

    Upcoming Deadlines & Dates
    --------------------------

    $series-3 milestone (feature freeze): $milestone3 (R-5 week)
    RC1 deadline: $rc1-deadline (R-3 week)
    Final RC deadline: $final-rc-deadline (R-1 week)
    Final Train release: $release-date
    $other-upcoming-event


R-5 week (Milestone-3)
======================

#. Process any remaining library freeze exception.

#. Early in the week, email openstack-discuss list to remind PTLs that
   cycle-highlights are due this week so that they can be included in
   release marketing preparations.

#. Propose autoreleases for cycle-with-intermediary client libraries which
   had commits that have not been included in a release.

   - List them using::

      ./tools/list_client_library_unreleased_changes.sh

   - That patch will be used as a base
     to communicate with the team: if a team wants to wait for a specific patch
     to make it to the library, someone from the team can -1 the patch to have
     it held, or update that patch with a different commit SHA.

   - Allow the ``stable/$series`` branch to be requested with each client
     library final release if they know they are ready. Do not require
     branching at this point in case of critical issues requiring another
     approved release past the freeze date.

   - Between Tuesday and Thursday, merge as soon as possible the patches that
     get +1 from the PTL or the release liaison.

   - On the Friday, merge patches that did not get any feedback from PTL or
     release liaison. Discuss standing -1s to see if they should be granted
     an exception and wait until next week.

#. Evaluate any libraries that did not have any change merged over the
   cycle to see if it is time to `transition them to the independent release
   model <https://releases.openstack.org/reference/release_models.html#openstack-related-libraries>`__.

   If it is OK to transition them, propose to move the deliverable file to
   the ``_independent`` directory.

   If it is not OK to transition them, create a new stable branch from the
   latest release from the previous series.

#. List cycle-with-intermediary deliverables that have not been released yet::

     tox -e venv -- list-deliverables --unreleased \
     --model cycle-with-intermediary \
     --type horizon-plugin --type other --type service

   Send a separate email targeted to teams with such unreleased deliverables
   saying::

    Quick reminder that we'll need a release very soon for a number of
    deliverables following a cycle-with-intermediary release model but which
    have not done *any* release yet in the $series cycle:

    {{list-of-deliverables}}

    Those should be released ASAP, and in all cases before $rc1-deadline, so
    that we have a release to include in the final $series release.

#. On Friday, remind the requirements team to freeze changes to
   ``openstack/requirements`` by applying -2 to all
   open patches. Ensure that reviewers do not approve changes created
   by the proposal bot, but do approve changes for new OpenStack deliverable
   releases.

#. At the end of the week, send weekly email content for R-3 week::

    Development Focus
    -----------------

    We just passed feature freeze! Until release branches are cut, you
    should stop accepting featureful changes to deliverables following the
    cycle-with-rc release model, or to libraries. Exceptions should be
    discussed on separate threads on the mailing-list, and feature freeze
    exceptions approved by the team's PTL.

    Focus should be on finding and fixing release-critical bugs, so that
    release candidates and final versions of the $series deliverables can be
    proposed, well ahead of the final $series release date.

    General Information
    -------------------

    We are still finishing up processing a few release requests, but the
    $series release requirements are now frozen. If new library releases are
    needed to fix release-critical bugs in $series, you must request a
    Requirements Freeze Exception (RFE) from the requirements team before we
    can do a new release to avoid having something released in $series that
    is not actually usable. This is done by posting to the openstack-discuss
    mailing list with a subject line similar to:

            [$PROJECT][requirements] RFE requested for $PROJECT_LIB

    Include justification/reasoning for why a RFE is needed for this lib.
    If/when the requirements team OKs the post-freeze update, we can then
    process a new release.

    A soft String freeze is now in effect, in order to let the I18N team do the
    translation work in good conditions. In Horizon and the various dashboard
    plugins, you should stop accepting changes that modify user-visible
    strings. Exceptions should be discussed on the mailing-list. By
    $rc-final-date this will become a hard string freeze, with no changes
    in user-visible strings allowed.

    Actions
    -------

    stable/$series branches should be created soon for all not-already-branched
    libraries. You should expect 2-3 changes to be proposed for each: a
    .gitreview update, a reno update (skipped for projects not using reno),
    and a tox.ini constraints URL update. Please review those in priority
    so that the branch can be functional ASAP.

    The Prelude section of reno release notes is rendered as the top level
    overview for the release. Any important overall messaging for $series
    changes should be added there to make sure the consumers of your release
    notes see them.

    Finally, if you haven't proposed $series cycle-highlights yet, you are
    already late to the party. Please see $email for details.

    Upcoming Deadlines & Dates
    --------------------------

    RC1 deadline: $rc1-deadline (R-3 week)
    Final RC deadline: $final-rc-deadline (R-1 week)
    Final Train release: $release-date
    $other-upcoming-event


R-4 week
========

#. Process any remaining client library freeze exception.

#. Freeze all cycle-based library releases except for release-critical
   bugs. Independently-released libraries may still be released, but
   constraint or requirement changes will be held until after the freeze
   period.

   .. note::

      Do not release libraries without a link to a message to openstack-discuss
      requesting a requirements RFE and an approval response from that team.

#. Propose ``stable/$series`` branch creation for all client and non-client
   libraries that had not requested it at freeze time.

   - The following command may be used::

      tox -e venv -- propose-library-branches --include-clients

   - That patch will be used as a base
     to communicate with the team: if a team wants to wait for a specific patch
     to make it to the library, someone from the team can -1 the patch to have
     it held, or update that patch with a different commit SHA.

   - On the Friday, merge patches that did not get any feedback from PTL or
     release liaison. Discuss standing -1s to see if they should be granted
     an exception and wait until next week.

#. List cycle-with-intermediary deliverables that have not been refreshed in
   the last 2 months. For this, use the following command, with YYYY-MM-DD
   being the day two months ago::

     tox -e venv -- list-deliverables --unreleased-since YYYY-MM-DD
     --model cycle-with-intermediary \
     --type horizon-plugin --type other --type service

   Send a separate email targeted to teams with such old deliverables
   saying::

    Quick reminder that for deliverables following the cycle-with-intermediary
    model, the release team will use the latest $series release available on
    release week.

    The following deliverables have done a $series release, but it was not
    refreshed in the last two months:

     {{list_of_deliverables}}

    You should consider making a new one very soon, so that we don't use an
    outdated version for the final release.

#. At the end of the week, send weekly email content preparing for R-3 week::

    Development Focus
    -----------------

    The Release Candidate (RC) deadline is next Thursday, $rc1-deadline. Work
    should be focused on fixing any release-critical bugs.

    General Information
    -------------------

    All deliverables released under a cycle-with-rc model should have a first
    release candidate by the end of the week, from which a stable/$series
    branch will be cut. This branch will track the $series release.

    Once stable/$series has been created, master will will be ready to switch
    to $next-series development. While master will no longer be feature-frozen,
    please prioritize any work necessary for completing $series plans.
    Release-critical bugfixes will need to be merged in the master branch
    first, then backported to the stable/$series branch before a new release
    candidate can be proposed.

    Actions
    -------

    Early in the week, the release team will be proposing RC1 patches for all
    cycle-with-rc projects, using the latest commit from master. If your team
    is ready to go for cutting RC1, please let us know by leaving a +1 on these
    patches.

    If there are still a few more patches needed before RC1, you can -1 the
    patch and update it later in the week with the new commit hash you would
    like to use. Remember, stable/$series branches will be created with this,
    so you will want to make sure you have what you need included to avoid
    needing to backport changes from master (which will technically then be
    $next-series) to this stable branch for any additional RCs before the final
    release.

    The release team will also be proposing releases for any deliverable
    following a cycle-with-intermediary model that has not produced any $series
    release so far.

    Finally, now is a good time to finalize release highlights. Release
    highlights help shape the messaging around the release and make sure that
    your work is properly represented.

    Upcoming Deadlines & Dates
    --------------------------

    RC1 deadline: $rc1-deadline (R-3 week)
    Final RC deadline: $final-rc-deadline (R-1 week)
    Final Train release: $release-date
    $other-upcoming-event


R-3 week (RC1 deadline)
=======================

#. Process any remaining library branching exception.

#. On the Monday, generate release requests for all deliverables
   that have do not have a suitable Train candidate yet. That includes:

   - Using `release-test` as a canary test. `release-test`
     needs to have a RC1 anyway for preparing the final release.

   - cycle-with-intermediary deliverables that have not released yet, for
     which a release should be proposed from HEAD, and include stable branch
     creation. You can list those using::

       tox -e venv -- list-deliverables --unreleased \
       --model cycle-with-intermediary \
       --type horizon-plugin --type other --type service

   - cycle-with-rc deliverables that have not done a RC1 yet, for which
     a release should be proposed from HEAD, and include stable branch
     creation. You can list those using::

       tox -e venv -- list-deliverables --missing-rc --model cycle-with-rc

   - cycle-automatic deliverables, for which a final release should be
     proposed from HEAD (unless there is an existing release in the cycle
     and no change was merged since). Those should **not** include stable
     branch creation. You can list those using::

       tox -e venv -- list-deliverables --model cycle-automatic

   - Those patches will be used as a base to communicate with the team:
     if a team wants to wait for a specific patch to make it to the release,
     someone from the team can -1 the patch to have it held, or update
     that patch with a different commit SHA.

   - Between Tuesday and Thursday, merge as soon as possible the patches that
     get +1 from the PTL or the release liaison.

   - By EOD Thursday, ideally we would want a +1 from the PTL and/or
     release liaison to indicate approval. However we will consider the
     absence of -1 or otherwise negative feedback as an indicator that the
     automatically proposed patches can be approved.

   - On the Friday, merge patches that did not get any feedback from PTL or
     release liaison. Discuss standing -1s to see if they should be granted
     an exception and wait until next week.

#. At the end of the week, send weekly email content preparing for R-2 week::

    Development Focus
    -----------------

    At this point we should have release candidates (RC1 or recent intermediary
    release) for all the $series deliverables. Teams should be working on any
    release-critical bugs that would require another RC or intermediary release
    before the final release.

    Actions
    -------

    Early in the week, the release team will be proposing stable/$series branch
    creation for all deliverables that have not branched yet, using the latest
    available $series release as the branch point. If your team is ready to go
    for creating that branch, please let us know by leaving a +1 on these
    patches.

    If you would like to wait for another release before branching, you can -1
    the patch and update it later in the week with the new release you would
    like to use. By the end of the week the release team will merge those
    patches though, unless an exception is granted.

    Once stable/$series branches are created, if a release-critical bug is
    detected, you will need to fix the issue in the master branch first, then
    backport the fix to the stable/$series branch before releasing out of the
    stable/$series branch.

    After all of the cycle-with-rc projects have branched we will branch
    devstack, grenade, and the requirements repos. This will effectively open
    them up for $next-series development, though the focus should still be on
    finishing up $series until the final release.

    For projects with translations, watch for any translation patches coming
    through and merge them quickly. A new release should be produced so that
    translations are included in the final $series release.

    Finally, now is a good time to finalize release notes. In particular,
    consider adding any relevant "prelude" content. Release notes are
    targetted for the downstream consumers of your project, so it would be
    great to include any useful information for those that are going to pick
    up and use or deploy the $series version of your project.

    Upcoming Deadlines & Dates
    --------------------------

    Final RC deadline: $final-rc-deadline (R-1 week)
    Final Train release: $release-date
    $other-upcoming-event


R-2 week
========

#. Process any standing RC1 deadline exceptions.

#. On the Monday, generate stable branches for all cycle deliverables that
   are still missing one.

   - You can list those using::

         tox -e venv -- list-deliverables --no-stable-branch

   - Those patches will be used as a base to communicate with the team:
     if a team wants to wait and make another release before the branch is
     cut, someone from the team can -1 the patch to have it held, or update
     that patch to include another release and stable branch point.

   - Between Tuesday and Thursday, merge as soon as possible the patches that
     get +1 from the PTL or the release liaison.

   - On the Friday, merge patches that did not get any feedback from PTL or
     release liaison. Discuss standing -1s to see if they should be granted
     an exception and wait until next week.

#. After all the projects enabled in devstack by default have been branched,
   we can engage with the QA, I18n and Requirements PTLs to finalize the
   stable branch setup:

   - Remind the QA PTL to create a branch in the devstack repository.
     Devstack doesn't push a tag at RC1 it is just branched off of HEAD.

   - After devstack is branched, remind the QA PTL to create a branch in the
     grenade repository. As with devstack, it will branch from HEAD instead
     of a tag.

   - Remind the QA PTL to update the default branch for devstack in the new
     stable branch. For example, https://review.opendev.org/#/c/493208/

   - Remind the QA PTL to update the grenade settings in devstack-gate for the
     new branch. For example, https://review.opendev.org/362438.

     .. note::

        As soon as grenade is updated for the new branch (see the RC1
        instructions that follow), projects without stable branches may
        start seeing issues with their grenade jobs because without the
        stable branch the branch selection will cause the jobs to run
        master->master instead of previous->master. At the end of Ocata
        this caused trouble for the Ironic team, for example.

   - Remind the I18n PTL to update the translation tools for the new stable
     series.

   - After all cycle-with-rc projects have their branches created, remind the
     requirements PTL to propose an update to the deliverable file to create
     the ``stable/$series`` branch for ``openstack/requirements``. Then
     announce that the requirements freeze is lifted from master.

     .. note::

         We wait until after the other projects have branched to
         create the branch for requirements because tests for the stable
         branches of those projects will fall back to using the master
         branch of requirements until the same stable branch is created,
         but if the branch for the requirements repo exists early the
         changes happening in master on the other projects will not use it
         and we can have divergence between the requirements being tested
         and being declared as correct.

  - Remind the QA PTL to create new branch specific jobs for our two
    branchless projects, devstack-gate and tempest, in the tempest repo.
    Configure tempest to run them on all changes, voting. Configure tempest
    to run them as periodic bitrot jobs as well. All this can be done in one
    tempest patch, for example, see https://review.opendev.org/521888.
    Configure devstack-gate to run the new jobs in check pipeline only,
    non-voting, for example see https://review.opendev.org/545144.

  - Remind the QA PTL to add the new branch to the list of branches in the
    periodic-stable job templates in openstack-zuul-jobs. For example, see
    https://review.opendev.org/545268/.

#. Ensure that all projects that are publishing release notes have the
   notes link included in their deliverable file. See
   tools/add_release_note_links.sh.

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

#. At the end of the week, send weekly email content preparing for R-1 week::

    Development Focus
    -----------------

    We are on the final mile of the $series development cycle!

    Remember that the $series final release will include the latest release
    candidate (for cycle-with-rc deliverables) or the latest intermediary
    release (for cycle-with-intermediary deliverables) available.

    $final-rc-deadline is the deadline for final $series release candidates
    as well as any last cycle-with-intermediary deliverables. We will then
    enter a quiet period until we tag the final release on $release-date.
    Teams should be prioritizing fixing release-critical bugs, before that
    deadline.

    Otherwise it's time to start planning the $next-series development cycle,
    including discussing Forum and PTG sessions content, in preparation of
    $other-upcoming-event.

    Actions
    -------

    Watch for any translation patches coming through on the stable/$series
    branch and merge them quickly. If you discover a release-critical issue,
    please make sure to fix it on the master branch first, then backport the
    bugfix to the stable/$series branch before triggering a new release.

    Please drop by #openstack-release with any questions or concerns about
    the upcoming release !

    Upcoming Deadlines & Dates
    --------------------------

    Final Train release: $release-date
    $other-upcoming-event


R-1 week (Final RC deadline)
============================

#. Process any remaining stable branching exception.

#. On the morning of the deadline for final release candidates, check
   the list of unreleased changes for cycle-with-rc projects and verify
   with the PTLs and liaisons that they are planning a release or that
   they do not need one.

   In the releases repository working directory, run::

     $ ./tools/list_rc_updates.sh

#. As soon as the last release candidate is tagged and the freeze
   period is entered, use ``propose-final-releases`` to tag the
   existing most recent release candidates as the final release for
   projects using the cycle-with-rc model.

#. Ask liaisons and PTLs of milestone-based projects to review and +1
   the final release proposal from the previous step so their approval
   is included in the metadata that goes onto the signed tag.

#. Test the release process using the ``openstack/release-test``
   repository to ensure our machinery is functional.

#. Notify the documentation team that it should be safe to apply
   their process to create the new release series landing pages for
   docs.openstack.org. Their process works better if they wait until
   most of the projects have their stable branches created, but they
   can do the work before the final release date to avoid having to
   synchronize with the release team on that day.


R+0 week (Final Release)
========================

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

R+1 week
========

#. Process any late or blocked
   release requests for deliverables for any branch (treating the new
   series branch as stable).

#. Prepare for the next release cycle by adding deliverable files under the
   next cycle's directory. Remove any deliverable files from the current cycle
   that ended up not having any releases. Then run the following command to use
   the current cycle deliverables to generate placeholders for the next cycle::

      tox -e venv -- init-series $SERIES $NEXT_SERIES

#. Remind PTLs of cycle-trailing projects to prepare their releases.

#. Plan the next release cycle schedule based on the number of desired weeks or
   by making sure the cycle ends within a few weeks of the next developer
   event. Using the first Monday following the close of the last cycle, and the
   Monday of the planned last week of the new cycle, use the tool
   ``tools/weeks.py`` to generate the release schedule YAML file. For example::

        ./tools/list_weeks.py t 2019-04-15 2019-10-16

   The generated output can be used to set up the schedule similar to what was
   done for the `Ussuri release <https://review.opendev.org/#/c/679822/>`_.

