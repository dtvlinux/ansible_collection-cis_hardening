#!/usr/bin/python

# Copyright: (c) 2026, Michael Lucraft @dtvlinux
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r'''
---
module: check_gpg_keys
short_description: Gather GPG key information from APT trusted directories for CIS auditing
author:
  - Michael Lucraft (@dtvlinux)
version_added: "1.0.0"
description:
  - This module scans specified directories for GPG and ASC files, extracts key IDs and Signed-By information using gpg.
  - It returns the results in a structured list of dictionaries for auditing purposes, such as CIS Ubuntu benchmarks.
  - Optionally, if keys are found and update_manual_actions is true, it appends a formatted message to the cis_manual_actions fact.
  - No changes are made to the system; this is a read-only audit module.
options:
  trusted_gpg_dir:
    description:
      - Directory to scan for trusted GPG/ASC files.
    type: str
    default: /etc/apt/trusted.gpg.d
  sources_list_dir:
    description:
      - Directory to scan for sources list GPG/ASC files.
    type: str
    default: /etc/apt/sources.list.d
  update_manual_actions:
    description:
      - Whether to append a detailed message to the cis_manual_actions fact if keys are found.
    type: bool
    default: false
  current_manual_actions:
    description:
      - The current value of cis_manual_actions to append to (pass via playbook variable).
    type: list
    elements: str
    default: []
requirements:
  - gpg (command-line tool must be installed on the target host)
  - awk (for parsing output)
'''

EXAMPLES = r'''
- name: Gather GPG key information
  check_gpg_keys:
    trusted_gpg_dir: /etc/apt/trusted.gpg.d
    sources_list_dir: /etc/apt/sources.list.d
  register: gpg_key_info

- name: Gather and update manual actions fact
  check_gpg_keys:
    update_manual_actions: true
    current_manual_actions: "{{ cis_manual_actions | default([]) }}"
  changed_when: false
'''

RETURN = r'''
keys:
  description: A list of dictionaries containing file paths and their extracted key IDs and Signed-By values.
  returned: always
  type: list
  elements: dict
  sample: [
    {
      "file": "/etc/apt/trusted.gpg.d/ubuntu-keyring-2012-cdimage.gpg",
      "keyids": ["D94AA3F0EFE21092"],
      "signed_by": []
    }
  ]
msg:
  description: A message indicating the status of the operation.
  returned: always
  type: str
  sample: "GPG key information gathered successfully."
ansible_facts:
  description: Updated facts if update_manual_actions is true and keys are found (includes cis_manual_actions).
  returned: when update_manual_actions is true
  type: dict
'''

import os
import subprocess
import glob
from ansible.module_utils.basic import AnsibleModule

def run_command(cmd):
    try:
        result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        return result.decode('utf-8').strip()
    except subprocess.CalledProcessError as e:
        return e.output.decode('utf-8').strip()

def main():
    module = AnsibleModule(
        argument_spec=dict(
            trusted_gpg_dir=dict(type='str', default='/etc/apt/trusted.gpg.d'),
            sources_list_dir=dict(type='str', default='/etc/apt/sources.list.d'),
            update_manual_actions=dict(type='bool', default=True),
            current_manual_actions=dict(type='list', default=[], elements='str'),
        ),
        supports_check_mode=True
    )

    trusted_dir = module.params['trusted_gpg_dir']
    sources_dir = module.params['sources_list_dir']
    update_manual_actions = module.params['update_manual_actions']
    current_manual_actions = module.params['current_manual_actions']
    keys = []
    msg = "GPG key information gathered successfully."
    ansible_facts = {}

    patterns = ['*.gpg', '*.asc']
    dirs = [trusted_dir, sources_dir]

    for d in dirs:
        if not os.path.isdir(d):
            continue

        for pattern in patterns:
            for file_path in glob.glob(os.path.join(d, pattern)):
                if not os.path.isfile(file_path):
                    continue

                keyid_cmd = f'gpg --list-packets "{file_path}" 2>/dev/null | awk \'/keyid/ && !seen[$NF]++ {{print $NF}}\''
                keyids_raw = run_command(keyid_cmd)
                keyids = keyids_raw.splitlines() if keyids_raw else []

                signed_by_cmd = f'gpg --list-packets "{file_path}" 2>/dev/null | awk \'/Signed-By:/ {{print $NF}}\''
                signed_by_raw = run_command(signed_by_cmd)
                signed_by = signed_by_raw.splitlines() if signed_by_raw else []

                keys.append({
                    'file': file_path,
                    'keyids': keyids,
                    'signed_by': signed_by
                })

    if not keys:
        msg = "No GPG files found in the specified directories."

    if update_manual_actions and keys:
        detailed_msg = (
            "- 1.2.1.1 Ensure GPG keys are configured:\n"
            "      Found keys:\n"
        )
        for key in keys:
            detailed_msg += (
                f"        - File: {key['file']}\n"
                f"          Key IDs: {', '.join(key['keyids'])}\n"
            )
            signed_by_str = ', '.join(key['signed_by']) if key['signed_by'] else 'N/A'
            detailed_msg += f"          Signed-By: {signed_by_str}\n"
        updated_actions = current_manual_actions + [detailed_msg.strip()]
        ansible_facts['cis_manual_actions'] = updated_actions
        msg = "Manual actions updated with GPG key details."

    module.exit_json(changed=False, keys=keys, msg=msg, ansible_facts=ansible_facts)

if __name__ == '__main__':
    main()
