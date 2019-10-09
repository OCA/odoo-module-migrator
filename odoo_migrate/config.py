# List of migrations handled by this library
# _MIGRATION_LIST = [
#     ("8.0", "9.0"),
#     ("9.0", "10.0"),
#     ("10.0", "11.0"),
#     ("11.0", "12.0"),
#     ("12.0", "13.0"),
# ]


_AVAILABLE_MIGRATION_STEPS = [
    {
        "init_version_name": "8.0",
        "target_version_name": "9.0",
        "init_version_code": "080",
        "target_version_code": "090",
    }, {
        "init_version_name": "9.0",
        "target_version_name": "10.0",
        "init_version_code": "090",
        "target_version_code": "100",
    }, {
        "init_version_name": "10.0",
        "target_version_name": "11.0",
        "init_version_code": "100",
        "target_version_code": "110",
    }, {
        "init_version_name": "11.0",
        "target_version_name": "12.0",
        "init_version_code": "110",
        "target_version_code": "120",
    }, {
        "init_version_name": "12.0",
        "target_version_name": "13.0",
        "init_version_code": "120",
        "target_version_code": "130",
    },

    # ("8.0", "9.0"),
    # ("9.0", "10.0"),
    # ("10.0", "11.0"),
    # ("11.0", "12.0"),
    # ("12.0", "13.0"),
]

_ALLOWED_EXTENSIONS = [".py", ".xml", ".js"]
