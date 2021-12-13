.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. image:: https://img.shields.io/badge/python-3.6-blue.svg
    :alt: Python support: 3.6
.. image:: https://travis-ci.org/grap/odoo-module-migrator.svg?branch=master
    :target: https://travis-ci.org/grap/odoo-module-migrator
.. image:: https://coveralls.io/repos/grap/odoo-module-migrator/badge.png?branch=master
    :target: https://coveralls.io/r/grap/odoo-module-migrator?branch=master

====================
odoo-module-migrator
====================

``odoo-module-migrator`` is a python3 library that allows you to automatically migrate 
module code to make it compatible with newer Odoo version.
for exemple: 

* renaming ``__openerp__.py`` file into ``__manifest__.py``
* removing ``# -*- encoding: utf-8 -*-`` since V11.0
* replacing ``openerp`` import by ``odoo`` import
* removing ``migrations`` folders
* changing <act_window> to <record model="ir.actions.window">
* ...

This library will so:

* (optionnaly) get commits from the old branch (if format-patch is enabled)
* apply automatically changes. (renaming, replacing, etc.)
* commit your changes.
* Display warnings or errors in log if your code belong obsolete code patterns.

This project is about migrating code. If you're looking for database data migration
between Odoo versions, take a look
at the https://github.com/OCA/OpenUpgrade project.

**INFO log**

It mentions that the lib automatically changed something.
*A priori* you have nothing to do. For example, for a migration from 8.0 to
a more recent version:

.. code-block:: shell

    12:38:54 INFO Renaming file: '/my_module/__openerp__.py' by '/my_module/__manifest__.py'

**WARNING log**

It mentions that you should check something. There is *maybe* something to do
to make the module working. For exemple:

.. code-block:: shell

    19:37:55 WARNING Replaced dependency of 'account_analytic_analysis' by 'contract' (Moved to OCA/contract)


**ERROR log**

It mentions that you should change something in your code. It not, the module
will not work *for sure*. (not installable, or generating error during the
execution)

For example, if you have a 8.0 module that depends on 'account_anglo_saxon',
that disappeared in more recent version, the following log will be displayed

.. code-block:: shell

    12:38:54 ERROR Depends on removed module 'account_anglo_saxon'

Development and improvment
==========================

If you want to improve or complete this library, please read the
``DEVELOP.rst`` file and the 'Roadmap / Know issues' sections.

Installation
============

.. code-block:: shell

    pip3 install odoo-module-migrator


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
    odoo-module-migrate
        --directory             ./
        --modules               pos_order_pricelist_change
        --init-version-name     8.0
        --target-version-name  12.0
        --format-patch

Without format Patch command
----------------------------

(Mainly for your custom modules)

if you have created a new branch (for exemple 12.0) based on your 10.0 branch
you can run the following command

.. code-block:: shell

    odoo-module-migrate
        --directory             /path/to/repository
        --modules               module_1,module_2,module_3
        --init-version-name     10.0
        --target-version-name   12.0

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
|``--log-level``           | ``-ll``  | Default:        | Possible value: ``DEBUG``, ``INFO``, ``WARNING``, etc.|
|                          |          | ``INFO``        |                                                       |
+--------------------------+----------+-----------------+-------------------------------------------------------+
|``--log-path``            | ``-lp``  | Default:        | If set, the logs will not be displayed at screen,     |
|                          |          | False           | but stored in a file                                  |
+--------------------------+----------+-----------------+-------------------------------------------------------+
|``--no-commit``           | ``-nc``  | Default:        | If set the library will not git add and git commit    |
|                          |          | commit          | changes.                                              |
+--------------------------+----------+-----------------+-------------------------------------------------------+


Roadmap / Know issues
=====================

* replacement of tag <openerp><data> by <odoo> will fail in the case
  where there are many <data> occurency.
  We could fix that, using ``lxml`` lib instead of regular expression.

* Add a call to ``pre-commit run -a``, if pre-commit is present in the
  repository.

Changes
=======

0.3.2 (December 04, 2019)
------------------------
* [REM] Remove black call. (Add call to more generic tool pre-commit
  in the roadmap)
* [IMP] Add --no-verify option in ``git commit`` to avoid to fail if pre-commit
  is present
* [REF] Refactor ``_execute_shell`` function


0.2.0 (October 13, 2019)
------------------------
* Second release


0.1.4 (October 12, 2019)
------------------------
* Test

[ADD] test

* framework

[ADD] ``--file-path`` option.
[ADD] ``_DEPRECATED_MODULES`` syntax.

* migration script

[FIX] Incorrect syntax of regular expression, to remove python 2 header
[IMP] first release of all the steps from 8.0 to 13.0


0.1.3 (October 11, 2019)
------------------------

* framework

[ADD] ``--no-commit`` option that disable git add and git commit calls
[FIX] do not commit many times if migration has many steps.
[REF] remove useless commented code
[REF] create _commit_changes() and _replace_in_file() functions

* Meta

[FIX] github url of the project in setup.py
[ADD] Travis file + links to coveralls
[ADD] test_requirements.txt

* migration script

[ADD] 12.0 to 13.0 and add a warning if reference to web_settings_dashboard are found. cortesy @yelizariev
[ADD] bump version in manifest file
[ADD] set installable to True


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

