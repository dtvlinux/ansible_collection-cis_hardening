#!/usr/bin/python

# Copyright: (c) 2025, Your Name <your@email.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import os
import re

from ansible.module_utils.basic import AnsibleModule

def run_module():
    module_args = dict(
        config_file=dict(type='str', required=False, default='/etc/modprobe.d/cis_hardening.conf'),
        modules=dict(type='list', elements='str', required=True),
    )

    result = dict(
        changed=False,
        message='',
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

    if owner_needs_change or mode_needs_change or not file_exists:
        changed = True

    # Ensure header
    header_needs_change = not lines or lines[0].rstrip('\n') != comment
    if header_needs_change:
        lines = [comment + '\n'] + lines
        content_changed = True

    # Process each module
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
                    found_index = i  # Update to last match

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

    # Apply changes
    if not module.check_mode:
        if content_changed or not file_exists:
            with open(config_file, 'w') as f:
                f.writelines(lines)

        need_set_perms = owner_needs_change or mode_needs_change or content_changed or not file_exists
        if need_set_perms:
            os.chown(config_file, 0, 0)
            os.chmod(config_file, 0o644)

    result['changed'] = changed
    result['message'] = f'Ensured configuration file {config_file} exists with correct ownership, permissions, managed header, and kernel module configurations.'

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
