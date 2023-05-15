def bump_revision(**kwargs):
    tools = kwargs["tools"]
    manifest_path = kwargs["manifest_path"]
    migration_steps = kwargs["migration_steps"]
    target_version_name = migration_steps[-1]["target_version_name"]

    new_version = "%s.1.0.0" % target_version_name

    old_term = r"('|\")version('|\").*('|\").*('|\")"
    new_term = r'\1version\2: "{0}"'.format(new_version)
    tools._replace_in_file(
        manifest_path, {old_term: new_term}, "Bump version to %s" % new_version
    )
