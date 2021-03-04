================
 Reviewer Guide
================

Review Inbox
============

.. reviewinbox::

General Review Considerations
=============================

As you're looking at any given review, you need to keep a few
different things in mind:

- Where are we in the release cycle? Some rules change depending on
  the phase we're in.
- What "release model" does the deliverable being released follow? The
  release model sets some general rules for version numbers and
  schedule.
- Which branch is the release on?

Many of the rules tied to these questions are enforced by the
validation job, so when you see an error understanding the rules helps
you understand the error message.

Approval Policies
=================

I prioritize the most current series, since that's where most
development work is going to happen.

For the stable series we have an arrangement with the
`stable-maint-core
<https://review.opendev.org/#/admin/groups/530,members>`_ team that
if a deliverable has the ``stable:follows-policy`` tag we don't
approve it until they have had a chance to review it (usually the
Monday after the request is submitted). Releases for deliverables that
do not have that governance tag can be approved at any time.

Releases from master can be approved with a single reviewer.

Code changes and doc changes and other things like that need 2
reviewers.

Releases from someone other than the PTL or release liaison must be
acknowledged by one of them with a +1 vote in gerrit.

Review Checks
=============

Does the commit message include the name of the deliverable and a
version number? If the request includes multiple deliverables it is OK
to include a team name and date.

The Validation Report
=====================

The validation job, ``openstack-tox-validate``, applies the validation
rules that can be automated.  It produces a text report in
``tox/validate-request-results.log``. The file contains the output of
what you would see if you ran ``tox -e validate`` for the patch.

The output is organized based on the rule being enforced.

We've tried to separate the "debug" output so it is easier to skim for
real content, with the important output left justified.

Warnings and errors are summarized at the bottom of the file.

The List Changes Report
=======================

The ``releases-tox-list-changes`` job produces a text report to
support human reviewers. It writes the report to
``tox/list-changes-results.log``. As with the validate job, it can be
run as ``tox -e list-changes`` locally.

Reviewers should read this log file for every review. It includes all
of the information needed to evaluate a release. The List Changes
Report has multiple sections you will need to review.

Release model
-------------

At the top of the file we get the release model, which tells us things
like when releases are allowed, what version numbers are allowed, etc.

Team details
------------

The "team details" section tells us the PTL and Liaison, so we know
who to make sure has acknowledged the request.  If one of those people
proposed the patch, we can go ahead without any delay.  Otherwise we
want to make sure one of them knows about the release and approves it
so that teams know we aren't going to release things they know are
broken, for example.

Tags
----

Next the report shows the governance tags for the repository.  If the
request is for a release on a stable branch and the project has that
``stable:follows-policy`` tag, there will be a large banner that says
the release needs to be approved by the stable team. Releases from
master will not include the banner, regardless of whether the
deliverable has the tag.

Details for commit receiving new tag X.Y.Z
------------------------------------------

In the "Details for commit receiving new tag..." section (below the DEBUG
lines) the report shows what git thinks the previous tag and number of
added patches should be. That's a quick way to verify that we aren't tagging
1.8.0 after 1.9.0 or something like that.

Check existing tags
-------------------

The next section shows any other tags already on the commit being tagged.
Sometimes a team will have a 3-part deliverable but only 1 part
changes in a release. If they have defined the 3 parts as 1
deliverable, they should tag all 3 anyway.

All branches with version numbers
---------------------------------

The next section shows what versions are on all of the branches.  This
is somewhat important, since for the first release off of master after
creating a stable branch we want to make sure we are moving ahead in
version numbers.  The validation job requires that least the Y value
in a X.Y.Z version number is incremented.

Branches containing commit
--------------------------

The next step shows which branch(es) contain(s) the commit. That's
useful for ensuring that someone has not merged 2 branches together
and we are not releasing off of the wrong branch.

For the current cycle, releases should always come from the ``master``
branch. Stable releases should come from the appropriate stable
branch.

Relationship to HEAD
--------------------

The "Relationship to HEAD" section tells us if the release will
skip any commits.  Sometimes someone uses a commit hash locally
that is older than the most recent commit on the branch.  If this
section does not say it is releasing HEAD (``Request releases from HEAD``),
it is good ask the submitter to verify that they're doing what they mean
to be doing. Sometimes they don't want to release the additional changes, and
sometimes they don't know about them.  It is not necessary to take
this extra precaution for milestone tags, because those are date-based
and it doesn't really matter if they don't include everything.  We
expect a lot of churn and progress around the milestone deadlines.

