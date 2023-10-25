.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. image:: https://img.shields.io/badge/python-3.6-blue.svg
    :alt: Python support: 3.6
.. image:: https://app.travis-ci.com/OCA/odoo-module-migrator.svg?branch=master
    :target: https://app.travis-ci.com/OCA/odoo-module-migrator

====================
odoo-module-migrator
====================

TODO documentar uso con controlador

``odoo-module-migrator`` is a python3 library that allows you to automatically migrate
module code to make it compatible with newer Odoo versions.
For example:

* renaming ``__openerp__.py`` file to ``__manifest__.py``
* removing ``# -*- encoding: utf-8 -*-`` since V11.0
* replacing ``openerp`` import with ``odoo`` import
* removing ``migrations`` folders
* changing <act_window> to <record model="ir.actions.window">
* ...

This library will:

* (optionally) get commits from the old branch (if format-patch is enabled)
* automatically apply changes (renaming, replacing, etc.)
* commit your changes
* display warnings or errors in the log if your code contains obsolete code patterns

This project is about migrating code. If you're looking for database data migration
between Odoo versions, check out the https://github.com/OCA/OpenUpgrade project.

**INFO log**

Indicates that the library automatically changed something.
*A priori* you have nothing to do. For example, for a migration from 8.0 to
a more recent version:

.. code-block:: shell

    12:38:54 INFO Renaming file: '/my_module/__openerp__.py' to '/my_module/__manifest__.py'

**WARNING log**

Indicates that you should check something. There may be something to do
to make the module work. For example:

.. code-block:: shell

    19:37:55 WARNING Replaced dependency of 'account_analytic_analysis' with 'contract' (Moved to OCA/contract)

**ERROR log**

Indicates that you must change something in your code. If not, the module
will not work *for sure* (not installable or generating errors during
execution).

For example, if you have an 8.0 module that depends on 'account_anglo_saxon',
which disappeared in more recent versions, the following log will be displayed:

.. code-block:: shell

    12:38:54 ERROR Depends on removed module 'account_anglo_saxon'

Development and Improvement
===========================

If you want to improve or contribute to this library, please read the
``DEVELOP.rst`` file and the 'Roadmap / Known Issues' sections.

Installation
============

.. code-block:: shell

    pip3 install odoo-module-migrator

Usage
=====

Using Format Patch command
--------------------------

(Recommended by the OCA)

If you want to migrate an Odoo module from version 8.0 to 12.0, for example,
the module ``pos_order_pricelist_change`` in the OCA "pos" repository:

.. code-block:: shell

    git clone https://github.com/OCA/pos -b 12.0
    cd pos
    odoo-module-migrate
        --directory             ./
        --modules               pos_order_pricelist_change
        --init-version-name     8.0
        --target-version-name   12.0
        --format-patch

Without format Patch command
----------------------------

(Mainly for your custom modules)

If you have created a new branch (for example 12.0) based on your 10.0 branch,
you can run the following command:

.. code-block:: shell

    odoo-module-migrate
        --directory             /path/to/repository
        --modules               module_1,module_2,module_3
        --init-version-name     10.0
        --target-version-name   12.0

This tool will operate the changes for each module.

Available Arguments
-------------------

+--------------------------+----------+-----------------+-------------------------------------------------------+
| Name                     | Shortcut | Options         | Description                                           |
+==========================+==========+=================+=======================================================+
|``--directory``           | ``-d``   | Default:        | Local folder that contains the module(s) to migrate.  |
|                          |          | ``./``          |                                                       |
+--------------------------+----------+-----------------+-------------------------------------------------------+
|``--init-version-name``   | ``-i``   | Required        | Initial version of your module(s) you want to migrate.|
+--------------------------+----------+-----------------+-------------------------------------------------------+
|``--target-version-name`` | ``-t``   | Default:        | Final version you want to migrate to.                 |
|                          |          | the latest Odoo |                                                       |
|                          |          | version         |                                                       |
+--------------------------+----------+-----------------+-------------------------------------------------------+
|``--modules``             | ``-m``   | Default:        | Module(s) to migrate. Note: if the format-patch option|
|                          |          | All modules     | is enabled, you have to provide only one module.      |
|                          |          | in the          |                                                       |
|                          |          | directory       |                                                       |
+--------------------------+----------+-----------------+-------------------------------------------------------+
|``--format-patch``        | ``-fp``  | Disabled        | Recover code using the git format-patch command.      |
|                          |          | by default      |                                                       |
+--------------------------+----------+-----------------+-------------------------------------------------------+
|``--remote-name``         | ``-rn``  | Default:        | Name of the main remote used by the format-patch      |
|                          |          | ``origin``      | command.                                              |
+--------------------------+----------+-----------------+-------------------------------------------------------+
|``--log-level``           | ``-ll``  | Default:        | Possible values: ``DEBUG``, ``INFO``, ``WARNING``,    |
|                          |          | ``INFO``        | etc.                                                  |
+--------------------------+----------+-----------------+-------------------------------------------------------+
|``--log-path``            | ``-lp``  | Default:        | If set, logs will not be displayed on screen,         |
|                          |          | False           | but stored in a file.                                 |
+--------------------------+----------+-----------------+-------------------------------------------------------+
|``--no-commit``           | ``-nc``  | Default:        | If set, the library will not git add and git commit   |
|                          |          | commit          | changes.                                              |
+--------------------------+----------+-----------------+-------------------------------------------------------+

Roadmap / Known Issues
======================

* The replacement of the tag <openerp><data> with <odoo> will fail in cases
  where there are many <data> occurrences.
  We could fix that by using the ``lxml`` library instead of regular expressions.

* Add a call to ``pre-commit run -a``, if pre-commit is present in the
  repository.

Changes
=======

0.3.2 (December 04, 2019)
-------------------------
* [REM] Remove black call (add call to a more generic tool pre-commit
  in the roadmap).
* [IMP] Add --no-verify option in ``git commit`` to avoid failure if pre-commit
  is present.
* [REF] Refactor ``_execute_shell`` function.

0.2.0 (October 13, 2019)
------------------------
* Second release.

0.1.4 (October 12, 2019)
------------------------
* Test

[ADD] test.

* Framework

[ADD] ``--file-path`` option.
[ADD] ``_DEPRECATED_MODULES`` syntax.

* Migration script

[FIX] Incorrect syntax of regular expression to remove python 2 header.
[IMP] First release of all the steps from 8.0 to 13.0.

0.1.3 (October 11, 2019)
------------------------

* Framework

[ADD] ``--no-commit`` option that disables git add and git commit calls.
[FIX] Do not commit many times if migration has many steps.
[REF] Remove useless commented code.
[REF] Create ``_commit_changes()`` and ``_replace_in_file()`` functions.

* Meta

[FIX] GitHub URL of the project in setup.py.
[ADD] Travis file + links to coveralls.
[ADD] test_requirements.txt.

* Migration script

[ADD] Migration from 12.0 to 13.0 and add a warning if references to web_settings_dashboard are found, courtesy of @yelizariev.
[ADD] Bump version in manifest file.
[ADD] Set installable to True.

0.1.2 (October 10, 2019)
------------------------

* First release.

Credits
=======

Authors
-------

* GRAP, Groupement Régional Alimentaire de Proximité (http://www.grap.coop)

Contributors
------------

* Sylvain LE GAL (https://www.twitter.com/legalsylvain)
