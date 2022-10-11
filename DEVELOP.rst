Installation
============

.. code-block:: shell

    # Pull Code
    git clone https://github.com/grap/odoo-module-migrator
    cd odoo-module-migrator

    # Create virtual env and activate it
    virtualenv env --python=python3
    . ./env/bin/activate

    # Install dependencies
    pip3 install -r requirements.txt

    # Run the script
    python -m odoo_module_migrate COMMAND OPTIONS

You can also install from test source via pip:

.. code-block:: shell

    pip3 install odoo-module-migrator\
        --upgrade\
        --index-url https://test.pypi.org/simple\
        --extra-index-url https://pypi.org/simple

Run tests
=========

.. code-block:: shell

    # Activate virtual env
    . ./env/bin/activate

    # Install extra dependencies required for tests
    pip3 install -r test_requirements.txt

    # Run Tests
    coverage run --source odoo_module_migrate setup.py test

Structure of the Project
========================

Framework
---------

In the ``odoo_module_migrate`` folder

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
`<odoo_module_migrate/migration_scripts/>`__:

* each operaion has specification when it has to be applied: ``FROM_TO`` part of the path.

  * `Possible values are <odoo_module_migrate/config.py>`__ ``090``, ``010``, ``011``, etc.
  * The ``TO`` part may have value ``always``, which means is should be applied in every version since ``FROM`` version.
  * Special value for ``FROM_TO`` is just a single ``allways`` (yes, it's mispealing) which means it will be applied whatever the init and target odoo version.

* ``migrate_FROM_TO.py`` — old way to specify operations. Normally, these files should not be changed.

* ``file_renames/migrate_FROM_TO/NAME.yaml`` — file renaming rules. For
  example, for migration from version 8.0 to more recent version:

  .. code-block:: yaml

      __openerp__.py: __manifest__.py

* ``text_replaces/migrate_FROM_TO/NAME.yaml`` — replace pattern text by
  another. for example, for migration from version 8.0 to version 9.0:

  .. code-block:: yaml

      .py:
          select=True: index=True


* ``text_errors/migrate_FROM_TO/NAME.yaml`` — display errors if files contains a
  given partern. For example, for migration from version 10.0 to version 11.0:

  .. code-block:: yaml

      "*":
          ir.values: "ir.values table does not exist anymore"

* ``text_warnings/migrate_FROM_TO/NAME.yaml`` — display errors if files contains a
  given partern. For example, for migration from version 12.0 to version 13.0:

  .. code-block:: yaml

      "*":
          "@api.returns": "decorator @api.returns is deprecated"

* ``deprecated_modules/migrate_FROM_TO/NAME.yaml`` — dependencies to obsoletes modules. There are following possibilities:

  * the module has been fully removed.
  * the module has been renamed.
  * the module features has been merged into another module.
  * the module has been moved under OCA umbrella. (w/o another name)

  .. code-block:: yaml

        - ["account_anglo_saxon", "removed"]
        - ["account_check_writing", "renamed", "account_check_printing"]
        - ["account_chart", "merged", "account"]
        - ["account_analytic_analysis", "oca_moved", "contract", "Moved to OCA/contract"]

* ``python_scripts/migrate_FROM_TO/NAME.py`` — for complex updates/checks. Must contain one or few functions that don't start with underscore symbol. The functions take following keyword arguments:

  * ``logger``
  * ``module_path``
  * ``module_name``
  * ``manifest_path``
  * ``migration_steps`` — list of steps. See ``_AVAILABLE_MIGRATION_STEPS`` in `<odoo_module_migrate/config.py>`__
  * ``tools`` — python module with some functions. See `<odoo_module_migrate/tools.py>`__

  .. code-block:: py

      def set_module_installable(**kwargs):
          tools = kwargs['tools']
          manifest_path = kwargs['manifest_path']
          old_term = r"('|\")installable('|\").*(False)"
          new_term = r"\1installable\2: True"
          tools._replace_in_file(
              manifest_path, {old_term: new_term}, "Set module installable")

* ``removed_fields/migrate_FROM_TO/NAME.yaml`` — removed fields rule. Give warnings if field name is found on the code.
    To minimize two many false positives we search for field name on this situations:
         * with simple/double quotes
         * prefixed with dot and with space, comma or equal after the string

 For example, for migration from version 15.0 to 16.0:
  .. code-block:: yaml
    - ['product.product', 'price', 'Commit https://github.com/odoo/odoo/commit/9e99a9df464d97a74ca320d']

* ``renamed_fields/migrate_FROM_TO/NAME.yaml`` — renamed fields rule. Give warnings if old field name is found on the code.
    To minimize two many false positives we search for field name on this situations:
         * with simple/double quotes
         * prefixed with dot and with space, comma or equal after the string

 For example, for migration from version 15.0 to 16.0:
  .. code-block:: yaml
    - ['account.account', 'user_type_id', 'account_type', 'Commit https://github.com/odoo/odoo/commit/26b2472f4977ccedbb0b5ed5f']

* ``removed_models/migrate_FROM_TO/NAME.yaml`` — removed models rule. Display errors / warnings if files contains a given partern:
     * errors: "old_model_name", 'old_model_name', old_table_name["',]
     * warnings: old.model.name, old_model_name

 For example, for migration from version 15.0 to 16.0:
  .. code-block:: yaml
    - ["account.account.type", "Commit https://github.com/odoo/odoo/commit/26b2472f4977ccedbb0b5ed5f"]

* ``renamed_models/migrate_FROM_TO/NAME.yaml`` — renamed models rule. Display errors / warnings if files contains a given partern:
     * errors: "old_model_name", 'old_model_name', old_table_name["',]
     * warnings: old.model.name, old_model_name

 For example, for migration from version 15.0 to 16.0:
  .. code-block:: yaml
    - ["stock.production.lot", "stock.lot", None]

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
