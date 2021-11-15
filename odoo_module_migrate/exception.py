# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


class OdooMigrateException(Exception):
    pass


class ConfigException(OdooMigrateException):
    pass


class CommandException(OdooMigrateException):
    pass
