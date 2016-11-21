=======================
 Using This Repository
=======================

This repository is for tracking release requests for OpenStack
projects. The releases are managed using groups of "deliverables",
made up of individual project repositories sharing a Launchpad group
and a version number history. Many deliverables will only have one
constituent project.

Requesting a Release
====================

The PTL or release liaison for a project may request a release from
master by submitting a patch to this repository, appending the necessary
release metadata to the file describing the deliverable to be
released. The release team will review the request and provide
feedback about the version number.

The stable maintenance team, PTL, or release liaison for a project may
request a release from a stable branch by submitting a patch to this
repository, appending the necessary release metadata to the file
describing the deliverable to be released. The release team will
review the request and provide feedback about the version number. If
the stable release is requested by the stable maintenance team, it
should be acknowledged by the PTL or release liaison to ensure that
the development team is aware of the coming change.

Prepare the release request by submitting a patch to this
repository.

 * Always add the new release to the end of the file being edited. The
   version numbers will be reordered for display.

 * Always pick new version numbers for new releases. We do not update
   the contents of previously tagged releases, because that confuses
   users who have already downloaded those packages.

 * Set the first line (summary) of the commit message to the package
   name and version being requested.

 * If you are not the release liaison or PTL, have the PTL of the
   project acknowledge the request with a +1.

 * Do not used the "Depends-On" feature of zuul to make a release
   request depend on merging another patch in your project. The
   dependency management does not work properly in the release check
   jobs, and the validator requires that the patch listed in your
   deliverable file actually be merged into a proper branch.

 * Do not submit multiple dependent patches for multiple
   releases. Having a patch series with multiple releases means the
   release team cannot properly prioritize processing them. During
   milestone weeks, preference is given to milestone
   releases. Releases from stable branches, independent projects, and
   other types of releases are processed later. If your milestone
   release request depends on a request that is deprioritized, you may
   miss the deadline.

Reviewing a Release Request
---------------------------

Care needs to be taken when reviewing a release request such that the version
proposed (1) follows semver rules and (2) will not cause issues between
branches, particularly stable branches (at least stable branches that are not
yet using upper-constraints checking in CI runs, which is anything before
stable/liberty).

General notes when reviewing a release request:

* Make sure you follow semantic versioning rules `semver <http://semver.org/>`_
  when picking the version number. In particular, if there is a change going
  into this release which requires a higher minimum version of a dependency,
  then the **minor** version should be incremented.

  .. note:: The exception to this rule is when the versions of a project are
    pinned between minor versions in stable branches. In those cases we
    frequently release global-requirements syncs with a patch version to fix
    the target branch, e.g. stable/juno, but don't increment the minor version
    to avoid it being used in a different branch, like stable/kilo.
    Someone from the
    `stable-maint-core <https://review.openstack.org/#/admin/groups/530,members>`_
    team should +1 a change like this before it's approved.

* Make sure the summary of the patch includes the deliverable name and
  version number.

The following rules apply mostly to stable branches and therefore a member of
the `stable-maint-core <https://review.openstack.org/#/admin/groups/530,members>`_
team should +1 the following types of changes before they are approved.

* For libraries, check global-requirements.txt (g-r) in the
  `openstack/requirements repo <http://git.openstack.org/cgit/openstack/requirements/>`_
  to make sure the version you are about to release does not cause a
  conflict and wedge the gate. Typically this is only a concern on stable
  branches with (un)capped dependencies.

  Typical examples of this kind of break (before upper-constraints are used):

  #. A stable branch, for example stable/juno, has uncapped dependencies on a
     library and a version is released on a newer branch, e.g. stable/kilo,
     and that version has updated requirements from global-requirements in
     stable/kilo which conflict with the versions of libraries allowed in
     stable/juno. This then leads to ContextualVersionConflict failures when
     installing packages on stable/juno.
  #. Similar to the point above, but if there are overlapping version ranges
     between two branches, like stable/juno and stable/kilo, you can have the
     same kinds of issues where a release from one branch which has g-r syncs
     specific to that branch gets used in the other branch and things break.
     We saw this happen with oslo.utils 1.4.1 which was intended for
     stable/juno consumption but because stable/kilo g-r allowed that version,
     we broke stable/kilo CI jobs since 1.4.1 had juno-level dependencies.

