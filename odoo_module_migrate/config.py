# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

# List of migrations steps handled by this library
# * init and target name are friendly name used by the user, when calling
#   the lib.
# * init and target code are technical code used to name the migration script
#   files.

_AVAILABLE_MIGRATION_STEPS = [
    {
        "init_version_name": "8.0",
        "target_version_name": "9.0",
        "init_version_code": "080",
        "target_version_code": "090",
    }, {
        "init_version_name": "9.0",
        "target_version_name": "10.0",
        "init_version_code": "090",
        "target_version_code": "100",
    }, {
        "init_version_name": "10.0",
        "target_version_name": "11.0",
        "init_version_code": "100",
        "target_version_code": "110",
    }, {
        "init_version_name": "11.0",
        "target_version_name": "12.0",
        "init_version_code": "110",
        "target_version_code": "120",
    }, {
        "init_version_name": "12.0",
        "target_version_name": "13.0",
        "init_version_code": "120",
        "target_version_code": "130",
    }, {
        "init_version_name": "13.0",
        "target_version_name": "14.0",
        "init_version_code": "130",
        "target_version_code": "140",
    },
]

_ALLOWED_EXTENSIONS = [".py", ".xml", ".js"]

_MANIFEST_NAMES = ["__openerp__.py", "__manifest__.py"]
