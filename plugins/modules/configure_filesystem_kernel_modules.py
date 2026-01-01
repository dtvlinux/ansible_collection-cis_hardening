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

import os

from ansible.module_utils.basic import AnsibleModule

class ConfigureFilesystemKernelModules:
    FILE_HEADER = '# Managed by Ansible collection dtvlinux.cis_hardening'
    FILE_MODE   = 0o644
    FILE_UID    = 0
    FILE_GID    = 0

    def __init__(self, module):
        self.module      = module
        self.config_file = module.params['config_file']
        self.modules     = module.params['modules']
    
    def filter_modules(self):
        if 'squashfs' not in self.modules:
            return None

        squashfs_in_use  = '/snap/' in open('/proc/mounts').read()

        builtin_path = f'/lib/modules/{os.uname()[2]}/modules.builtin'
        squashfs_builtin = 'squashfs' in open(builtin_path).read() if os.path.exists(builtin_path) else False

        if squashfs_in_use or squashfs_builtin:
            if len(self.modules) == 1:
                self.module.exit_json(changed=False, msg="skipped squashfs as in use")
            
            self.modules = [m for m in self.modules if m != 'squashfs']
            return "skipped squashfs as in use"
        
        return None

    def check_config_file_exists(self):
        return os.path.exists(self.config_file)
    
    def check_config_file_mode(self):
        return (os.stat(self.config_file).st_mode & 0o777) == self.FILE_MODE

    def update_config_file_mode(self):
        os.chmod(self.config_file, self.FILE_MODE)

    def check_config_file_user(self):
        return os.stat(self.config_file).st_uid == self.FILE_UID

    def check_config_file_group(self):
        return os.stat(self.config_file).st_gid == self.FILE_GID
    
    def update_config_file_ownership(self):
        os.chown(self.config_file, self.FILE_UID, self.FILE_GID)
    
    def check_config_file_header(self):
        with open(self.config_file, 'r') as f:
            return f.readline().strip() == self.FILE_HEADER

    def update_config_file_header(self):
        with open(self.config_file, 'r') as f:
            lines = f.readlines()

        if not lines:
            lines = [f"{self.FILE_HEADER}\n"]
        elif lines[0].strip().startswith(('install', 'blacklist')):
            lines = [f"{self.FILE_HEADER}\n"] + lines
        else:
            lines = [f"{self.FILE_HEADER}\n"] + lines[1:]

        with open(self.config_file, 'w') as f:
            f.writelines(lines)
    
    def check_config_file_contents(self):
        with open(self.config_file, 'r') as f:
            file_lines = [line.strip() for line in f.readlines()]

        module_status = {}
        for module_name in self.modules:
            install_line   = f"install {module_name} /bin/false"
            blacklist_line = f"blacklist {module_name}"
            
            has_required = (install_line in file_lines and blacklist_line in file_lines)
            
            other_mentions = [
                l for l in file_lines 
                if module_name in l and l != install_line and l != blacklist_line
            ]
            
            module_status[module_name] = has_required and not other_mentions
        
        return module_status
    
    def update_config_file_contents(self):
        with open(self.config_file, 'r') as f:
            lines = f.readlines()

        new_lines = [lines[0]]

        for line in lines[1:]:
            if not any(m in line for m in self.modules):
                new_lines.append(line)

        if not new_lines[-1].endswith('\n'):
            new_lines[-1] += '\n'

        for module_name in self.modules:
            new_lines.append(f"install {module_name} /bin/false\n")
            new_lines.append(f"blacklist {module_name}\n")

        with open(self.config_file, 'w') as f:
            f.writelines(new_lines)

    def validate_current_state(self):
        if not self.check_config_file_exists():
            return {
                "conf_contents":   {m: False for m in self.modules},
                "conf_exists":     False,
                "conf_group":      False,
                "conf_header":     False,
                "conf_mode":       False,
                "conf_user":       False,
                "module_unloaded": {m: False for m in self.modules},
            }
        
        return {
            "conf_contents":   self.check_config_file_contents(),
            "conf_exists":     True,
            "conf_group":      self.check_config_file_group(),
            "conf_header":     self.check_config_file_header(),
            "conf_mode":       self.check_config_file_mode(),
            "conf_user":       self.check_config_file_user(),
            "module_unloaded": self.check_modules_unloaded(),
        }

    def create_config_file(self):
        with open(self.config_file, 'w') as f:
            f.write(f"{self.FILE_HEADER}\n")
            for module_name in self.modules:
                f.write(f"install {module_name} /bin/false\n")
                f.write(f"blacklist {module_name}\n")
        
        os.chown(self.config_file, self.FILE_UID, self.FILE_GID)
        os.chmod(self.config_file, self.FILE_MODE)
    
    def check_modules_unloaded(self):
        current_loaded = [line.split()[0] for line in open('/proc/modules').readlines()]
        return {m: (m not in current_loaded) for m in self.modules}

    def unload_modules(self, modules_to_unload):
        for m in modules_to_unload:
            self.module.run_command([self.module.get_bin_path('modprobe', True), '-r', m])


def main():
    module = AnsibleModule(
        argument_spec=dict(
            config_file=dict(type='str', required=False, default='/etc/modprobe.d/cis_hardening.conf'),
            modules=dict(type='list', elements='str', required=True),
        ),
        supports_check_mode=True,
    )

    manager  = ConfigureFilesystemKernelModules(module)
    skip_msg = manager.filter_modules()
    results  = manager.validate_current_state()
    
    if not results['conf_exists']:
        if not module.check_mode:
            manager.create_config_file()
        
        module.exit_json(
            changed=True,
            msg=f"Created {manager.config_file} with required settings.",
            validation_results=manager.validate_current_state() if not module.check_mode else results
        )

    changed = False
    change_msg = []

    if not results['conf_mode']:
        changed = True
        change_msg.append("updated file mode")
        if not module.check_mode:
            manager.update_config_file_mode()
    
    if not results['conf_user'] or not results['conf_group']:
        changed = True
        
        if not results['conf_user'] and not results['conf_group']:
            change_msg.append("updated file user and group")
        elif not results['conf_user']:
            change_msg.append("updated file user")
        else:
            change_msg.append("updated file group")

        if not module.check_mode:
            manager.update_config_file_ownership()

    if not results['conf_header']:
        changed = True
        change_msg.append("updated header")
        if not module.check_mode:
            manager.update_config_file_header()

    if not all(results['conf_contents'].values()):
        changed = True
        content_modules = [m for m, ok in results['conf_contents'].items() if not ok]
        change_msg.append(f"synchronized modules: {', '.join(content_modules)}")
        
        if not module.check_mode:
            manager.update_config_file_contents()

    to_unload = [m for m, is_unloaded in results['module_unloaded'].items() if not is_unloaded]

    if to_unload:
        changed = True
        change_msg.append(f"unloaded modules: {', '.join(to_unload)}")

        if not module.check_mode:
            manager.unload_modules(to_unload)

    if skip_msg:
        final_msg = f"{skip_msg}; {final_msg}"

    module.exit_json(
        changed=changed,
        msg="; ".join(change_msg) if changed else "File matches specification",
        validation_results=manager.validate_current_state() if (changed and not module.check_mode) else results
    )

if __name__ == "__main__":
    main()
