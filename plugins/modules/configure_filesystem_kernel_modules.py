#!/usr/bin/python

# Copyright: (c) 2025, Michael Lucraft @dtvlinux
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: configure_filesystem_kernel_modules

short_description: Configure filesystem kernel modules

version_added: "1.0.0"

description: This module creates or updates a configuration file in /etc/modprobe.d/ to disable specified kernel modules by blacklisting them and setting install to /bin/false. It also unloads the modules if they are currently loaded. Special handling for 'squashfs' by skipping configuration and unloading if it is in use (e.g., via snap packages) or built into the kernel. The module is idempotent and supports check mode. If 'squashfs' is the only module and it is skipped, the config file is not created if it does not exist.

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

author:
  - Michael Lucraft (@dtvlinux)
'''

EXAMPLES = r'''

# Specify single module for disabling
- name: Disable cramfs
  dtvlinux.cis_hardening.configure_filesystem_kernel_modules:
    modules: cramfs

# Specifiy multiple modules to be disabled
- name: Disable cramfs & freevxfs
  dtvlinux.cis_hardening.configure_filesystem_kernel_modules:
    modules:
      - cramfs
      - freevxfs

# Specify a custom configuration file
- name: Disable cramfs
  dtvlinux.cis_hardening.configure_filesystem_kernel_modules:
    config_file: /etc/modprobe.d/cramfs.conf
    modules: cramfs
'''

RETURN = r'''
changed:
  description: Whether the module made any changes to the system.
  type: bool
  returned: always

message:
  description: A status message describing the actions taken.
  type: str
  returned: always

unloaded_modules:
  description: List of modules that were unloaded during the run.
  type: list
  elements: str
  returned: always

skipped_modules:
  description: List of modules that were skipped (e.g., squashfs if in use).
  type: list
  elements: str
  returned: when verbosity >=1

debug_message:
  description: Additional debug information about why modules were skipped.
  type: str
  returned: when verbosity >=1
'''

import os
import re
import subprocess

from ansible.module_utils.basic import AnsibleModule

def run_module():
    module_args = dict(
        config_file=dict(
            type='str',
            required=False,
            default='/etc/modprobe.d/cis_hardening.conf'
        ),
        modules=dict(
            type='list',
            elements='str',
            required=True
        ),
    )

    result = dict(
        changed=False,
        message='',
        unloaded_modules=[],
        skipped_modules=[],
        debug_message='',
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    config_file = module.params['config_file']
    modules_list = module.params['modules']
    changed = False
    content_changed = False
    comment = '# Managed by Ansible collection dtvlinux.cis_hardening'

    squashfs_in_use = False
    squashfs_builtin = False

    try:
        snap_output = subprocess.check_output(['lsblk', '-o', 'MOUNTPOINT'], text=True)
        snap_count = sum(1 for line in snap_output.splitlines() if '/snap' in line.strip())
        if snap_count > 0:
            squashfs_in_use = True
    except Exception:
        pass

    try:
        kernel = os.uname()[2]
        builtin_path = f'/lib/modules/{kernel}/modules.builtin'
        if os.path.exists(builtin_path):
            with open(builtin_path, 'r') as f:
                for line in f:
                    if 'squashfs' in line:
                        squashfs_builtin = True
                        break
    except Exception as e:
        module.fail_json(msg=f"Failed to check if squashfs is built-in: {str(e)}", **result)

    skip_squashfs = squashfs_in_use or squashfs_builtin

    if skip_squashfs and 'squashfs' in modules_list:
        result['skipped_modules'].append('squashfs')
        result['debug_message'] = 'squashfs is in use (snap packages or built-in kernel module) - skipped configuration and unloading.'
        modules_list = [m for m in modules_list if m != 'squashfs']

    try:
        with open(config_file, 'r') as f:
            lines = f.readlines()
        file_exists = True
    except FileNotFoundError:
        lines = []
        file_exists = False

    owner_needs_change = False
    mode_needs_change = False
    if file_exists:
        stat_info = os.stat(config_file)
        current_uid = stat_info.st_uid
        current_gid = stat_info.st_gid
        current_mode = stat_info.st_mode & 0o777

        owner_needs_change = (current_uid != 0 or current_gid != 0)
        mode_needs_change = (current_mode != 0o644)

    if owner_needs_change or mode_needs_change:
        changed = True

    if modules_list:
        header_needs_change = not lines or lines[0].rstrip('\n') != comment
        if header_needs_change:
            lines = [comment + '\n'] + lines
            content_changed = True

        for mod in modules_list:
            for is_install in [True, False]:
                if is_install:
                    target_line = f"install {mod} /bin/false"
                    regexp_str = r"^(#)?install\s+" + re.escape(mod) + r"\s"
                else:
                    target_line = f"blacklist {mod}"
                    regexp_str = r"^(#)?blacklist\s+" + re.escape(mod) + r"$"

                regexp = re.compile(regexp_str)

                found_index = -1
                for i, line in enumerate(lines):
                    if regexp.match(line.rstrip('\n')):
                        found_index = i

                this_needs_change = False
                if found_index != -1:
                    current_line = lines[found_index].rstrip('\n')
                    if current_line != target_line:
                        this_needs_change = True
                        if not module.check_mode:
                            lines[found_index] = target_line + '\n'
                else:
                    this_needs_change = True
                    if not module.check_mode:
                        lines.append(target_line + '\n')

                if this_needs_change:
                    content_changed = True

        if content_changed:
            changed = True

    if not module.check_mode:
        if modules_list and (content_changed or not file_exists):
            with open(config_file, 'w') as f:
                f.writelines(lines)

        need_set_perms = owner_needs_change or mode_needs_change or (modules_list and (content_changed or not file_exists))
        if need_set_perms:
            os.chown(config_file, 0, 0)
            os.chmod(config_file, 0o644)

    unloaded_modules = []
    if modules_list:
        try:
            lsmod_output = subprocess.check_output(['lsmod'], text=True)
            loaded_modules = set()
            for line in lsmod_output.splitlines()[1:]:
                if line.strip():
                    loaded_modules.add(line.split()[0])
        except Exception as e:
            module.fail_json(msg=f"Failed to check loaded modules: {str(e)}", **result)

        for mod in modules_list:
            if mod in loaded_modules:
                if not module.check_mode:
                    try:
                        subprocess.check_call(['modprobe', '-r', mod])
                    except subprocess.CalledProcessError:
                        pass
                unloaded_modules.append(mod)
                changed = True

    result['changed'] = changed
    result['unloaded_modules'] = unloaded_modules

    message_parts = [
        f'Ensured configuration file {config_file} exists with correct ownership, '
        f'permissions, managed header, and kernel module configurations.'
    ]

    if module._verbosity >= 1:
        if result['skipped_modules']:
            skip_msg = f'Skipped modules: {", ".join(result["skipped_modules"])} ({result["debug_message"]}).'
            message_parts.append(skip_msg)
    else:
        if 'skipped_modules' in result:
            del result['skipped_modules']
        if 'debug_message' in result:
            del result['debug_message']

    result['message'] = ' '.join(message_parts)

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