* The rule of thumb is that branches should not overlap versions at the minor
  version range. For example, stable/juno can require foo>=1.1,<1.2 and
  stable/kilo can require foo>=1.2,<1.3. In this way only patch-level versions
  are released for foo on stable/juno and stable/kilo. The pin at the minor
  version range prevents those patch-level versions from breaking each other's
  branch.

Release Approval
================

Releases will only be denied during freeze weeks, periods where there
are known gate issues, or when releasing will introduce unwanted
instability. Releases made late in a week may be delayed until early
in the next week unless there is a pressing need such as a gate
failure or security issue.

Who is Responsible for the Release?
===================================

The release team is responsible for helping to clearly signal the
nature of the changes in the release through good version number
selection.

The project team is responsible for understanding the implications for
consuming projects when a new release is made, and ensuring that
releases do not break other projects. When breaks occur, the project
team is responsible for taking the necessary corrective action.

Deliverable Files
=================

Deliverable repositories for projects tagged with
release:cycle_with_intermediatry or release:cycle_with_milestones
should be placed in their respective releases within the
deliverables directory. Deliverable repositories for projects tagged with
release:indepedent should be placed in the ``deliverables/_independent``
directory.  Deliverable repositories tagged with release:none have no
release and are not tracked in this repository.

For deliverable set of projects, we use one YAML file per release
series to hold all of the metadata for all releases of that
deliverable. For each release, we need to track:

* the launchpad project name (such as ``oslo.config``)
* the series (Kilo, Liberty, etc.)
* the release model being used
* for each repository

  * the name (such as ``openstack/oslo.config``)
  * the hash of the commit to be tagged

* the version number to use
* highlights for the release notes email (optional)

We track this metadata for the history of all releases of the
deliverable, so we can render a set of release history documentation.

The file should be named based on the deliverable to be tagged, so
releases for ``liberty`` from the ``openstack/oslo.config`` repository
will have a file in ``openstack/releases`` called
``deliverables/liberty/oslo.config.yaml``. Releases of the same deliverable from
the ``stable/kilo`` branch will be described by
``deliverables/kilo/oslo.config.yaml``.

Deliverables File Schema
========================

The top level of a deliverable file is a mapping with keys:

``team``
  The name of the team that owns the deliverable, as listed in the
  governance repository data files.

``launchpad``
  The slug name of the launchpad project, suitable for use in URLs.

``release-notes``
  The URL or URLs to the published release notes for the deliverable
  for the series.

  Deliverables contained a single repository should simply include the
  URL to the notes for that repository. Deliverables made up of
  multiple repositories should use a hash to map each repository name
  to its notes URL.

``include-pypi-link``
  Either ``yes`` or ``no``, indicating whether the release
  announcement should include the link to the package on
  PyPI. Defaults to ``no``.

``release-model``
  Identify the release model used by the deliverable. See
  the reference section of the documentation for descriptions
  of the valid models.

``type``
  Categorize the deliverable based on what it does. See the reference
  section of the documentation for descriptions of the valid
  deliverable types.

