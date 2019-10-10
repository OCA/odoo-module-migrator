.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. image:: https://img.shields.io/badge/python-3.6-blue.svg
    :alt: Python support: 3.6

============
odoo-migrate
============

``odoo-migrate`` is a python3 library that allows you to realize automatically
recurring changes when migrating Odoo modules from a version to another.
for exemple, renaming ``__openerp__.py`` file into ``__manifest__.py``.

This library will so:

* (optionnaly) get commit from the old branch (if format-patch is enabled)
* apply automatically changes. (renaming, replacing, etc.)
* (depending of the config and the version) black your code.
* commit your changes.
* Display warnings if your code belong obsolete code patterns.

Development and improvment
==========================

If you want to improve or complete this library, please read the
``DEVELOP.rst`` file and the 'Roadmap / Know issues' sections.

Installation
============

.. code-block:: shell

    # Install Stable Source
    pip3 install odoo-migrate


Usage
=====

**using Format Patch command**

(Recommanded by the OCA)

If you want to migrate an Odoo module from a version 8.0 to 12.0, for exemple
the module ``pos_order_pricelist_change`` in the OCA "pos" repository.

.. code-block:: shell

    git clone https://github.com/OCA/pos -b 12.0
    cd pos
    odoo-migrate
        --directory             ./
        --modules               pos_order_pricelist_change
        --init-version-name     8.0
        -- target-version-name 12.0
        --format-patch

**Without format Patch command**

(Mainly for your custom modules)

if you have created a new branch (for exemple 12.0) based on your 10.0 branch
you can run the following command

.. code-block:: shell

    odoo-migrate
        --directory             /path/to/repository
        --modules               module_1,module_2,module_3
        --init-version-name     10.0
        -- target-version-name  12.0

This tools will operate the changes for each module.

**Options**

    * ``--directory`` (-d):
        local folder that belongs the module(s) to migrate.
        Default: ``./``

    * ``--init-version-name`` (-i): REQUIRED
        Initial version of your module(s) you want to migrate.

    * ``--target-version-name`` (-i):
        Final Version you want to migrate.
        Default: the last odoo version available.

    * ``--modules`` (-m):
        module(s) to migrate.
        Default: All modules present in the directory.
        Note if format-patch option is enabled, you have to provide only
        one module.

    * ``--format-patch`` (-fp):
        Recover code, using git format-patch command.

    * ``--remote-name`` -(-rn):
        Name of the main remote, used by format-patch command.
        Default: ``origin``

    * ``--force-black`` (-fb) :
        Force to use black library. Note that this option is enabled by
        default, if migrating to 13.0 or further version.

    * ``--log-level`` (-ll):
        Possible value: ``DEBUG``, ``INFO``, ``WARNING``, etc.
        Default: ``INFO``


Roadmap / Know issues
=====================

* Complete migration scripts.

* Add tests.

* finish to implement black.

Credits
=======

Authors
-------

* GRAP, Groupement Régional Alimentaire de Proximité (http://www.grap.coop)

Contributors
------------

* Sylvain LE GAL (https://www.twitter.com/legalsylvain)
