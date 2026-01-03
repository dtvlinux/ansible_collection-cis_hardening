#!/usr/bin/python

# Copyright: (c) 2026, Michael Lucraft @dtvlinux
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r'''
---
module: configure_filesystem_kernel_modules
short_description: Disable filesystem kernel modules
author:
  - Michael Lucraft (@dtvlinux)
version_added: "1.0.0"
description:
  - "This module manages a modprobe configuration file to disable specified kernel modules (typically filesystem-related) by adding 'install' and 'blacklist' directives."
  - "It ensures the configuration file exists with correct ownership (root:root), mode (0644), and a managed header."
  - "If modules are currently loaded, it unloads them."
  - "Special handling for 'squashfs': skips configuration if in use (e.g., /snap/ mounted) or built into the kernel."
  - "Supports check mode to validate without changes."
options:
  config_file:
    description:
      - Path to the modprobe configuration file.
    required: false
    type: str
    default: /etc/modprobe.d/cis_hardening.conf
  modules:
    description:
      - List of kernel modules to disable.
    required: true
    type: list
    elements: str
'''

EXAMPLES = r'''
- name: Specify single module for disabling
  dtvlinux.cis_hardening.configure_filesystem_kernel_modules:
    modules: cramfs

- name: Specifiy multiple modules to be disabled
  dtvlinux.cis_hardening.configure_filesystem_kernel_modules:
    modules:
      - cramfs
      - freevxfs

- name: Specify a custom configuration file
  dtvlinux.cis_hardening.configure_filesystem_kernel_modules:
    config_file: /etc/modprobe.d/cramfs.conf
    modules: cramfs
'''

RETURN = r'''
---
changed:
  description: Whether any changes were made.
  type: bool
  returned: always
msg:
  description: Summary message of actions taken or skipped.
  type: str
  returned: always
validation_results:
  description: Dictionary of validation states for the configuration.
  type: dict
  returned: always
  contains:
    exists:
      description: Whether the config file exists.
      type: bool
    mode:
      description: Whether the file mode is 0644.
      type: bool
    user:
      description: Whether the file owner is root (UID 0).
      type: bool
    group:
      description: Whether the file group is root (GID 0).
      type: bool
    header:
      description: Whether the file starts with the managed header.
      type: bool
    contents:
      description: Dictionary where keys are module names and values indicate if the module is correctly configured (install and blacklist lines present, no other mentions).
      type: dict
    unloaded:
      description: Dictionary where keys are module names and values indicate if the module is unloaded.
      type: dict
'''

from ansible.module_utils.basic import AnsibleModule
import os

def run_module():
    module_args = dict(
        path=dict(type='str', required=True),
        device=dict(type='str', required=True),
    )

    result = dict(changed=False, message='')
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    path = module.params['path'].rstrip('/')
    device = module.params['device']
    temp_mnt = f"/mnt/sync_{os.path.basename(path)}"

    if not os.path.exists(path) or not os.path.isdir(path):
        result['message'] = f"Source path {path} does not exist. Created directory for future mount."
        if not module.check_mode:
            os.makedirs(path, mode=0o750)
        module.exit_json(**result)

    if not os.listdir(path):
        result['message'] = f"Source path {path} is empty. No data to sync."
        module.exit_json(**result)

    if module.check_mode:
        result['changed'] = True
        module.exit_json(**result)

    if not os.path.exists(temp_mnt):
        os.makedirs(temp_mnt)

    try:
        rc, _, err = module.run_command(['mount', device, temp_mnt])
        if rc != 0:
            module.fail_json(msg=f"Failed to mount {device} on {temp_mnt}: {err}")

        rsync_src = path + '/'
        rsync_cmd = ['rsync', '-aAXH', '--delete', '--exclude=lost+found']

        if path == '/var':
            rsync_cmd.extend([
                '--exclude=log/*', 
                '--exclude=log/audit/*', 
                '--exclude=tmp/*'
            ])
        elif path == '/var/log':
            rsync_cmd.append('--exclude=audit/*')

        rsync_cmd.extend([rsync_src, temp_mnt])
        
        rc_rs, _, err_rs = module.run_command(rsync_cmd)
        
        if rc_rs == 0:
            result['changed'] = True
            result['message'] = f"Successfully synced data from {path} to {device}"
        else:
            module.fail_json(msg=f"Rsync failed: {err_rs}")

    finally:
        module.run_command(['umount', temp_mnt])
        if os.path.exists(temp_mnt):
            os.rmdir(temp_mnt)

    module.exit_json(**result)

if __name__ == '__main__':
    run_module()
