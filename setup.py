# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import setuptools

setuptools.setup(
    name="odoo-module-migrator",
    version="0.5.0",
    author="GRAP, Groupement Régional Alimentaire de Proximité",
    author_email="informatique@grap.coop",
    description="Small tools to migrate Odoo modules from a version" " to another",
    long_description=open("README.rst").read(),
    long_description_content_type="text/x-rst",
    url="https://github.com/OCA/odoo-module-migrator",
    packages=["odoo_module_migrate", "odoo_module_migrate.migration_scripts"],
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Odoo",
        "Topic :: Software Development :: Code Generators",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Environment :: Console",
    ],
    install_requires=open("requirements.txt").read().splitlines(),
    entry_points=dict(
        console_scripts=[
            "odoo-module-migrate=odoo_module_migrate.__main__:main",
        ]
    ),
    keywords=[
        "Odoo Community Association (OCA)",
        "Odoo",
        "Migration",
        "Upgrade",
        "Module",
    ],
)
