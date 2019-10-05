# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import argparse
import argcomplete
import logging
from pathlib import Path
from . import migrate_tools


_logger = logging.getLogger(__name__)

_MIGRATION_LIST = [
    ("8.0", "9.0"),
    ("9.0", "10.0"),
    ("10.0", "11.0"),
    ("11.0", "12.0"),
]


def _get_init_versions():
    return [x[0] for x in _MIGRATION_LIST]


def _get_target_versions():
    return [x[1] for x in _MIGRATION_LIST]


def _get_latest_version():
    return _MIGRATION_LIST[-1][1]


def _get_migration_list(init_version, target_version):
    found = False
    res = []
    for item in _MIGRATION_LIST:
        if not found and item[0] != init_version:
            continue
        else:
            found = True
        res.append(item)
        if item[1] == target_version:
            return res


def get_parser():
    """Return :py:class:`argparse.ArgumentParser` instance for CLI."""

    main_parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter
    )

    main_parser.add_argument(
        "-d",
        "--directory",
        dest="directory",
        required=True,
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
        "--init-version",
        choices=_get_init_versions(),
        dest="init_version",
        required=True,
        type=str,
    )

    main_parser.add_argument(
        "-fp",
        "--format-patch",
        dest="format_patch",
        default=False,
        type=bool,
    )

    main_parser.add_argument(
        "-rn",
        "--remote-name",
        dest="remote_name",
        default='origin',
        type=str,
    )

    main_parser.add_argument(
        "-l",
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        dest="log_level",
        default="INFO",
        type=str,
    )

    main_parser.add_argument(
        "-t",
        "--target-version",
        dest="target_version",
        type=str,
        choices=_get_target_versions(),
        default=_get_latest_version(),
        help="Target version of the Odoo module you want to migrate."
        " If 'latest' is set, the tool will try to migrate to the latest"
        " Odoo version.",
    )

    return main_parser


def main():
    # Parse Arguments
    parser = get_parser()
    argcomplete.autocomplete(parser, always_complete_options=False)
    args = parser.parse_args()

    # Set log level
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(levelname)-10s %(message)s")
    handler.setFormatter(formatter)
    _logger.addHandler(handler)
    _logger.setLevel(getattr(logging, str(args.log_level)))

    try:

        # Get Main path and test if exists
        root_path = Path(args.directory)
        if not root_path.exists():
            raise ValueError("'%s' is not a valid path." % (args.directory))

        # Recover modules list
        modules_path = []
        modules_list = args.modules\
            and [x for x in args.modules.split(",") if x] or []

        if not args.modules:
            # Recover all submodules, if no modules list is provided
            subfolders = [x for x in root_path.iterdir() if x.is_dir()]
        else:
            subfolders = [root_path / x for x in modules_list]

        # Recover code for former version, if asked
        if args.format_patch:
            if len(modules_list) != 1:
                raise ValueError(
                    "If 'format-patch' option is enabled, you should provide"
                    " a unique module name in the 'modules' argument.")
            migrate_tools._get_code_from_previous_branch(
                _logger, root_path, modules_list[0], args.init_version,
                args.target_version, args.remote_name)

        # check if each folder is a valid module or not
        for subfolder in subfolders:
            if (subfolder / "__openerp__.py").exists() or (
                subfolder / "__manifest__.py"
            ).exists():
                modules_path.append(subfolder)
            else:
                if modules_list:
                    _logger.warning(
                        "The module %s was not found in the directory %s"
                        % (subfolder.name, args.directory)
                    )

        if modules_path:
            _logger.debug(
                "The lib will process the following modules '%s'"
                % (", ".join([x.name for x in modules_path]))
            )
        else:
            _logger.error("No module found.")

        # Compute migration list
        migration_list = _get_migration_list(
            args.init_version, args.target_version
        )

        for module_path in modules_path:
            migrate_tools._migrate_module(
                root_path, module_path, migration_list)

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
