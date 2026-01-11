# get_mount_options.py
class FilterModule(object):
    def filters(self):
        return {
            'current_mount_options': self.current_mount_options
        }

    def current_mount_options(self, facts_mounts, mount_path, task_results=None):
        if task_results:
            for result in reversed(task_results):
                if result.get('changed'):
                    return result.get('opts', 'defaults')

        mount = next((m for m in facts_mounts if m['mount'] == mount_path), None)
        if mount:
            return mount.get('options', 'defaults')

        return 'defaults'
