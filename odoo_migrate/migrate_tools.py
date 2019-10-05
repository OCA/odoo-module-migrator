import os
import subprocess
import importlib
import re

_ALLOWED_EXTENSIONS = [".py", ".xml", ".js"]


def _migrate_module(logger, root_path, module_path, migration_list):
    logger.info("Migration of module '%s'" % (module_path))

    for migration in migration_list:
        # Execute specific migration for a version to another
        # Exemple 8.0 -> 9.0
        script_module = importlib.import_module(
            "odoo_migrate.migrate_%s__%s"
            % (
                migration[0].replace(".", "_"),
                (migration[1].replace(".", "_")),
            )
        )
        _migrate_module_script(logger, root_path, module_path, script_module)

        # Execute migration that have to be done for all version after
        # a given revision
        # Exemple remove python3 header if version >= to 11.0
        script_module = importlib.import_module(
            "odoo_migrate.migrate_%s__all" % (migration[0].replace(".", "_"))
        )
        _migrate_module_script(logger, root_path, module_path, script_module)

    # Finally, execute a script that will be allways executed
    script_module = importlib.import_module("odoo_migrate.migrate_allways")
    _migrate_module_script(logger, root_path, module_path, script_module)


def _migrate_module_script(logger, root_path, module_path, script_module):
    logger.debug("Executing script '%s'" % (script_module.__name__))

    file_renames = getattr(script_module, "_FILE_RENAMES", {})
    text_replaces = getattr(script_module, "_TEXT_REPLACES", {})
    text_warnings = getattr(script_module, "_TEXT_WARNING", {})

    for root, directories, filenames in os.walk(module_path._str):
        for filename in filenames:
            # Skip useless file
            # TODO, skip files present in some folders. (for exemple 'lib')
            extension = os.path.splitext(filename)[1]
            if extension not in _ALLOWED_EXTENSIONS:
                continue

            filenameWithPath = os.path.join(root, filename)
            logger.debug("Migrate '%s' file" % filenameWithPath)

            # Rename file, if required
            new_name = file_renames.get(filename)
            if new_name:
                _rename_file(
                    logger, module_path, filenameWithPath,
                    os.path.join(root, new_name))
                filenameWithPath = os.path.join(root, new_name)

            with open(filenameWithPath, "U") as f:
                # Operate changes in the file (replacements, removals)
                currentText = f.read()
                newText = currentText

                replaces = text_replaces.get("*", {})
                replaces.update(text_replaces.get(extension, {}))

                for old_term, new_term in replaces.items():
                    newText = re.sub(old_term, new_term, newText)

                # Write file if changed
                if newText != currentText:
                    logger.info("Changing content of file: %s" % filename)
                    with open(filenameWithPath, "w") as f:
                        f.write(newText)

                # Display warnings if the file content some obsolete code
                warnings = text_warnings.get("*", {})
                warnings.update(text_warnings.get(extension, {}))
                for pattern, warning_message in warnings.items():
                    if re.findall(pattern, newText):
                        logger.warning(warning_message)


def _rename_file(logger, module_path, old_file_path, new_file_path):
    """Rename a file. try to execute 'git mv', to avoid huge diff.
    if 'git mv' fails, make a classical rename"""
    logger.info(
        "renaming file: %s. New name: %s " % (old_file_path, new_file_path)
    )

    # try:
    subprocess.check_output(
        "cd %s && git mv %s %s" % (
            module_path._str, old_file_path, new_file_path
        ), shell=True)
    # except:
    # os.rename(old_file_path, new_file_path)


def _get_code_from_previous_branch(
        logger, root_path, module_name, init_version, target_version,
        remote_name):

    logger.info("Try to format-patch code from the initial branch %s" % (
        module_name))
    _execute_shell(logger, "cd %s git fetch %s" % (root_path, remote_name))

    subprocess.check_output(
        "cd %s && git format-patch --keep-subject --stdout"
        " %s/%s..%s/%s"
        " -- %s | git am -3 --keep" % (
            root_path,
            remote_name, target_version, remote_name, init_version,
            module_name))


def _execute_shell(logger, shell):
    logger.debug("Execute: '%s" % (shell))
    return subprocess.check_output(shell)
