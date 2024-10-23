# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Module name",
    "version": "17.0.1.0.0",
    "installable": False,
    'license': 'AGPL-3',
    'depends': [
        'base',
    ],
    'data': [
        'views/res_partner.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'module_170/static/src/js/main.js',
        ],
    },
}
