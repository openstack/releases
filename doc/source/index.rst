====================
 OpenStack Releases
====================

Release Series
==============

OpenStack is developed and released around 6-month cycles. After the initial
release, additional stable point releases will be released in each release
series. You can find the detail of the various release series here on their
series page. Subscribe to the `combined release calendar`_ for continual
updates.

.. _combined release calendar: schedule.ics

.. datatemplate:yaml::
   :source: series_status.yaml
   :template: series_status_table.tmpl

.. toctree::
   :glob:
   :maxdepth: 1
   :hidden:

   flamingo/index
   epoxy/index
   dalmatian/index
   caracal/index
   bobcat/index
   antelope/index
   zed/index
   yoga/index
   xena/index
   wallaby/index
   victoria/index
   ussuri/index
   train/index
   stein/index
   rocky/index
   queens/index
   pike/index
   ocata/index
   newton/index
   mitaka/index
   liberty/index
   kilo/index
   juno/index
   icehouse/index
   havana/index
   grizzly/index
   folsom/index
   essex/index
   diablo/index
   cactus/index
   bexar/index
   austin/index
   releases/*

.. note::
   The schedule of `Maintenance phases`_ changed during Ocata
   and also during 2024.1 Caracal.
   The `old phases`_ were used until Newton.
   The last series that transitioned to Extended Maintenance was Xena.
   The replacement of Extended Maintenance process to Unmaintained
   was formulated in the `2023-07-24 Unmaintained status replaces
   Extended Maintenance`_ resolution.

.. _extended-maintenance-note:

.. note::
   If a branch is marked as Extended Maintenance, that means individual
   projects can be in state *Maintained*, *Unmaintained*, *Last* or
   *End of Life* on that branch. Please check specific project about its
   actual status on the given branch.

.. _Maintenance phases: https://docs.openstack.org/project-team-guide/stable-branches.html#maintenance-phases
.. _old phases: https://github.com/openstack/project-team-guide/blob/1c837bf0~/doc/source/stable-branches.rst
.. _2023-07-24 Unmaintained status replaces Extended Maintenance: https://governance.openstack.org/tc/resolutions/20230724-unmaintained-branches.html

Series-Independent Releases
===========================

Some deliverables are released independently from the OpenStack release series.
You can find their releases listed here:

.. toctree::
   :maxdepth: 1

   independent

.. _slurp:

Releases with Skip Level Upgrade Release Process (SLURP)
========================================================

Releases can be marked as `Skip Level Upgrade Release Process`_ (or
`SLURP`) releases. This practically means, that upgrades will be
supported between these (`SLURP`) releases, in addition to between
adjacent major releases. For example the upgrade paths starting with
the 2023.1 Antelope release look like this:

.. image:: _images/slurp.png
   :width: 800
   :alt: Slurp Upgrade Path

.. _Skip Level Upgrade Release Process: https://governance.openstack.org/tc/resolutions/20220210-release-cadence-adjustment.html

Teams
=====

Deliverables are produced by `project teams`_. Here you can find all OpenStack
deliverables, organized by the team that produces them:

.. toctree::
   :maxdepth: 1
   :glob:

   teams/*

.. _project teams: https://governance.openstack.org/tc/reference/projects/index.html

Cryptographic Signatures
========================

Git tags created through our release automation are signed by
`centrally-managed OpenPGP keys`_ maintained by the `OpenStack
TaCT SIG`_. Detached signatures of many separate release
artifacts are also provided using the same keys. A new key is
created corresponding to each development cycle and rotated
relatively early in the cycle. (Implementation completed late in the
Newton cycle, so many early Newton artifacts have no corresponding
signatures.) Copies of the public keys can be found below along with
the date ranges during which each key was in general use.

* 2016-08-03..2016-11-22 (Newton Cycle key):
  `key 0x80fcce3dc49bd7836fc2464664dbb05acc5e7c28`_
* 2016-11-22..2017-03-24 (Ocata Cycle key):
  `key 0xd47bab1b7dc2e262a4f6171e8b1b03fd54e2ac07`_
* 2017-03-24..2017-09-15 (Pike Cycle key):
  `key 0xc96bfb160752606daa0de2fa05eb5792c876df9a`_
* 2017-09-15..2018-03-19 (Queens Cycle key):
  `key 0x4c8b8b5a694f612544b3b4bac52f01a3fbdb9949`_
* 2018-03-19..2018-09-05 (Rocky Cycle key):
  `key 0xc31292066be772022438222c184fd3e1edf21a78`_
* 2018-09-05..2019-06-11 (Stein Cycle key):
  `key 0x27023b1ffccd8e3ae9a5ce95d943d5d270273ada`_
* 2019-06-11..2019-10-29 (Train Cycle key):
  `key 0xcdc08088c3cb45a9be08332b2354069e5b504663`_
* 2019-10-29..2020-05-21 (Ussuri Cycle key):
  `key 0xbba3b1e67a7303dd1769d34595bf2e4d09004514`_
* 2020-05-21..2020-10-30 (Victoria Cycle key):
  `key 0x2426b928085a020d8a90d0d879ab7008d0896c8a`_
* 2020-10-30..2021-05-06 (Wallaby Cycle key):
  `key 0x5d2d1e4fb8d38e6af76c50d53d4fec30cf5ce3da`_
* 2021-05-06..2021-10-27 (Xena Cycle key):
  `key 0x4c29ff0e437f3351fd82bdf47c5a3bc787dc7035`_
* 2021-10-27..2022-04-09 (Yoga Cycle key):
  `key 0x01527a34f0d0080f8a5db8d6eb6c5df21b4b6363`_
* 2022-04-09..2022-10-07 (Zed Cycle key):
  `key 0xa63ea142678138d1bb15f2e303bdfd64dd164087`_
* 2022-10-07..2023-03-31 (2023.1/Antelope Cycle key):
  `key 0xa7475c5f2122fec3f90343223fe3bf5aad1080e4`_
* 2023-03-31..2023-10-09 (2023.2/Bobcat Cycle key):
  `key 0x815afec729392386480e076dcc0dfe2d21c023c9`_
* 2023-10-09..2024-04-08 (2024.1/Caracal Cycle key):
  `key 0x2ef3fe0ec2b075ab7458b5f8b702b20b13df2318`_
* 2024-04-08..2024-10-07 (2024.2/Dalmatian Cycle key):
  `key 0xf8675126e2411e7748dd46662fc2093e4682645f`_
* 2024-10-07..present (2025.1/Epoxy Cycle key):
  `key 0x22284f69d9eccdf3df7819791c711af193ff8e54`_

.. Static key files are generated with the following command:
   ( gpg --fingerprint --keyid-format=0xlong \
   --list-options=no-show-uid-validity --list-sigs \
   0x80fcce3dc49bd7836fc2464664dbb05acc5e7c28 ; gpg \
   --armor --export 0x80fcce3dc49bd7836fc2464664dbb05acc5e7c28 ) > \
   doc/source/static/0x80fcce3dc49bd7836fc2464664dbb05acc5e7c28.txt
.. _`key 0x80fcce3dc49bd7836fc2464664dbb05acc5e7c28`: _static/0x80fcce3dc49bd7836fc2464664dbb05acc5e7c28.txt
.. _`key 0xd47bab1b7dc2e262a4f6171e8b1b03fd54e2ac07`: _static/0xd47bab1b7dc2e262a4f6171e8b1b03fd54e2ac07.txt
.. _`key 0xc96bfb160752606daa0de2fa05eb5792c876df9a`: _static/0xc96bfb160752606daa0de2fa05eb5792c876df9a.txt
.. _`key 0x4c8b8b5a694f612544b3b4bac52f01a3fbdb9949`: _static/0x4c8b8b5a694f612544b3b4bac52f01a3fbdb9949.txt
.. _`key 0xc31292066be772022438222c184fd3e1edf21a78`: _static/0xc31292066be772022438222c184fd3e1edf21a78.txt
.. _`key 0x27023b1ffccd8e3ae9a5ce95d943d5d270273ada`: _static/0x27023b1ffccd8e3ae9a5ce95d943d5d270273ada.txt
.. _`key 0xcdc08088c3cb45a9be08332b2354069e5b504663`: _static/0xcdc08088c3cb45a9be08332b2354069e5b504663.txt
.. _`key 0xbba3b1e67a7303dd1769d34595bf2e4d09004514`: _static/0xbba3b1e67a7303dd1769d34595bf2e4d09004514.txt
.. _`key 0x2426b928085a020d8a90d0d879ab7008d0896c8a`: _static/0x2426b928085a020d8a90d0d879ab7008d0896c8a.txt
.. _`key 0x5d2d1e4fb8d38e6af76c50d53d4fec30cf5ce3da`: _static/0x5d2d1e4fb8d38e6af76c50d53d4fec30cf5ce3da.txt
.. _`key 0x4c29ff0e437f3351fd82bdf47c5a3bc787dc7035`: _static/0x4c29ff0e437f3351fd82bdf47c5a3bc787dc7035.txt
.. _`key 0x01527a34f0d0080f8a5db8d6eb6c5df21b4b6363`: _static/0x01527a34f0d0080f8a5db8d6eb6c5df21b4b6363.txt
.. _`key 0xa63ea142678138d1bb15f2e303bdfd64dd164087`: _static/0xa63ea142678138d1bb15f2e303bdfd64dd164087.txt
.. _`key 0xa7475c5f2122fec3f90343223fe3bf5aad1080e4`: _static/0xa7475c5f2122fec3f90343223fe3bf5aad1080e4.txt
.. _`key 0x815afec729392386480e076dcc0dfe2d21c023c9`: _static/0x815afec729392386480e076dcc0dfe2d21c023c9.txt
.. _`key 0x2ef3fe0ec2b075ab7458b5f8b702b20b13df2318`: _static/0x2ef3fe0ec2b075ab7458b5f8b702b20b13df2318.txt
.. _`key 0xf8675126e2411e7748dd46662fc2093e4682645f`: _static/0xf8675126e2411e7748dd46662fc2093e4682645f.txt
.. _`key 0x22284f69d9eccdf3df7819791c711af193ff8e54`: _static/0x22284f69d9eccdf3df7819791c711af193ff8e54.txt

.. _`centrally-managed OpenPGP keys`: https://docs.openstack.org/infra/system-config/signing.html
.. _`OpenStack TaCT SIG`: https://governance.openstack.org/sigs/tact-sig.html

Documentation
=============

Content for this site is automatically generated from the data submitted to
the `openstack/releases`_ git repository. You can learn more about this
repository and the release management team processes in the following
documentation:

.. toctree::
   :maxdepth: 2
   :glob:

   reference/using
   reference/release_models
   reference/deliverable_types
   reference/join_release_team
   reference/reviewer_guide
   reference/release_infra
   reference/process

.. _`openstack/releases`: https://opendev.org/openstack/releases
