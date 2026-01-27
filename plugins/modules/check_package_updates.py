#!/usr/bin/python

# Copyright: (c) 2026, Michael Lucraft @dtvlinux
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r'''
---
module: check_package_updates
short_description: Check for upgradable packages using apt for CIS auditing
author:
  - Michael Lucraft (@dtvlinux)
version_added: "1.0.0"
description:
  - This module runs apt list --upgradable, parses the output, and extracts information about upgradable packages.
  - It returns the results in a structured list of dictionaries for auditing purposes, such as CIS Ubuntu benchmarks.
  - Optionally, if upgradable packages are found and update_manual_actions is true, it appends a formatted message to the cis_manual_actions fact.
  - No changes are made to the system; this is a read-only audit module.
options:
  update_manual_actions:
    description:
      - Whether to append a detailed message to the cis_manual_actions fact if upgradable packages are found.
    type: bool
    default: true
  current_manual_actions:
    description:
      - The current value of cis_manual_actions to append to (pass via playbook variable).
    type: list
    elements: str
    default: []
'''

EXAMPLES = r'''
- name: Check for upgradable packages
  check_package_updates:
  register: package_update_info

- name: Check and update manual actions fact
  check_package_updates:
    update_manual_actions: true
    current_manual_actions: "{{ cis_manual_actions | default([]) }}"
  changed_when: false
'''

RETURN = r'''
upgradable_packages:
  description: A list of dictionaries containing package names, installed versions, and available versions.
  returned: always
  type: list
  elements: dict
  sample: [
    {
      "package": "azure-cli",
      "installed": "2.81.0-1~noble",
      "available": "2.82.0-1~noble"
    }
  ]
msg:
  description: A message indicating the status of the operation.
  returned: always
  type: str
  sample: "Package update information gathered successfully."
ansible_facts:
  description: Updated facts if update_manual_actions is true and upgradable packages are found (includes cis_manual_actions).
  returned: when update_manual_actions is true
  type: dict
'''

import subprocess
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
            update_manual_actions=dict(type='bool', default=True),
            current_manual_actions=dict(type='list', default=[], elements='str'),
        ),
        supports_check_mode=True
    )

    update_manual_actions = module.params['update_manual_actions']
    current_manual_actions = module.params['current_manual_actions']
    upgradable_packages = []
    msg = "Package update information gathered successfully."
    ansible_facts = {}

    cmd = "apt list --upgradable 2>/dev/null"
    output = run_command(cmd)
    lines = output.splitlines()

    for line in lines[1:]:
        if not line.strip():
            continue
        if '[upgradable from:' not in line:
            continue

        parts = line.split('[upgradable from:')
        if len(parts) != 2:
            continue

        main_part = parts[0].strip()
        installed = parts[1].strip().rstrip(']')

        subparts = main_part.split()
        if len(subparts) < 3:
            continue

        package_repo = subparts[0]
        available = subparts[1]
        package = package_repo.split('/')[0]

        upgradable_packages.append({
            'package': package,
            'installed': installed,
            'available': available
        })

    if not upgradable_packages:
        msg = "No upgradable packages found."

    if update_manual_actions and upgradable_packages:
        detailed_msg = (
            "- 1.2.2.1 Ensure updates, patches, and additional security software "
            "are installed:\n"
            "      Upgradable packages:\n"
        )
        for pkg in upgradable_packages:
            detailed_msg += (
                f"        - Package: {pkg['package']}\n"
                f"          Installed: {pkg['installed']}\n"
                f"          Available: {pkg['available']}\n"
            )
        updated_actions = current_manual_actions + [detailed_msg.strip()]
        ansible_facts['cis_manual_actions'] = updated_actions
        msg = "Manual actions updated with package update details."

    module.exit_json(changed=False, upgradable_packages=upgradable_packages, msg=msg, ansible_facts=ansible_facts)

if __name__ == '__main__':
    main()
