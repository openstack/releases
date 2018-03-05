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

.. list-table::
   :header-rows: 1

   - * Series
     * Status
     * Initial Release Date
     * Next Phase
     * EOL Date
   - * :doc:`rocky/index`
     * :doc:`Under Development <rocky/schedule>`
     * :ref:`scheduled <r-release>`
     *
     * TBD
   - * :doc:`queens/index`
     * `Phase I -- Latest release`_
     * 2018-02-28
     * `Phase II -- Maintained release`_ on 2018-08-27
     * 2019-02-25
   - * :doc:`pike/index`
     * `Phase II -- Maintained release`_
     * 2017-08-30
     * `Phase III -- Legacy release`_ on 2018-08-27
     * 2018-09-03
   - * :doc:`ocata/index`
     * EOL
     * 2017-02-22
     *
     * 2018-02-26
   - * :doc:`newton/index`
     * EOL
     * 2016-10-06
     *
     * 2017-10-25
   - * :doc:`mitaka/index`
     * EOL
     * 2016-04-07
     *
     * 2017-04-10
   - * :doc:`liberty/index`
     * EOL
     * 2015-10-15
     *
     * 2016-11-17
   - * :doc:`kilo/index`
     * EOL
     * 2015-04-30
     *
     * 2016-05-02
   - * :doc:`juno/index`
     * EOL
     * 2014-10-16
     *
     * 2015-12-07
   - * :doc:`icehouse/index`
     * EOL
     * 2014-04-17
     *
     * 2015-07-02
   - * :doc:`havana/index`
     * EOL
     * 2013-10-17
     *
     * 2014-09-30
   - * :doc:`grizzly/index`
     * EOL
     * 2013-04-04
     *
     * 2014-03-29
   - * :doc:`folsom/index`
     * EOL
     * 2012-09-27
     *
     * 2013-11-19
   - * :doc:`essex/index`
     * EOL
     * 2012-04-05
     *
     * 2013-05-06
   - * :doc:`diablo/index`
     * EOL
     * 2011-09-22
     *
     * 2013-05-06
   - * :doc:`cactus/index`
     * Deprecated
     * 2011-04-15
     *
     *
   - * :doc:`bexar/index`
     * Deprecated
     * 2011-02-03
     *
     *
   - * :doc:`austin/index`
     * Deprecated
     * 2010-10-21
     *
     *

.. _Phase I -- Latest release: https://docs.openstack.org/project-team-guide/stable-branches.html#support-phases
.. _Phase II -- Maintained release: https://docs.openstack.org/project-team-guide/stable-branches.html#support-phases
.. _Phase III -- Legacy release: https://docs.openstack.org/project-team-guide/stable-branches.html#support-phases

.. toctree::
   :glob:
   :maxdepth: 1
   :hidden:

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

Series-Independent Releases
===========================

Some projects are released independently from the OpenStack release series.
You can find their releases listed here:

.. toctree::
   :maxdepth: 1

   independent

Teams
=====

Deliverables organized by the team that produces them.

.. toctree::
   :maxdepth: 1
   :glob:

   teams/*

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
* 2017-09-15..present (Queens Cycle key):
  `key 0x4c8b8b5a694f612544b3b4bac52f01a3fbdb9949`_ (details__)

.. Static key files are generated with the following command:
   ( gpg2 --fingerprint 0x80fcce3dc49bd7836fc2464664dbb05acc5e7c28
   gpg2 --armor --export-options export-clean,export-minimal \
   --export 0x80fcce3dc49bd7836fc2464664dbb05acc5e7c28 ) > \
   doc/source/static/0x80fcce3dc49bd7836fc2464664dbb05acc5e7c28.txt
.. _`key 0x80fcce3dc49bd7836fc2464664dbb05acc5e7c28`: _static/0x80fcce3dc49bd7836fc2464664dbb05acc5e7c28.txt
.. __: https://sks-keyservers.net/pks/lookup?op=vindex&search=0x80fcce3dc49bd7836fc2464664dbb05acc5e7c28&fingerprint=on
.. _`key 0xd47bab1b7dc2e262a4f6171e8b1b03fd54e2ac07`: _static/0xd47bab1b7dc2e262a4f6171e8b1b03fd54e2ac07.txt
.. __: https://sks-keyservers.net/pks/lookup?op=vindex&search=0xd47bab1b7dc2e262a4f6171e8b1b03fd54e2ac07&fingerprint=on
.. _`key 0xc96bfb160752606daa0de2fa05eb5792c876df9a`: _static/0xc96bfb160752606daa0de2fa05eb5792c876df9a.txt
.. __: https://sks-keyservers.net/pks/lookup?op=vindex&search=0xc96bfb160752606daa0de2fa05eb5792c876df9a&fingerprint=on
.. _`key 0x4c8b8b5a694f612544b3b4bac52f01a3fbdb9949`: _static/0x4c8b8b5a694f612544b3b4bac52f01a3fbdb9949.txt
.. __: https://sks-keyservers.net/pks/lookup?op=vindex&search=0x4c8b8b5a694f612544b3b4bac52f01a3fbdb9949&fingerprint=on

.. _`centrally-managed OpenPGP keys`: https://docs.openstack.org/infra/system-config/signing.html
.. _`OpenStack Infrastructure team`: https://governance.openstack.org/tc/reference/projects/infrastructure.html

References
==========

.. toctree::
   :maxdepth: 2
   :glob:

   reference/*
