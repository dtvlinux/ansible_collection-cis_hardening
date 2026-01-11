# plugins/filter/dedicated_disk_size.py
class FilterModule(object):
    def filters(self):
        return {'dedicated_disk_size': self.dedicated_disk_size}

    def dedicated_disk_size(self, device_name, ansible_devices):
        device_info = ansible_devices.get(device_name)
        if device_info and 'size' in device_info:
            return device_info['size']
        return "0"
