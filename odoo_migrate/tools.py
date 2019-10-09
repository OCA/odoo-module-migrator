from . import config


def _get_init_versions():
    return [x[0] for x in config._MIGRATION_LIST]


def _get_target_versions():
    return [x[1] for x in config._MIGRATION_LIST]


def _get_latest_version():
    return config._MIGRATION_LIST[-1][1]


def _get_migration_list(init_version, target_version):
    found = False
    res = []
    for item in config._MIGRATION_LIST:
        if not found and item[0] != init_version:
            continue
        else:
            found = True
        res.append(item)
        if item[1] == target_version:
            return res
