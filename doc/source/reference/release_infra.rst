======================
Release infrastructure
======================

What happens when a release is approved? Release infrastructure is divided
into two steps, triggered by different, but related events.

The first step is triggered by the release request being merged into the
releases repository, starting a series of jobs in the "post" pipeline
of the releases repository::

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
of jobs in the "tag" pipeline and the "release" pipeline (or "pre-release"
pipeline, in case of beta versions) of the repository the tag landed in::

  Tag is created -----------------------------------------------
        |                                                      |
   +----v------------------------------------+      +----------v-----------+
          Release pipeline (each repo)              Tag pipeline (each repo)
   +----+---------------+---------------+----+      +----------------------+
        |               |               |                      |
        v               v               v                      v
  +-----+-----+   +-----+-----+   +-----+-----+          +-----+-----+
  |  release  |   |  announce |   |  propose  |          |  publish  |
  |           |   |           |   |constraints|          |  release  |
  |(builds    |   |  (sends   |   |  update   |          |  notes    |
  | tarball   |   |   email)  |   |           |          |           |
  | & uploads |   |           |   +-----------+          +-----------+
  | it)       |   +-----------+
  +-----------+

Note that a single release request can create multiple tags in different
repositories, triggering that second stage in multiple repositories.

Jobs in the release pipeline need information from the release request
(like series name, or whether to upload to pypi). We use metadata in the
git tag itself to pass that information: the "tag" job in step 1 records
the information in the tag, and the jobs in step 2 retrieve that information
directly from the tag.
