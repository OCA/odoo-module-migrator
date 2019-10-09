from .config import _AVAILABLE_MIGRATION_STEPS


class Migration():

    _migration_steps = []

    def __init__(self, init_version_name, target_version_name):
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

        # TODO compute list of migration scripts

    def run(self):
        print("Migration Steps will be executed")
        print(self._migration_steps)
