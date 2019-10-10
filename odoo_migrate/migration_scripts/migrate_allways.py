# Bump Module version
# Switch the installable key to True
import os
import subprocess


def remove_migration_folder(**kwargs):
    logger = kwargs['logger']
    module_path = kwargs['module_path']
    module_name = kwargs['module_name']
    migration_path_folder = os.path.join(module_path, 'migrations')
    if os.path.exists(migration_path_folder):
        logger.info("Removing 'migrations' folder in module %s" % (
            module_name))
        subprocess.check_output("rm -r %s" % migration_path_folder, shell=True)

_GLOBAL_FUNCTIONS = [remove_migration_folder]
