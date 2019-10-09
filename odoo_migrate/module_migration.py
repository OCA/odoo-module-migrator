from .log import logger


class ModuleMigration():

    _migration = False
    _module_name = False

    def __init__(self, migration, module_name):
        self._migration = migration
        self._module_name = module_name

    def run(self):
        logger.info("Running migration of module %s" % self._module_name)
