#!/usr/bin/python

# Copyright: (c) 2025, Your Name <your@email.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import os
import re
import subprocess

from ansible.module_utils.basic import AnsibleModule

def run_module():
    module_args = dict(
        config_file=dict(type='str', required=False, default='/etc/modprobe.d/cis_hardening.conf'),
        modules=dict(type='list', elements='str', required=True),
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

    # Special handling for squashfs
    squashfs_in_use = False
    squashfs_builtin = False

    # Check if squashfs is in use (snap packages mounted)
    try:
        snap_output = subprocess.check_output("lsblk | grep -wc '/snap'", shell=True, text=True).strip()
        if int(snap_output) > 0:
            squashfs_in_use = True
    except Exception:
        pass

    # Check if squashfs is built into the kernel
    try:
        kernel = subprocess.check_output(['uname', '-r'], text=True).strip()
        builtin_cmd = f"cat /lib/modules/{kernel}/modules.builtin | grep 'squashfs'"
        subprocess.check_call(builtin_cmd, shell=True)
        squashfs_builtin = True
    except subprocess.CalledProcessError as e:
        if e.returncode not in [0, 1]:
            module.fail_json(msg=f"Failed to check if squashfs is built-in: {str(e)}", **result)
    except Exception as e:
        module.fail_json(msg=f"Failed to check if squashfs is built-in: {str(e)}", **result)

    # If squashfs is in use (via snap) or built-in, skip it
    skip_squashfs = squashfs_in_use or squashfs_builtin

    if skip_squashfs and 'squashfs' in modules_list:
        result['skipped_modules'].append('squashfs')
        result['debug_message'] = 'squashfs is in use (snap packages or built-in kernel module) - skipped configuration and unloading.'
        # Remove squashfs from processing list to pretend it's not there
        modules_list = [m for m in modules_list if m != 'squashfs']

    try:
        # Read or initialize file content
        with open(config_file, 'r') as f:
            lines = f.readlines()
        file_exists = True
    except FileNotFoundError:
        lines = []
        file_exists = False

    # Check/correct ownership and permissions
    owner_needs_change = False
    mode_needs_change = False
    if file_exists:
        stat_info = os.stat(config_file)
        current_uid = stat_info.st_uid
        current_gid = stat_info.st_gid
        current_mode = stat_info.st_mode & 0o777

        owner_needs_change = (current_uid != 0 or current_gid != 0)
        mode_needs_change = (current_mode != 0o644)

    if owner_needs_change or mode_needs_change or not file_exists:
        changed = True

    # Ensure managed header
    header_needs_change = not lines or lines[0].rstrip('\n') != comment
    if header_needs_change:
        lines = [comment + '\n'] + lines
        content_changed = True

    # Process each module for config
    for mod in modules_list:
        for is_install in [True, False]:
            if is_install:
                target_line = f"install {mod} /bin/false"
                regexp_str = r"^(#)?install " + re.escape(mod) + r"(\s|$)"
            else:
                target_line = f"blacklist {mod}"
                regexp_str = r"^(#)?blacklist " + re.escape(mod) + r"$"

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

    # Apply file changes if needed
    if not module.check_mode:
        if content_changed or not file_exists:
            with open(config_file, 'w') as f:
                f.writelines(lines)

        need_set_perms = owner_needs_change or mode_needs_change or content_changed or not file_exists
        if need_set_perms:
            os.chown(config_file, 0, 0)
            os.chmod(config_file, 0o644)

    # Unload modules if they are loaded (requires root)
    unloaded_modules = []
    for mod in modules_list:
        try:
            lsmod_output = subprocess.check_output(['lsmod'], text=True)
            if re.search(fr'\b{mod}\b', lsmod_output):
                if not module.check_mode:
                    subprocess.check_call(['modprobe', '-r', mod])
                unloaded_modules.append(mod)
                changed = True
        except subprocess.CalledProcessError:
            pass
        except Exception as e:
            module.fail_json(msg=f"Failed to handle module {mod}: {str(e)}", **result)

    result['changed'] = changed
    result['unloaded_modules'] = unloaded_modules

    message_parts = [
        f'Ensured configuration file {config_file} exists with correct ownership, '
        f'permissions, managed header, and kernel module configurations. '
        f'Unloaded {len(unloaded_modules)} modules: {", ".join(unloaded_modules) or "none"}.'
    ]

    # Include skip info only if verbose
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