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
      - "A list of rsync-style exclude patterns."
      - "If omitted, the module uses internal defaults: ['log/*', 'tmp/*'] for /var and ['audit/*'] for /var/log."
      - "Set to an empty list [] to force a sync with no exclusions."
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
reboot_required:
  description: Whether the changes require a system reboot to take effect.
  type: bool
  returned: always
'''

from ansible.module_utils.basic import AnsibleModule
import os
import stat
import json
import re

def size_to_bytes(size_str):
    size_str = size_str.upper()
    match = re.match(r'^(\d+(?:\.\d+)?)([BKMGT])?$', size_str)
    if not match:
        raise ValueError("Invalid size format")
    num, unit = match.groups()
    num = float(num)
    units = {'B': 1, 'K': 1024, 'M': 1024**2, 'G': 1024**3, 'T': 1024**4}
    multiplier = units.get(unit, 1)
    return int(num * multiplier)

class DedicatedDiskPartition:
    FILE_FSTAB = '/etc/fstab'
    FSTAB_OPTS = 'defaults'

    def __init__(self, module):
        self.module = module
        self.device = module.params['device']
        self.vg = module.params['vg']
        self.lv = module.params['lv']
        self.size = module.params['size']
        self.fstype = module.params['fstype']
        self.sync = module.params['sync']
        self.path = module.params['path'].rstrip('/')
        self.excludes = module.params['excludes']
        self.lv_device = f"/dev/{self.vg}/{self.lv}"
        self.lv_mapper = f"/dev/mapper/{self.vg}-{self.lv}"
        self.temp_mnt = f"/mnt/sync_{os.path.basename(self.path)}"

    def check_block_device(self):
        if not os.path.exists(self.device):
            return False
        dev_stat = os.stat(self.device)
        return stat.S_IFMT(dev_stat.st_mode) == stat.S_IFBLK

    def check_device_in_use(self):
        # Check if it's a PV first
        rc, out, err = self.module.run_command(['pvs', '--noheadings', '-o', 'vg_name', self.device])
        if rc == 0:
            vg_name = out.strip()
            if vg_name and vg_name != self.vg:
                return True  # Part of different VG
            return False  # Already in our VG or orphan, ok

        # If not PV, check if device has filesystem (non-LVM)
        rc, out, err = self.module.run_command(['blkid', '-s', 'TYPE', '-o', 'value', self.device])
        if rc == 0 and out.strip():
            return True

        # Check for partitions/children or mounts
        rc, out, err = self.module.run_command(['lsblk', '-J', '-o', 'NAME,TYPE,MOUNTPOINTS', self.device])
        if rc != 0:
            return True
        lsblk_data = json.loads(out)
        device_info = lsblk_data['blockdevices'][0]
        if device_info.get('mountpoints', [None])[0] is not None:
            return True
        if device_info.get('children'):
            return True

        return False

    def ensure_pv(self):
        rc, _, _ = self.module.run_command(['pvs', self.device])
        if rc == 0:
            return False  # Already PV
        self.module.run_command(['pvcreate', self.device], check_rc=True)
        return True

    def check_vg_exists(self):
        rc, _, _ = self.module.run_command(['vgs', self.vg])
        return rc == 0

    def ensure_vg(self):
        changed = False
        if not self.check_vg_exists():
            # Check if orphan PV
            rc, out, _ = self.module.run_command(['pvs', '--noheadings', '-o', 'vg_name', self.device])
            if rc == 0 and not out.strip():
                self.module.run_command(['pvremove', '--force', self.device], check_rc=True)
                changed = True

            changed |= self.ensure_pv()
            self.module.run_command(['vgcreate', self.vg, self.device], check_rc=True)
            changed = True
        else:
            rc, out, _ = self.module.run_command(['pvs', '--noheadings', '-o', 'pv_name', '-S', f'vg_name={self.vg}'])
            resolved_device = os.path.realpath(self.device)
            resolved_pvs = [os.path.realpath(pv.strip()) for pv in out.split() if pv.strip()]
            if resolved_device not in resolved_pvs:
                self.module.fail_json(msg=f"VG {self.vg} exists but specified device {self.device} is not part of it; extension not allowed")
        return changed

    def check_lv_exists(self):
        rc, _, _ = self.module.run_command(['lvs', f"{self.vg}/{self.lv}"])
        return rc == 0

    def get_lv_size(self):
        rc, out, err = self.module.run_command(['lvs', '--noheadings', '-o', 'lv_size', '--units', 'b', '--nosuffix', f"{self.vg}/{self.lv}"])
        if rc == 0:
            return out.strip()
        else:
            self.module.fail_json(msg=f"Failed to get LV size: {err}")

    def create_lv(self):
        self.module.run_command(['lvcreate', '--yes', '-L', self.size, '-n', self.lv, self.vg], check_rc=True)

    def resize_lv(self):
        self.module.run_command(['lvextend', '-L', self.size, '-r', self.lv_device], check_rc=True)

    def get_fs_type(self):
        rc, out, _ = self.module.run_command(['blkid', '-s', 'TYPE', '-o', 'value', self.lv_device])
        return out.strip() if rc == 0 else ''

    def create_fs(self):
        self.module.run_command(['mkfs', '-t', self.fstype, self.lv_device], check_rc=True)

    def check_fstab_entry(self):
        with open(self.FILE_FSTAB, 'r') as f:
            lines = f.readlines()

        has_correct = False
        previous_lines = []
        for i, line in enumerate(lines):
            if line.startswith('#'):
                continue
            fields = re.split(r'\s+', line.strip())
            if len(fields) < 6 or fields[1] != self.path:
                continue
            if fields[0] in (self.lv_device, self.lv_mapper):
                has_correct = True
            else:
                previous_lines.append(i)

        return has_correct, previous_lines, lines

    def update_fstab(self, current_fstype):
        has_correct, previous_lines, lines = self.check_fstab_entry()
        changed = False

        for idx in previous_lines:
            lines[idx] = f"# {lines[idx]}"
            changed = True

        if not has_correct:
            new_line = f"{self.lv_device} {self.path} {current_fstype} {self.FSTAB_OPTS} 0 0\n"
            lines.append(new_line)
            changed = True

        if changed:
            with open(self.FILE_FSTAB, 'w') as f:
                f.writelines(lines)

        return changed

    def sync_data(self, default_excludes):
        if not os.path.isdir(self.path):
            os.makedirs(self.path, mode=0o750)
            return True, "created source directory"

        if not os.listdir(self.path):
            return False, "source empty; no sync needed"

        active_excludes = self.excludes if self.excludes is not None else default_excludes

        rsync_cmd = ['rsync', '-aAXH', '--delete', '--exclude=lost+found']
        for pattern in active_excludes:
            rsync_cmd.append(f'--exclude={pattern}')
        rsync_cmd.extend([f"{self.path}/", self.temp_mnt])

        os.makedirs(self.temp_mnt, exist_ok=True)
        try:
            rc, _, err = self.module.run_command(['mount', self.lv_device, self.temp_mnt])
            if rc != 0:
                self.module.fail_json(msg=f"Failed to mount {self.lv_device}: {err}")

            rc, _, err = self.module.run_command(rsync_cmd)
            if rc != 0:
                self.module.fail_json(msg=f"Rsync failed: {err}")

        finally:
            self.module.run_command(['umount', self.temp_mnt])
            if os.path.exists(self.temp_mnt):
                os.rmdir(self.temp_mnt)

        return True, "synced data"

    def validate_current_state(self):
        results = {
            'vg_exists': self.check_vg_exists(),
            'lv_exists': self.check_lv_exists(),
            'fs_type': self.get_fs_type(),
            'fstab_correct': False,
            'fstab_previous_entries': 0,
        }
        if results['lv_exists']:
            has_correct, previous_lines, _ = self.check_fstab_entry()
            results['fstab_correct'] = has_correct
            results['fstab_previous_entries'] = len(previous_lines)
        return results

def main():
    module = AnsibleModule(
        argument_spec=dict(
            device=dict(type='str', required=True),
            vg=dict(type='str', required=True),
            lv=dict(type='str', required=True),
            size=dict(type='str', required=True),
            fstype=dict(type='str', required=True),
            sync=dict(type='bool', required=True),
            path=dict(type='str', required=True),
            excludes=dict(type='list', elements='str', required=False),
        ),
        supports_check_mode=True,
    )

    manager = DedicatedDiskPartition(module)
    state = manager.validate_current_state()

    if not manager.check_block_device():
        module.fail_json(msg=f"{manager.device} is not a valid block device")

    if manager.check_device_in_use():
        module.fail_json(msg=f"{manager.device} is already in use or part of another configuration")

    changed = False
    change_msgs = []
    would_change_msgs = []

    # Ensure VG
    vg_changed = False
    if module.check_mode:
        if not state['vg_exists']:
            vg_changed = True
            would_change_msgs.append("would ensure VG and PV")
    else:
        vg_changed = manager.ensure_vg()
        if vg_changed:
            change_msgs.append("created VG")
    changed |= vg_changed

    # Ensure LV
    lv_created = False
    if not state['lv_exists']:
        if module.check_mode:
            would_change_msgs.append("would create LV")
        else:
            manager.create_lv()
            change_msgs.append("created LV")
        lv_created = True
        changed = True

    # Resize LV if needed
    resize_performed = False
    if state['lv_exists']:
        try:
            requested_bytes = size_to_bytes(manager.size)
            current_bytes = int(manager.get_lv_size())
            if requested_bytes > current_bytes:
                if module.check_mode:
                    would_change_msgs.append("would resize LV and filesystem")
                else:
                    manager.resize_lv()
                    change_msgs.append("resized LV and filesystem")
                resize_performed = True
                changed = True
        except ValueError as e:
            module.fail_json(msg=f"Size comparison failed: {str(e)}")

    # Create filesystem if needed
    fs_created = False
    current_fstype = state['fs_type']
    if lv_created or not current_fstype:
        if module.check_mode:
            would_change_msgs.append("would create filesystem")
        else:
            manager.create_fs()
            change_msgs.append("created filesystem")
        fs_created = True
        current_fstype = manager.fstype
        changed = True

    # Update fstab if needed
    fstab_changed = False
    if state['lv_exists'] or lv_created:
        has_correct, previous_lines, _ = manager.check_fstab_entry()
        previous_entries = len(previous_lines)
        if previous_entries > 0 or not has_correct:
            if module.check_mode:
                would_change_msgs.append("would update fstab")
            else:
                manager.update_fstab(current_fstype)
                if previous_entries > 0:
                    change_msgs.append(f"commented out {previous_entries} previous fstab entries")
                if not has_correct:
                    change_msgs.append("added new fstab entry")
            fstab_changed = True
            changed = True

    # Sync data if needed
    sync_changed = False
    default_excludes_map = {
        '/var': ['log/*', 'tmp/*'],
        '/var/log': ['audit/*']
    }
    default_excludes = default_excludes_map.get(manager.path, [])
    if manager.sync and fs_created:
        if module.check_mode:
            if not os.path.isdir(manager.path) or os.listdir(manager.path):
                would_change_msgs.append("would sync data")
                sync_changed = True
        else:
            sync_changed, sync_msg = manager.sync_data(default_excludes)
            if sync_changed:
                change_msgs.append(sync_msg)
        changed |= sync_changed

    # Determine if reboot is required
    reboot_required = vg_changed or lv_created or fs_created or fstab_changed or sync_changed

    if module.check_mode:
        # In check mode, changed is True if any would_change
        changed = len(would_change_msgs) > 0
        # Reboot required unless only resize
        if changed:
            reboot_required = not (len(would_change_msgs) == 1 and "would resize LV and filesystem" in would_change_msgs)
        msg = "; ".join(change_msgs + would_change_msgs) if changed else "No changes needed"
        module.exit_json(
            changed=changed,
            msg=msg,
            validation_results=state,
            reboot_required=reboot_required
        )

    # Refresh state after changes
    new_state = manager.validate_current_state()

    module.exit_json(
        changed=changed,
        msg="; ".join(change_msgs) if changed else "Configuration matches specification",
        validation_results=new_state,
        reboot_required=reboot_required
    )

if __name__ == "__main__":
    main()
