#!/usr/bin/python

# Copyright: (c) 2026, Michael Lucraft @dtvlinux
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r'''
---
module: dedicated_disk_partition
short_description: Manage LVM partitions and migrate filesystem data
author:
  - Michael Lucraft (@dtvlinux)
version_added: "2.0.0"
description:
  - "This module ensures a dedicated LVM partition exists for a specific path and synchronizes existing data to it."
  - "It manages the full lifecycle: creating PVs, VGs, and LVs; formatting the filesystem; and updating /etc/fstab."
  - "If 'sync' is enabled, data from the source path is moved to the new device via a temporary mount point."
  - "Designed for CIS hardening to move directories like /var, /var/log, or /home onto dedicated partitions."
  - "Automatically handles LVM resizing if the target size differs from the current size."
options:
  path:
    description:
      - The target mount point and source directory path (e.g., /var).
    required: true
    type: str
  device:
    description:
      - The underlying block device to use for the LVM Physical Volume (e.g., /dev/sdb).
    required: true
    type: str
  vg:
    description:
      - The Name of the Volume Group to create or use.
    required: true
    type: str
  lv:
    description:
      - The Name of the Logical Volume to create or use.
    required: true
    type: str
  size:
    description:
      - The desired size of the Logical Volume (e.g., 10G, 500M).
    required: true
    type: str
  fstype:
    description:
      - The filesystem type to format the LV with.
    default: ext4
    type: str
  sync:
    description:
      - Whether to synchronize existing data from the path to the new device.
    default: true
    type: bool
  excludes:
    description:
      - "A list of rsync-style exclude patterns used during the data migration phase."
      - "If omitted, the module applies internal defaults based on the 'path' parameter."
      - "Defaults for '/var': ['log/*', 'tmp/*']."
      - "Defaults for '/var/log': ['audit/*']."
      - "Setting this to an empty list [] overrides all defaults and forces a full sync (except for 'lost+found' which is applied in addition to defaults or user-provided excludes."
    required: false
    type: list
    elements: str
'''

EXAMPLES = r'''
- name: Harden /var by moving it to a dedicated 10GB LVM partition
  dtvlinux.cis_hardening.filesystem_sync:
    path: /var
    device: /dev/sdb
    vg: vg_data
    lv: lv_var
    size: 10G
    fstype: xfs
    sync: true

- name: Create a new partition for /home without syncing data
  dtvlinux.cis_hardening.filesystem_sync:
    path: /home
    device: /dev/sdc
    vg: vg_home
    lv: lv_home
    size: 20G
    sync: false

- name: Ensure /var is on a specific LV with excludes
  dtvlinux.cis_hardening.filesystem_sync:
    path: /var
    device: /dev/sdd
    vg: vg_audit
    lv: lv_audit
    size: 5G
    excludes:
      - "log/*"
'''

RETURN = r'''
---
changed:
  description: Whether any changes were made (LVM creation, FS formatting, or data sync).
  type: bool
  returned: always
msg:
  description: Summary of the operations performed.
  type: str
  returned: always
reboot_required:
  description: Whether a reboot is required to complete the migration
  type: bool
  returned: always
details:
  description: Specific details about LVM and Sync actions.
  type: dict
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
        rc, out, err = self.module.run_command(['pvs', '--noheadings', '-o', 'vg_name', self.device])
        if rc == 0:
            vg_name = out.strip()
            if vg_name and vg_name != self.vg:
                return True
            return False

        rc, out, err = self.module.run_command(['blkid', '-s', 'TYPE', '-o', 'value', self.device])
        if rc == 0 and out.strip():
            return True

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
            return False
        self.module.run_command(['pvcreate', self.device], check_rc=True)
        return True

    def check_vg_exists(self):
        rc, _, _ = self.module.run_command(['vgs', self.vg])
        return rc == 0

    def ensure_vg(self):
        changed = False
        if not self.check_vg_exists():
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
        always_excludes = ['lost+found/']

        rsync_cmd = ['rsync', '-aAXH', '--delete']
        for pattern in always_excludes:
            rsync_cmd.append(f'--exclude={pattern}')
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
            fstype=dict(type='str', required=False, default='ext4'),
            sync=dict(type='bool', required=False, default=True),
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

    lv_created = False
    if not state['lv_exists']:
        if module.check_mode:
            would_change_msgs.append("would create LV")
        else:
            manager.create_lv()
            change_msgs.append("created LV")
        lv_created = True
        changed = True

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
                changed = True
        except ValueError as e:
            module.fail_json(msg=f"Size comparison failed: {str(e)}")

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

    reboot_required = vg_changed or lv_created or fs_created or fstab_changed or sync_changed

    if module.check_mode:
        changed = len(would_change_msgs) > 0
        if changed:
            reboot_required = not (len(would_change_msgs) == 1 and "would resize LV and filesystem" in would_change_msgs)
        msg = "; ".join(change_msgs + would_change_msgs) if changed else "No changes needed"
        module.exit_json(
            changed=changed,
            msg=msg,
            validation_results=state,
            reboot_required=reboot_required
        )

    new_state = manager.validate_current_state()

    module.exit_json(
        changed=changed,
        msg="; ".join(change_msgs) if changed else "Configuration matches specification",
        validation_results=new_state,
        reboot_required=reboot_required
    )

if __name__ == "__main__":
    main()
