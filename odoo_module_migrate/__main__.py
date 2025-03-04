# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import argparse
import argcomplete
import sys

from . import tools
from .log import setup_logger
from .migration import Migration


def get_parser():

    main_parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

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
        help="Target Modules to migrate."
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
        action="store_true",
        help="Enable this option, if you want to get the code from the"
        " previous branch.",
    )

    main_parser.add_argument(
        "-rn",
        "--remote-name",
        dest="remote_name",
        default="origin",
        type=str,
    )

    main_parser.add_argument(
        "-ll",
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        dest="log_level",
        default="INFO",
        type=str,
    )

    main_parser.add_argument(
        "-lp",
        "--log-path",
        dest="log_path",
        default=False,
        type=str,
    )

    main_parser.add_argument(
        "-nc",
        "--no-commit",
        action="store_true",
        default=False,
        help="Enable this option, if you don't want that the library commits"
        " the changes. (using git add and git commit command)",
    )

    # TODO: Move to `argparse.BooleanOptionalAction` once in Python 3.9+
    main_parser.add_argument(
        "-npc",
        "--no-pre-commit",
        dest="pre_commit",
        action="store_false",
        help="Skip pre-commit execution",
    )

    # TODO: Move to `argparse.BooleanOptionalAction` once in Python 3.9+
    main_parser.add_argument(
        "-nrmf",
        "--no-remove-migration-folder",
        dest="remove_migration_folder",
        action="store_false",
        help="Skip removing migration folder",
    )

    return main_parser


def main(args=False):
    # Parse Arguments
    parser = get_parser()
    argcomplete.autocomplete(parser, always_complete_options=False)
    if args:
        args = parser.parse_args(args)
    else:
        args = parser.parse_args()

    # Set log level
    setup_logger(args.log_level, args.log_path)

    try:
        # Create a new Migration Object
        module_names = (
            args.modules
            and [x.strip() for x in args.modules.split(",") if x.strip()]
            or []
        )

        migration = Migration(
            args.directory,
            args.init_version_name,
            args.target_version_name,
            module_names,
            args.format_patch,
            args.remote_name,
            not args.no_commit,
            args.pre_commit,
            args.remove_migration_folder,
        )

        # run Migration
        migration.run()

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main(sys.argv[1:])
