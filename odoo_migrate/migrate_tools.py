import os
import subprocess


def _rename_file(logger, module_path, old_file_path, new_file_path):
    """Rename a file. if the git repository is provided, the rename will not
    be done normaly, but by a 'git mv' command"""
    logger.info(
        "renaming file: %s. New name: %s " % (old_file_path, new_file_path)
    )

    try:
        subprocess.check_output(
            "cd %s && git mv %s %s" % (
                module_path._str, old_file_path, new_file_path
            ), shell=True)
    except:
        os.rename(old_file_path, new_file_path)
