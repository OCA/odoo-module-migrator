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

This library allows to realize automatically recurring changes when migrating
Odoo modules from a version to another.

For that purpose, once installed

.. code-block:: shell

    odoo-migrate --directory module_folder --init-version 8.0 --target-version 12.0


Roadmap / Know issues
=====================

* Add tests.

Credits
=======

Authors
-------

* GRAP, Groupement Régional Alimentaire de Proximité (http://www.grap.coop)

Contributors
------------

* Sylvain LE GAL (https://www.twitter.com/legalsylvain)
