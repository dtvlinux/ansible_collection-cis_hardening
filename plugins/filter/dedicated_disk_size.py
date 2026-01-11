# plugins/filter/dedicated_disk_size.py

DOCUMENTATION = r'''
  name: dedicated_disk_size
  author:
    - Michael Lucraft (@dtvlinux)
  short_description: Get the size of a specific disk from ansible_devices
  description:
    - This filter retrieves the human-readable size of a disk device from the ansible_devices fact.
  options:
    device_name:
      description: The name of the device (e.g., 'sda').
      type: str
      required: true
    ansible_devices:
      description: The ansible_devices fact dictionary.
      type: dict
      required: true
'''

class FilterModule(object):
    def filters(self):
        return {'dedicated_disk_size': self.dedicated_disk_size}

    def dedicated_disk_size(self, device_name, ansible_devices):
        device_info = ansible_devices.get(device_name)
        if device_info and 'size' in device_info:
            return device_info['size']
        return "0"
