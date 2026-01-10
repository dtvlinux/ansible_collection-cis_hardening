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
'''

from ansible.module_utils.basic import AnsibleModule
import os
import stat
import json
import re

class DedicatedDiskPartition:
    FILE_FSTAB = '/etc/fstab'
    FILE_MODE = 0o644
    FILE_UID = 0
    FILE_GID = 0
    FSTAB_OPTS = 'defaults'
    FSTAB_DUMP = 0

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

    def create_lv(self):
        self.module.run_command(['lvcreate', '--yes', '-L', self.size, '-n', self.lv, self.vg], check_rc=True)

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
            fstab_pass = 0 if self.path in ('/tmp', '/var/tmp') else 2
            new_line = f"{self.lv_device} {self.path} {current_fstype} {self.FSTAB_OPTS} {self.FSTAB_DUMP} {fstab_pass}\n"
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
    
    def disable_mount_unit(self):
        unit_name = self.path.strip('/').replace('/', '-') + ".mount"

        changed = False
        rc, _, _ = self.module.run_command(['systemctl', 'disable', unit_name])
        if rc == 0:
            changed = True

        rc_mask, _, _ = self.module.run_command(['systemctl', 'mask', unit_name])
        if rc_mask == 0:
            changed = True
            
        if changed:
            self.module.run_command(['systemctl', 'daemon-reload'])
            
        return changed
    
    def mask_mount_unit(self):
        unit = self.path.lstrip('/').replace('/', '-') + '.mount'
        if not unit:
            return False, None

        rc, out, err = self.module.run_command(['systemctl', 'is-enabled', unit])
        if rc != 0 or out.strip() == 'masked':
            return False, None

        if self.module.check_mode:
            return True, unit

        rc, _, err = self.module.run_command(['systemctl', 'mask', unit])
        if rc != 0:
            self.module.fail_json(msg=f"Failed to mask {unit}: {err}")

        return True, unit

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

    # Always ensure VG includes the device
    vg_changed = False
    if not module.check_mode:
        vg_changed = manager.ensure_vg()
    else:
        would_change_msgs.append("would ensure VG and PV")
    changed |= vg_changed
    if vg_changed:
        change_msgs.append("created VG")

    lv_created = False
    if not state['lv_exists']:
        if not module.check_mode:
            manager.create_lv()
        else:
            would_change_msgs.append("would create LV")
        changed = True
        change_msgs.append("created LV")
        lv_created = True

    fs_created = False
    current_fstype = state['fs_type']
    if lv_created or not current_fstype:
        use_fstype = manager.fstype
        if not module.check_mode:
            manager.create_fs()
        else:
            would_change_msgs.append("would create filesystem")
        changed = True
        change_msgs.append("created filesystem")
        fs_created = True
        current_fstype = use_fstype
    elif current_fstype and state['lv_exists']:
        # Ignore provided fstype, use current
        pass

    fstab_changed = False
    if state['lv_exists'] or lv_created:
        has_correct = state['fstab_correct']
        previous_entries = state['fstab_previous_entries']
        if previous_entries > 0 or not has_correct:
            if not module.check_mode:
                fstab_changed = manager.update_fstab(current_fstype)
            else:
                would_change_msgs.append("would update fstab")
            changed |= fstab_changed
            if fstab_changed:
                if previous_entries > 0:
                    change_msgs.append(f"commented out {previous_entries} previous fstab entries")
                if not has_correct:
                    change_msgs.append("added new fstab entry")

    sync_changed = False
    sync_msg = ''
    default_excludes_map = {
        '/var': ['log/*', 'tmp/*'],
        '/var/log': ['audit/*']
    }
    default_excludes = default_excludes_map.get(manager.path, [])
    if manager.sync and fs_created:
        if not module.check_mode:
            sync_changed, sync_msg = manager.sync_data(default_excludes)
            if sync_changed:
                change_msgs.append(sync_msg)
        else:
            would_change_msgs.append("would sync data")
        changed |= sync_changed

    mask_changed, masked_unit = manager.mask_mount_unit()
    changed |= mask_changed
    if mask_changed and masked_unit:
        if module.check_mode:
            would_change_msgs.append(f"would mask conflicting mount unit {masked_unit}")
        else:
            change_msgs.append(f"masked conflicting mount unit {masked_unit}")

    if module.check_mode:
        module.exit_json(
            changed=changed,
            msg="; ".join(change_msgs + would_change_msgs) if changed else "No changes needed",
            validation_results=state
        )

    # Refresh state after changes
    new_state = manager.validate_current_state()

    module.exit_json(
        changed=changed,
        msg="; ".join(change_msgs) if changed else "Configuration matches specification",
        validation_results=new_state
    )

if __name__ == "__main__":
    main()
