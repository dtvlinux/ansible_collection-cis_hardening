# plugins/filter/current_mount_options.py

DOCUMENTATION = r'''
  name: current_mount_options
  author:
    - Michael Lucraft (@dtvlinux)
  short_description: Get current mount options from facts or task results
  description: 
    - This filter returns the mount options for a specific path.
  options:
    facts_mounts:
      description: The ansible_facts['mounts'] list.
      type: list
      required: true
    mount_path:
      description: The path to check.
      type: str
      required: true
'''

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
