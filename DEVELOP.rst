Installation
============

.. code-block:: shell

    # Pull Code
    git clone https://github.com/grap/odoo-migrate
    cd odoo-migrate

    # Create virtual env and activate it
    virtualenv env --python=python3
    . ./env/bin/activate

    # Install dependencies
    pip3 install -r requirements.txt

    # Run the script
    python -m odoo_migrate COMMAND OPTIONS

You can also install from test source via pip:

.. code-block:: shell

    pip3 install odoo-migrate\
        --upgrade\
        --index-url https://test.pypi.org/simple\
        --extra-index-url https://pypi.org/simple

Run tests
=========

TODO

Structure of the Project
========================

Framework
---------

In the ``odoo_migrate`` folder

* ``__main__.py``: the entry point of this module. It mainly
  handles arguments, and launch the script.

* ``config.py``: configuration file, to updated if new features are available
  in this library. (For exemple, a new migration available from X to X+1)

* ``log.py``: Handle logs of this library.

* ``tools.py``: bundle of generic functions used by the framework.

* ``migration.py``: Define the class ``Migration`` that handle a migration
  from a version X.0 to a version Y.0 for any module.

* ``module_migration.py``: Define the class ``ModuleMigration`` that handle
  a migration for a given module.


Migration Scripts
-----------------

The list of the operations are written in the subfolder
``odoo_migrate/migration_scripts``:

* in a file for each migration for exemple ``migrate_090__100.py`` file
  contains all the operations to do for a migration from 9.0 to 10.0.

* in a file for operations that should be execute since some revision, named
  for exemple ``migrate_10_0__allways.py``

* a file ``migrate_allways.py`` contains all the operations that will be
  executed, whatever the init and the target versions.

**List of the operations**

* Rename files. For exemple, for migration from version 8.0 to more recent
  version

.. code-block:: python

    _FILE_RENAMES = {
        "__openerp__.py": "__manifest__.py",
    }

* Replace pattern text by another. for exemple, for migration from version 8.0
  to version 9.0:

.. code-block:: python

   _TEXT_REPLACES = {
        ".py": {
            "select=True": "index=True",
        }
    }

* Display warnings if files contains a given partern. For exemple, for
  migration from version 10.0 to version 11.0:

.. code-block:: python

    _TEXT_WARNING = {
        "*": {
            "ir.values": "ir.values table does not exist anymore"
        }
    }

How to improve the library
==========================

* Read (or complete !) the migration advices of the OCA.
  https://github.com/OCA/maintainer-tools/wiki#migration

* Read the complementary pages
  https://odoo-development.readthedocs.io/en/latest/migration/

* Discover what changed between two revisions, reading OpenUpgrade
  documentation, specially the modules changes, for exemple:
  https://github.com/OCA/OpenUpgrade/blob/12.0/odoo/openupgrade/doc/source/modules110-120.rst

* Create or complete the according migration file.

* Add tests.

* Make a Pull request.

Package deployment
==================

.. code-block:: shell

    pip3 install --upgrade setuptools wheel
    pip3 install  --upgrade twine

    # Generate wheel and package
    python3 setup.py sdist bdist_wheel

    # Push on pyPi Test
    twine upload --repository-url https://test.pypi.org/legacy/ dist/*

    # Push on pyPi Production
    twine upload dist/*
