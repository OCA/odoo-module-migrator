.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. image:: https://img.shields.io/badge/python-3.6-blue.svg
    :alt: Python support: 3.6

============
odoo-migrate
============

Installation
============

.. code-block:: shell

    # Install Stable Source
    pip3 install odoo-migrate

    # Or, Install Test source
    pip3 install odoo-migrate\
        --upgrade\
        --index-url https://test.pypi.org/simple\
        --extra-index-url https://pypi.org/simple

Usage
=====

Migrate Tools
-------------

This library allow to realize automatically recurring changes when migrating
Odoo modules from a version to another.

For that purpose, once installed

.. code-block:: shell

    odoo-migrate --directory module_folder --init-version 8.0 --target-version 12.0

Settings
========

The list of the operations are written:

* in a file for each migration for exemple ``migrate_10_0__11_0.py`` file
  contains all the operations to do for a migration from 10.0 to 11.0.

* in a file for operations that should be execute since some revision, named
  for exemple ``migrate_10_0__all.py``

* a file ``migrate_allways.py`` contains all the operations that will be
  executed, whatever the init and the target versions.

List of the operations
----------------------

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

Developement
============

Installation
------------

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

Package deployment
------------------

.. code-block:: shell

    pip3 install --upgrade setuptools wheel
    pip3 install  --upgrade twine

    # Generate wheel and package
    python3 setup.py sdist bdist_wheel

    # Push on pyPi Test
    twine upload --repository-url https://test.pypi.org/legacy/ dist/*

    # Push on pyPi Production
    twine upload dist/*

Roadmap / Know issues
=====================

* Add tests.

* option ``init_version`` : add 'auto' as a possible option, to let library
  guess the current version of the module.

Credits
=======

Authors
-------

* GRAP, Groupement Régional Alimentaire de Proximité (http://www.grap.coop)

Contributors
------------

* Sylvain LE GAL (https://www.twitter.com/legalsylvain)
