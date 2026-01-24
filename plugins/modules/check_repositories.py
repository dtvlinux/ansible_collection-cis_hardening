#!/usr/bin/python

# Copyright: (c) 2026, Michael Lucraft @dtvlinux
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r'''
---
module: check_repositories
short_description: Gather and format APT repository metadata for CIS reporting
author:
  - Michael Lucraft (@dtvlinux)
version_added: "1.0.0"
description:
  - "This module executes 'apt-cache policy' to identify all active package manager repositories on the system."
  - "It parses the output to extract the Priority, Repository URL, Release Metadata, and Site Origin for each entry."
  - "The module explicitly excludes the local dpkg status file (/var/lib/dpkg/status) to focus strictly on external package sources as required by CIS 1.2.1.2."
  - "It formats the results into a structured string and appends it to the 'cis_manual_actions' fact for manual audit reporting."
options:
  current_manual_actions:
    description:
      - A list of strings containing existing CIS manual action reports. The CIS roles pass this list using 'ansible_facts["cis_manual_actions"]'.
    required: false
    type: list
    elements: str
    default: []
  update_manual_actions:
    description:
      - Whether to append the findings to the 'cis_manual_actions' fact.
    required: false
    type: bool
    default: true
'''

EXAMPLES = r'''
- name: 1.2.1.2 | Ensure package manager repositories are configured | Manual Actions Report
  dtvlinux.cis_hardening.check_repositories:
    current_manual_actions: "{{ ansible_facts['cis_manual_actions'] | default([]) }}"

- name: Gather repository info without updating manual actions fact
  dtvlinux.cis_hardening.check_repositories:
    update_manual_actions: false
  register: repo_check
'''

RETURN = r'''
---
changed:
  description: Whether the module made changes to the system state. Always false as this is a reporting module.
  type: bool
  returned: always
repositories:
  description: A list of dictionaries containing the parsed repository information.
  type: list
  returned: always
  contains:
    priority:
      description: The APT pinning priority assigned to the repository.
      type: str
    repository:
      description: The full URL and component string of the repository.
      type: str
    release:
      description: The distribution properties (v, o, a, n, l, c, b) from the release line.
      type: str
    origin:
      description: The hostname of the site providing the packages.
      type: str
ansible_facts:
  description: Facts to be set on the managed host.
  type: dict
  returned: when update_manual_actions is true
  contains:
    cis_manual_actions:
      description: An updated list of strings containing formatted CIS manual review blocks.
      type: list
'''

from ansible.module_utils.basic import AnsibleModule
import subprocess
import re

def run_command(cmd):
    try:
        result = subprocess.check_output(['apt-cache', 'policy'], stderr=subprocess.STDOUT)
        return result.decode('utf-8')
    except subprocess.CalledProcessError as e:
        return ""

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
    
    output = run_command('apt-cache policy')
    repos = []
    
    if output:
        lines = output.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i]
            
            if "/var/lib/dpkg/status" in line:
                i += 1
                continue

            # Regex captures: 1=Priority, 2=Repository URL/Details
            match = re.match(r'^\s+(\d+)\s+(http\S+.*Packages)', line)
            if match:
                repo_entry = {
                    'priority': match.group(1),
                    'repository': match.group(2),
                    'release': 'N/A',
                    'origin': 'N/A'
                }

                j = i + 1
                while j < len(lines) and j < i + 3:
                    if 'release' in lines[j]:
                        repo_entry['release'] = lines[j].split('release', 1)[1].strip()
                    elif 'origin' in lines[j]:
                        repo_entry['origin'] = lines[j].split('origin', 1)[1].strip()
                    
                    if re.match(r'^\s+(\d+)\s+(http)', lines[j]):
                        break
                    j += 1
                
                repos.append(repo_entry)
                i = j - 1
            i += 1

    ansible_facts = {}
    if update_manual_actions and repos:
        detailed_msg = (
            "- 1.2.1.2 Ensure package manager repositories are configured:\n"
            "      Found Repositories:\n"
        )
        for repo in repos:
            detailed_msg += (
                f"        - Repository: {repo['repository']}\n"
                f"          Priority: {repo['priority']}\n"
                f"          Release: {repo['release']}\n"
                f"          Origin: {repo['origin']}\n"
            )
        
        updated_actions = current_manual_actions + [detailed_msg.strip()]
        ansible_facts['cis_manual_actions'] = updated_actions

    module.exit_json(
        changed=False,
        repositories=repos,
        ansible_facts=ansible_facts
    )

if __name__ == '__main__':
    main()
