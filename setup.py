# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import setuptools

setuptools.setup(
    name="odoo-migrate",
    version="0.0.6",
    author="GRAP, Groupement Régional Alimentaire de Proximité",
    author_email="informatique@grap.coop",
    description="Small tools too migrate Odoo modules",
    long_description=open('README.rst').read(),
    long_description_content_type='text/x-rst',
    url="https://www.grap.coop",
    packages=['odoo_migrate'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
    ],
    install_requires=open('requirements.txt').read().splitlines(),
    entry_points=dict(
        console_scripts=['odoo-migrate=odoo_migrate.__main__:main']),
)
