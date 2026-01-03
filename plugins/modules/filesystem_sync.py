#!/usr/bin/python

# Copyright: (c) 2026, Michael Lucraft @dtvlinux
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r'''
---
module: filesystem_sync
short_description: Synchronize filesystem data to a new device or partition
author:
  - Michael Lucraft (@dtvlinux)
version_added: "1.0.0"
description:
  - "This module synchronizes data from a source directory to a target block device via a temporary mount point."
  - "It is designed for CIS hardening workflows where data must be moved to new, compliant partitions."
  - "The module automatically creates the source directory if it is missing and skips synchronization if the source is empty."
  - "Supports path-specific default excludes (e.g., for /var or /var/log) unless overridden by the 'excludes' option."
  - "Ensures the temporary mount point is cleaned up after execution, even on failure."
  - "Supports check mode to validate if a sync is required without modifying the target device."
options:
  path:
    description:
      - The source directory path to synchronize data from.
    required: true
    type: str
  device:
    description:
      - The target block device (e.g., /dev/mapper/vg-lv) to mount and sync data into.
    required: true
    type: str
  excludes:
    description:
      - A list of rsync-style exclude patterns.
      - If omitted, the module uses internal defaults: C(['log/*', 'tmp/*']) for C(/var) and C(['audit/*']) for C(/var/log).
      - Set to an empty list C([]) to force a sync with no exclusions.
    required: false
    type: list
    elements: str
'''

EXAMPLES = r'''
- name: Sync /var using internal module defaults
  dtvlinux.cis_hardening.filesystem_sync:
    path: /var
    device: /dev/mapper/vg-lv

- name: Sync /var with specific excludes via imported variable
  dtvlinux.cis_hardening.filesystem_sync:
    path: /var
    device: /dev/mapper/vg-lv
    excludes:
      - 'log/*'
      - 'tmp/*'

- name: Force a full sync with no exclusions
  dtvlinux.cis_hardening.filesystem_sync:
    path: "/home"
    device: "/dev/sdb1"
    excludes: []
'''

RETURN = r'''
---
changed:
  description: Whether data was synchronized or a new source directory was created.
  type: bool
  returned: always
message:
  description: Summary of the action performed.
  type: str
  returned: always
applied_excludes:
  description: The actual list of exclude patterns used during the rsync process.
  type: list
  returned: success
  elements: str
'''

from ansible.module_utils.basic import AnsibleModule
import os

def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            path=dict(type='str', required=True),
            device=dict(type='str', required=True),
            excludes=dict(type='list', elements='str', required=False)
        ),
        supports_check_mode=True
    )

    path = module.params['path'].rstrip('/')
    device = module.params['device']
    user_excludes = module.params.get('excludes')
    temp_mnt = f"/mnt/sync_{os.path.basename(path)}"

    if not os.path.isdir(path):
        if not module.check_mode:
            os.makedirs(path, mode=0o750)
        module.exit_json(changed=True, message=f"Source {path} was missing; created directory.")

    if not os.listdir(path):
        module.exit_json(changed=False, message=f"Source {path} is empty; no data to sync.")

    if module.check_mode:
        module.exit_json(changed=True, message="Changes would be applied (check mode).")

    default_excludes_map = {
        '/var': ['log/*', 'tmp/*'],
        '/var/log': ['audit/*']
    }

    if user_excludes is not None:
        active_excludes = user_excludes
    else:
        active_excludes = default_excludes_map.get(path, [])

    rsync_cmd = ['rsync', '-aAXH', '--delete', '--exclude=lost+found']
    for pattern in active_excludes:
        rsync_cmd.append(f'--exclude={pattern}')
    rsync_cmd.extend([f"{path}/", temp_mnt])

    os.makedirs(temp_mnt, exist_ok=True)
    try:
        rc, _, err = module.run_command(['mount', device, temp_mnt])
        if rc != 0:
            module.fail_json(msg=f"Failed to mount {device} on {temp_mnt}: {err}")

        rc_rs, _, err_rs = module.run_command(rsync_cmd)
        if rc_rs != 0:
            module.fail_json(msg=f"Rsync failed: {err_rs}")

    finally:
        module.run_command(['umount', temp_mnt])
        if os.path.exists(temp_mnt):
            os.rmdir(temp_mnt)

    module.exit_json(
        changed=True, 
        message=f"Successfully synced {path} to {device}",
        applied_excludes=active_excludes
    )

if __name__ == '__main__':
    run_module()