Open patches, Documentation patches and Patches with Release Notes
------------------------------------------------------------------

The next couple of sections show open patches matching various
criteria.  These are useful close to the release candidate phase of
the cycle.  When we are close to a freeze date the release team might
encourage teams to approve outstanding changes for requirements
updates, release notes, and translations before releasing.

Requirements Changes
--------------------

The next two sections, "Requirements Changes..." and "setup.cfg
Changes...", show the dependencies that have changed for the project
since the last time it was tagged.  We use those to ensure that the
exception to the SemVer rules is applied:

* Projects tagging a regular release (not a "pre-release" like an
  alpha, beta, or rc) need to increment at least the Y part of their
  version number when the minimum version of a dependency changes or
  when a new dependency is added.

The report shows the changes to the test requirements as the second
part of the "Requirements Changes" section. Those do not trigger Y
version changes.

Release X.Y.Z will include
--------------------------

The "Release $version will include" section shows the actual changes
being included in the new release -- the difference since the last
version was tagged.  This is where the subjective part of the review
really comes in.  If a patch release is being tagged and something in
this list looks like a new feature, we want them to tag a minor update
instead.  If anything in the list appears to describe a
backwards-incompatible change, we want them to tag a major version
update.

The ``git log`` section gives a more detailed view of the log messages.
Look for comments like "delete class X" or "add argument Y to method B" to
indicate the release will not be backwards-compatible.  It is not
necessary to *lower* a version number, say, if the release does not
have new features and has only fixed a bug.  Sometimes if there is
only one change and it is clearly a bug fix we may ask them to do
that, but most of the time releases include a mix of fixes and
features.

Another thing to look for is if there are only CI configuration
changes.  There is no reason to tag a release if the only change was
to the zuul or tox configuration, because the end user won't see those
changes. That happens sometimes with the projects that have a script
to prepare the release proposal.

The next part of the output (below the ``Release Notes``) shows the same
text that will appear in the release announcement email.  It is included so
that if building that text fails for some reason this job will fail and the
reno input files can be fixed instead of having the announce job fail.

Users of $PROJECT
-----------------

The final part of the output is a list of projects that have the
current deliverable being released in one of their dependency
lists.  That section is useful for evaluating the impact of a late
release when we're in the freeze period.

Release Jobs
============

When a release request is submitted the ``check-release-approval`` job
will be triggered to check that release requests were approved by PTL or
release liaison.

After a release request merges, the ``tag-releases`` job will start up
in the ``release-post`` pipeline.

``tag-releases`` reads the file from the releases repository and adds
the tag to the repository mentioned in the deliverable file.

Adding the tag triggers another job that actually builds the release
and uploads it.

.. ttx has a nice diagram of that, insert it here

After a Python package release is uploaded, the job
``propose-update-constraints`` submits a change to
``openstack/requirements`` to update the ``upper-constraints.txt``
list. The constraints list is used along with the actual requirements
list to tell the jobs which versions of which packages to
install. Since we maintain that list, every time we release something
that is constrained we want to make sure the value is updated.  The
job runs for all python packages, but not all of them are in the
constraint list so sometimes it does not submit a patch.

Release Job Failures
====================

When release jobs fail, messages are sent to release failure mailing
list:
http://lists.openstack.org/cgi-bin/mailman/listinfo/release-job-failures

Release Approval Status
=======================

Depending on the kind of job failures experienced it could be mandatory
to stop all our release approvals.

Indeed, sometimes job failures are systemic and should be fixed
first to avoid repeated failures wich could lead inconsistent states in our
coordinated releases.

To answer that case we defined three statuses to indicate if we should/shouldn't
continue to validate patch:

- ``RED``: no more approvals;
- ``ORANGE``: a transient status where we think that the issue is solved but
  approvals must be carefully monitored first;
- ``GREEN``: the issue have been fixed and everything works as expected.
  (approvals are reopen).

To inform all the release managers that something went wrong and ask them to
hold approvals then follow the following process:

1. open a new thread on the ML with for topic ``[release] Status: RED - $subject``
   to indicate the issue
2. notify directly the release managers on IRC (``#openstack-release``)

When you think that the problem is solved but that it still need some tests
you just have to reply on the thread by moving the topic from ``RED``
to ``ORANGE``.

When everything seems under control then you can reply on the thread by moving
the topic from ``ORANGE`` to ``GREEN``.
