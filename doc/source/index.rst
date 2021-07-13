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
   The schedule of `Maintenance phases`_ changed during Ocata.
   The `old phases`_ were used until Newton.

.. _extended-maintenance-note:

.. note::
   If a branch is marked as Extended Maintenance, that means individual
   projects can be in state *Maintained*, *Unmaintained*, *Last* or
   *End of Life* on that branch. Please check specific project about its
   actual status on the given branch.

.. _Maintenance phases: https://docs.openstack.org/project-team-guide/stable-branches.html#maintenance-phases
.. _old phases: https://github.com/openstack/project-team-guide/blob/1c837bf0~/doc/source/stable-branches.rst

Series-Independent Releases
===========================

Some deliverables are released independently from the OpenStack release series.
You can find their releases listed here:

.. toctree::
   :maxdepth: 1

   independent

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
Infrastructure team`_. Detached signatures of many separate release
artifacts are also provided using the same keys. A new key is
created corresponding to each development cycle and rotated
relatively early in the cycle. (Implementation completed late in the
Newton cycle, so many early Newton artifacts have no corresponding
signatures.)

OpenStack Infrastructure root sysadmins and Release Managers publish
their own signatures of these keys into the global keyserver
network. Copies of the public keys can be found below along with the
date ranges during which each key was in general use.

* 2016-08-03..2016-11-22 (Newton Cycle key):
  `key 0x80fcce3dc49bd7836fc2464664dbb05acc5e7c28`_ (details__)
* 2016-11-22..2017-03-24 (Ocata Cycle key):
  `key 0xd47bab1b7dc2e262a4f6171e8b1b03fd54e2ac07`_ (details__)
* 2017-03-24..2017-09-15 (Pike Cycle key):
  `key 0xc96bfb160752606daa0de2fa05eb5792c876df9a`_ (details__)
* 2017-09-15..2018-03-19 (Queens Cycle key):
  `key 0x4c8b8b5a694f612544b3b4bac52f01a3fbdb9949`_ (details__)
* 2018-03-19..2018-09-05 (Rocky Cycle key):
  `key 0xc31292066be772022438222c184fd3e1edf21a78`_ (details__)
* 2018-09-05..2019-06-11 (Stein Cycle key):
  `key 0x27023b1ffccd8e3ae9a5ce95d943d5d270273ada`_ (details__)
* 2019-06-11..2019-10-29 (Train Cycle key):
  `key 0xcdc08088c3cb45a9be08332b2354069e5b504663`_ (details__)
* 2019-10-29..2020-05-21 (Ussuri Cycle key):
  `key 0xbba3b1e67a7303dd1769d34595bf2e4d09004514`_ (details__)
* 2020-05-21..2020-10-30 (Victoria Cycle key):
  `key 0x2426b928085a020d8a90d0d879ab7008d0896c8a`_ (details__)
* 2020-10-30..2021-05-06 (Wallaby Cycle key):
  `key 0x5d2d1e4fb8d38e6af76c50d53d4fec30cf5ce3da`_ (details__)
* 2021-05-06..present (Xena Cycle key):
  `key 0x4c29ff0e437f3351fd82bdf47c5a3bc787dc7035`_ (details__)

.. Static key files are generated with the following command:
   ( gpg2 --fingerprint 0x80fcce3dc49bd7836fc2464664dbb05acc5e7c28
   gpg2 --armor --export-options export-clean,export-minimal \
   --export 0x80fcce3dc49bd7836fc2464664dbb05acc5e7c28 ) > \
   doc/source/static/0x80fcce3dc49bd7836fc2464664dbb05acc5e7c28.txt
.. _`key 0x80fcce3dc49bd7836fc2464664dbb05acc5e7c28`: _static/0x80fcce3dc49bd7836fc2464664dbb05acc5e7c28.txt
.. __: http://pool.sks-keyservers.net:11371/pks/lookup?op=vindex&search=0x80fcce3dc49bd7836fc2464664dbb05acc5e7c28&fingerprint=on
.. _`key 0xd47bab1b7dc2e262a4f6171e8b1b03fd54e2ac07`: _static/0xd47bab1b7dc2e262a4f6171e8b1b03fd54e2ac07.txt
.. __: http://pool.sks-keyservers.net:11371/pks/lookup?op=vindex&search=0xd47bab1b7dc2e262a4f6171e8b1b03fd54e2ac07&fingerprint=on
.. _`key 0xc96bfb160752606daa0de2fa05eb5792c876df9a`: _static/0xc96bfb160752606daa0de2fa05eb5792c876df9a.txt
.. __: http://pool.sks-keyservers.net:11371/pks/lookup?op=vindex&search=0xc96bfb160752606daa0de2fa05eb5792c876df9a&fingerprint=on
.. _`key 0x4c8b8b5a694f612544b3b4bac52f01a3fbdb9949`: _static/0x4c8b8b5a694f612544b3b4bac52f01a3fbdb9949.txt
.. __: http://pool.sks-keyservers.net:11371/pks/lookup?op=vindex&search=0x4c8b8b5a694f612544b3b4bac52f01a3fbdb9949&fingerprint=on
.. _`key 0xc31292066be772022438222c184fd3e1edf21a78`: _static/0xc31292066be772022438222c184fd3e1edf21a78.txt
.. __: http://pool.sks-keyservers.net:11371/pks/lookup?op=vindex&search=0xc31292066be772022438222c184fd3e1edf21a78&fingerprint=on
.. _`key 0x27023b1ffccd8e3ae9a5ce95d943d5d270273ada`: _static/0x27023b1ffccd8e3ae9a5ce95d943d5d270273ada.txt
.. __: http://pool.sks-keyservers.net:11371/pks/lookup?op=vindex&search=0x27023b1ffccd8e3ae9a5ce95d943d5d270273ada&fingerprint=on
.. _`key 0xcdc08088c3cb45a9be08332b2354069e5b504663`: _static/0xcdc08088c3cb45a9be08332b2354069e5b504663.txt
.. __: http://pool.sks-keyservers.net:11371/pks/lookup?op=vindex&search=0xcdc08088c3cb45a9be08332b2354069e5b504663&fingerprint=on
.. _`key 0xbba3b1e67a7303dd1769d34595bf2e4d09004514`: _static/0xbba3b1e67a7303dd1769d34595bf2e4d09004514.txt
.. __: http://pool.sks-keyservers.net:11371/pks/lookup?op=vindex&search=0xbba3b1e67a7303dd1769d34595bf2e4d09004514&fingerprint=on
.. _`key 0x2426b928085a020d8a90d0d879ab7008d0896c8a`: _static/0x2426b928085a020d8a90d0d879ab7008d0896c8a.txt
.. __: http://pool.sks-keyservers.net:11371/pks/lookup?op=vindex&search=0x2426b928085a020d8a90d0d879ab7008d0896c8a&fingerprint=on
.. _`key 0x5d2d1e4fb8d38e6af76c50d53d4fec30cf5ce3da`: _static/0x5d2d1e4fb8d38e6af76c50d53d4fec30cf5ce3da.txt
.. __: http://pool.sks-keyservers.net:11371/pks/lookup?op=vindex&search=0x5d2d1e4fb8d38e6af76c50d53d4fec30cf5ce3da&fingerprint=on
.. _`key 0x4c29ff0e437f3351fd82bdf47c5a3bc787dc7035`: _static/0x4c29ff0e437f3351fd82bdf47c5a3bc787dc7035.txt
.. __: http://pool.sks-keyservers.net:11371/pks/lookup?op=vindex&search=0x4c29ff0e437f3351fd82bdf47c5a3bc787dc7035&fingerprint=on

.. _`centrally-managed OpenPGP keys`: https://docs.openstack.org/infra/system-config/signing.html
.. _`OpenStack Infrastructure team`: https://governance.openstack.org/tc/reference/projects/infrastructure.html

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
   reference/reviewer_guide
   reference/process

.. _`openstack/releases`: https://opendev.org/openstack/releases
