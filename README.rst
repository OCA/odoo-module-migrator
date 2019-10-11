.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
.. image:: https://img.shields.io/badge/python-3.6-blue.svg
.. image:: https://travis-ci.org/grap/odoo-migrate.svg?branch=master
    :target: https://travis-ci.org/grap/odoo-migrate
.. image:: https://coveralls.io/repos/grap/odoo-migrate/badge.png?branch=master
    :target: https://coveralls.io/r/grap/odoo-migrate?branch=master

============
odoo-migrate
============

``odoo-migrate`` is a python3 library that allows you to realize automatically
recurring changes when migrating Odoo modules from a version to another.
for exemple: 

* renaming ``__openerp__.py`` file into ``__manifest__.py``
* removing ``# -*- encoding: utf-8 -*-`` since V11.0
* replacing ``openerp`` import by ``odoo`` import
* removing ``migrations`` folders
* ...

This library will so:

* (optionnaly) get commits from the old branch (if format-patch is enabled)
* apply automatically changes. (renaming, replacing, etc.)
* (depending of the config and the version) black your code.
* commit your changes.
* Display warnings if your code belong obsolete code patterns. For exemple,
  for a migration to V11+


.. code-block:: shell

    15:59:04   WARNING     'ir.values' found. This model has been removed in V11.


Development and improvment
==========================

If you want to improve or complete this library, please read the
``DEVELOP.rst`` file and the 'Roadmap / Know issues' sections.

Installation
============

.. code-block:: shell

    pip3 install odoo-migrate


Usage
=====

Using Format Patch command
--------------------------

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

Without format Patch command
----------------------------

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

Available arguments
-------------------

+--------------------------+----------+-----------------+-------------------------------------------------------+
|name                      | shortcut | Options         | description                                           |
+==========================+==========+=================+=======================================================+
|``--directory``           |``-d``    | Default:        | Local folder that belongs the module(s) to migrate.   |
|                          |          | ``./``          |                                                       |
+--------------------------+----------+-----------------+-------------------------------------------------------+
|``--init-version-name``   | ``-i``   | Required        | Initial version of your module(s) you want to migrate.|
|                          |          |                 |                                                       |
+--------------------------+----------+-----------------+-------------------------------------------------------+
|``--target-version-name`` | ``-t``   | Default:        | Final Version you want to migrate.                    |
|                          |          | the laster odoo |                                                       |
|                          |          | version         |                                                       |
+--------------------------+----------+-----------------+-------------------------------------------------------+
|``--modules``             | ``-m``   | Default:        | Module(s) to migrate. Note if format-patch option is  |
|                          |          | All modules     | enabled, you have to provide only one module.         |
|                          |          | present in the  |                                                       |
|                          |          | directory       |                                                       |
+--------------------------+----------+-----------------+-------------------------------------------------------+
|``--format-patch``        | ``-fp``  | disabled        | Recover code, using git format-patch command.         |
|                          |          | by default      |                                                       |
+--------------------------+----------+-----------------+-------------------------------------------------------+
|``--remote-name``         | ``-rn``  | Default:        | Name of the main remote, used by format-patch command.|
|                          |          | ``origin``      |                                                       |
+--------------------------+----------+-----------------+-------------------------------------------------------+
|``--force-black``         | ``-fb``  | depends on the  | Force to use black library.                           |
|                          |          | configuration   |                                                       |
+--------------------------+----------+-----------------+-------------------------------------------------------+
|``--log-level``           | ``-ll``  | Default:        | Possible value: ``DEBUG``, ``INFO``, ``WARNING``, etc.|
|                          |          | ``INFO``        |                                                       |
+--------------------------+----------+-----------------+-------------------------------------------------------+
|``--no-commit``           | ``-nc``  | Default:        | If set the library will not git add and git commit    |
|                          |          | commit          | changes.                                              |
+--------------------------+----------+-----------------+-------------------------------------------------------+


Roadmap / Know issues
=====================

* Complete migration scripts.

* Add tests.

Changes
=======

0.1.2 (October 10, 2019)
------------------------

* First release

Credits
=======

Authors
-------

* GRAP, Groupement Régional Alimentaire de Proximité (http://www.grap.coop)

Contributors
------------

* Sylvain LE GAL (https://www.twitter.com/legalsylvain)

