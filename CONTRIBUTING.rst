======================================
Release management contribution ladder
======================================

Getting involved with release management can feel a bit overwhelming.
To set expectations reasonably, we define 4 levels of engagement.

Stage 0 - Review release requests
=================================

This stage does not require any special rights. You should just review
release requests (modifications of files in deliverables/ directory in
the releases repository), apply the release review rules and vote.

Release review guidelines
-------------------------

Three test jobs run for every release request:

* openstack-tox-validate checks for proper yaml format and schema validation
  and checks for things like proper job types and valid release note links

* releases-tox-list-changes finds included commits, lists PTL and release
  liaison, requirements changes, and open reviews for docs and release notes

* build-openstack-sphinx-docs performs a build of the releases website and
  checks for errors.

You should:

* check that the version bump matches semver rules. In particular, a .Z bump
  means only bugfixes should be listed in list-changes.

* check the output of the test jobs.

* Place your vote based on whether you think the request should be accepted
  as-is or not.


Stage 1 - Approving release requests
====================================

At this stage you will be trusted with CodeReview+2 and Workflow+1 votes
on the releases repository, giving you the ability to trigger releases.
You will need a base understanding of the release machinery, and know
to refrain from approving when unsure.

Release infrastructure primer
-----------------------------

What happens when a release is approved? Release infrastructure is divided
into two steps, triggered by different, but related events.

The first step is triggered by the release request being merged into the
releases repository, starting a series of jobs in the "post" pipeline
of the releases repository:

Release request merged
            |
    +-------v-----------------------+
      Post pipeline (releases repo)
    +---+-----------------------+---+
        |                       |
        v                       v
+-------+-------+       +-------+-------+
|      tag      |       |  publish-docs |
|               |       |               |
| (pushes tags  |       | (to releases  |
| to each repo) |       |     website)  |
|               |       |               |
+-------+-------+       +---------------+

The second step is triggered by the creation of the tag, creating a series
of jobs in the "release" pipeline (or "pre-release" pipeline, in case of beta
versions) of the repository the tag landed in:

  Tag is created
        |
   +----v------------------------------------+
          Release pipeline (each repo)
   +----+---------------+---------------+----+
        |               |               |
        v               v               v
  +-----+-----+   +-----+-----+   +-----+-----+
  |  release  |   |  announce |   |  propose  |
  |           |   |           |   |constraints|
  |(builds    |   |  (sends   |   |  update   |
  | tarball   |   |   email)  |   |           |
  | & uploads |   |           |   +-----------+
  | it)       |   +-----------+
  +-----------+

Note that a single release request can create multiple tags in different
repositories, triggering that second stage in multiple repositories.

Jobs in step 2 need information from the release request (like series name,
or whether to upload to pypi). We use metadata in the git tag itself to pass
that information: the "tag" job in step 1 records the information in the tag,
and the jobs in step 2 retrieve that information directly from the tag.


Checklist before approving a release
-------------------------------------

* You should only approve release requests.
* You should check that release is approved by PTL or release liaison
* You should check that infrastructure is not currently experiencing issues
* You should check that we are not in any freeze period
* If unsure, it is better to wait for a second opinion that to press
  Workflow+1 directly.


Stage 2 - Knowing the release cycle process
===========================================

At this stage you will be able to help drive the release cycle process,
send reminder emails and answer questions from release liaisons.


Stage 3 - Understanding the Release Automation Infrastructure
=============================================================

At this stage you will be able to debug complex release infrastructure
failures, and review/approve release tooling changes.

