import pathlib
from .config import _AVAILABLE_MIGRATION_STEPS


class Migration():

    _migration_steps = []
    _absolute_directory_path = False

    def __init__(
        self, init_version_name, target_version_name, relative_directory_path
    ):
        pass
        # Get migration steps that will be runned
        found = False
        for item in _AVAILABLE_MIGRATION_STEPS:
            if not found and item["init_version_name"] != init_version_name:
                continue
            else:
                found = True
            self._migration_steps.append(item)
            if item["target_version_name"] == target_version_name:
                break
            import pdb; pdb.set_trace()

    def run(self):
        print("Migration Steps will be executed")
        print(self._migration_steps)
