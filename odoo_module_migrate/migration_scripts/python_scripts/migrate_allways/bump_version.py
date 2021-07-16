import os


def bump_revision(**kwargs):
    tools = kwargs['tools']
    manifest_path = kwargs['manifest_path']
    migration_steps = kwargs['migration_steps']
    target_version_name = migration_steps[-1]["target_version_name"]
    init_version_name = migration_steps[0]["init_version_name"]

    module_path = kwargs['module_path']
    migration_path_folder = module_path / 'i18n'
    file_paths = migration_path_folder.rglob("*")
    line_to_change = '"Project-Id-Version: Odoo Server {}'
    old_term = line_to_change.format(
        init_version_name
    )
    new_term = line_to_change.format(
        target_version_name
    )
    for file_path in file_paths:
        if os.path.isfile(file_path):
            tools._replace_in_file(
                file_path,
                {old_term: new_term}
            )

    new_version = "%s.1.0.0" % target_version_name

    old_term = r"('|\")version('|\").*('|\").*('|\")"
    new_term = r'\1version\2: "{0}"'.format(new_version)
    tools._replace_in_file(
        manifest_path, {old_term: new_term},
        "Bump version to %s" % new_version)