``artifact-link-mode``
  Describe how to link to artifacts produced by the project. The
  default is ``tarball`. Valid values are:

    tarball
      Automatically generates links to version-specific files on
      tarballs.openstack.org.

    none
      Do not link to anything, just show the version number.

``repository-settings``
  Mapping of special settings to control the behavior for each repository, keyed
  by the repository name.

  ``flags``
    A list of flags attached to the repository.

    ``no-artifact-build-job``
      This repository has no job for building an artifact, but should
      be tagged anyway.

    ``retired``
      This repository is no longer used, but was present in old
      versions of a deliverable.

``release-type``
  This (optional) key sets the level of validation for the versions numbers.

  ``std``
      Default: Enforces 3 digit semver version numbers in releases and allows
      for common alpha, beta and dev releases.  This should be appropriate for
      most OpenStack release requirements.

  ``xstatic``
      Allows a more flexible versioning in line with xstatic package guidelines
      and requirements.

   ``fuel``
      The Fuel project manages its own packages.

``releases``
  A list of the releases for the deliverable.

Each `release` entry is a mapping with keys:

``version``
  The version tag for that release, to be applied to all of the member
  projects.

``projects``
  A list of all of the projects making up the deliverable for that
  release.

``highlights``
  An optional message to be included in the release note email
  announcing the release. (Use ``|`` to indicate a multi-line,
  pre-formatted message.)

Each `project` entry is a mapping with keys:

``repo``
  The name of the repository on git.openstack.org.

``hash``
  The SHA1 hash for the commit to receive the version tag.

``tarball-base``
  An optional name for the base of the tarball created by the
  release. If no value is provided, it defaults to the repo base name.

Examples
========

For example, one version of
``deliverables/liberty/oslo.config.yaml`` might contain::

   ---
   launchpad: oslo.config
   releases:
     - version: 1.12.0
       projects:
         - repo: openstack/oslo.config
           hash: 02a86d2eefeda5144ea8c39657aed24b8b0c9a39

and then for the subsequent release it would be updated to contain::

   ---
   launchpad: oslo.config
   releases:
     - version: 1.12.0
       projects:
         - repo: openstack/oslo.config
           hash: 02a86d2eefeda5144ea8c39657aed24b8b0c9a39
     - version: 1.12.1
       projects:
         - repo: openstack/oslo.config
           hash: 0c9113f68285f7b55ca01f0bbb5ce6cddada5023
       highlights: |
          This release includes the change to stop importing
          from the 'oslo' namespace package.

For deliverables with multiple repositories, the list of projects
would contain all of them. For example, the Neutron deliverable might
be described by ``deliverables/mitaka/neutron.yaml`` containing:

::

   ---
   launchpad: neutron
   release-notes:
     openstack/neutron: http://docs.openstack.org/releasenotes/neutron/mitaka.html
     openstack/neutron-lbaas: http://docs.openstack.org/releasenotes/neutron-lbaas/mitaka.html
     openstack/neutron-fwaas: http://docs.openstack.org/releasenotes/neutron-fwaas/mitaka.html
     openstack/neutron-vpnaas: http://docs.openstack.org/releasenotes/neutron-vpnaas/mitaka.html
   releases:
    - version: 8.0.0
      projects:
        - repo: openstack/neutron
          hash: 3213eb124e40b130e174ac3a91067e2b196788dd
        - repo: openstack/neutron-fwaas
          hash: ab5622891e2b1a7631f97471f55ffb9b5235e5ee
        - repo: openstack/neutron-lbaas
          hash: 19b18f05037dae4bbbada848aae6421da18ab490
        - repo: openstack/neutron-vpnaas
          hash: a1b12601a64a2359b2224fd4406c5db008484700

To allow tagging for repositories without build artifacts, set the
``no-artifact-build-job`` flag.

::

    ---
    launchpad: astara
    repository-settings:
      openstack/astara-appliance:
        flags:
          - no-artifact-build-job
    releases:
      - version: 9.0.0.0b1
        projects:
          - repo: openstack/astara-appliance
            hash: c21a64ea7b3b0fbdab8592afecdd31d9b8e64a6a

Helpers
=======

In order to help build out these files there are various command line
based tools that come with this repository. To install these it is as
easy as ``pip install .`` in this repository directory.

* ``list-changes`` that lists the changes in a given release file.
* ``interactive-release`` that goes through a *wizard* style set of
  questions to produce a new or updated release of a given project or
  set of projects.
* ``missing-releases`` scans deliverable files and verifies that all
  of the releases that should have been tagged by hand have been
