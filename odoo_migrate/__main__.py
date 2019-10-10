# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import argparse
import argcomplete
# from pathlib import Path
# from . import migrate_tools
from . import tools
from .log import setup_logger
from .migration import Migration


def get_parser():

    main_parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter
    )

    main_parser.add_argument(
        "-d",
        "--directory",
        dest="directory",
        default="./",
        type=str,
        help="Target Modules directory. Set here a folder path"
        " that contains Odoo modules you want to migrate from a version"
        " to another.",
    )

    main_parser.add_argument(
        "-m",
        "--modules",
        dest="modules",
        type=str,
        help="Targer Modules to migrate."
        " If not set, all the modules present in the directory will be"
        " migrated.",
    )

    main_parser.add_argument(
        "-i",
        "--init-version-name",
        choices=tools._get_available_init_version_names(),
        dest="init_version_name",
        required=True,
        type=str,
    )

    main_parser.add_argument(
        "-t",
        "--target-version-name",
        dest="target_version_name",
        type=str,
        choices=tools._get_available_target_version_names(),
        default=tools._get_latest_version_name(),
        help="Target version of the Odoo module you want to migrate."
        " If 'latest' is set, the tool will try to migrate to the latest"
        " Odoo version.",
    )

    main_parser.add_argument(
        "-fp",
        "--format-patch",
        action='store_true',
        help="Enable this option, if you want to get the code from the"
        " previous branch."
    )

    main_parser.add_argument(
        "-fb",
        "--force-black",
        action='store_true',
        default=True,
        help="Enable this option, if you want to use 'black' to clean the code"
    )

    main_parser.add_argument(
        "-rn",
        "--remote-name",
        dest="remote_name",
        default='origin',
        type=str,
    )

    main_parser.add_argument(
        "-ll",
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        dest="log_level",
        default="DEBUG",
        type=str,
    )

    return main_parser


def main():
    # Parse Arguments
    parser = get_parser()
    argcomplete.autocomplete(parser, always_complete_options=False)
    args = parser.parse_args()

    # Set log level
    setup_logger(args.log_level)

    try:
        # Create a new Migration Object
        module_names = args.modules\
            and [x.strip() for x in args.modules.split(",") if x.strip()] or []

        migration = Migration(
            args.directory, args.init_version_name, args.target_version_name,
            module_names, args.format_patch, args.remote_name, args.force_black
        )

        # run Migration
        migration.run()

        # # Get Main path and test if exists
        # root_path = Path(args.directory)
        # if not root_path.exists():
        #     raise ValueError("'%s' is not a valid path." % (args.directory))

        # # Recover modules list
        # modules_path = []
        # modules_list = args.modules\
        #     and [x for x in args.modules.split(",") if x] or []

        # if not args.modules:
        #     # Recover all submodules, if no modules list is provided
        #     subfolders = [x for x in root_path.iterdir() if x.is_dir()]
        # else:
        #     subfolders = [root_path / x for x in modules_list]

        # # Recover code for former version, if asked
        # if args.format_patch:
        #     if len(modules_list) != 1:
        #         raise ValueError(
        #             "If 'format-patch' option is enabled, you should provide"
        #             " a unique module name in the 'modules' argument.")
        #     migrate_tools._get_code_from_previous_branch(
        #         _logger, root_path, modules_list[0], args.init_version,
        #         args.target_version, args.remote_name)

        # # check if each folder is a valid module or not
        # for subfolder in subfolders:
        #     if (subfolder / "__openerp__.py").exists() or (
        #         subfolder / "__manifest__.py"
        #     ).exists():
        #         modules_path.append(subfolder)
        #     else:
        #         if modules_list:
        #             _logger.warning(
        #                 "The module %s was not found in the directory %s"
        #                 % (subfolder.name, args.directory)
        #             )

        # if modules_path:
        #     _logger.debug(
        #         "The lib will process the following modules '%s'"
        #         % (", ".join([x.name for x in modules_path]))
        #     )
        # else:
        #     _logger.error("No module found.")

        # # Compute migration list
        # migration_list = tools._get_migration_list(
        #     args.init_version, args.target_version
        # )

        # for module_path in modules_path:
        #     # Use black to clean the code
        #     if args.enable_black:
        #         pass

        #     # migrate modules
        #     migrate_tools._migrate_module(
        #         _logger, root_path, module_path, migration_list)

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
