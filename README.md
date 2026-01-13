# DTV Linux CIS Hardening

> This collection is under development as a side project for some fun.

## Description

An Ansible collection that provides automated security hardening for Linux systems, based on official CIS Benchmarks.

## Requirements

- Python:
  - The Python interpreter version must meet Ansible Core's requirements.
- Ansible Core:
  - ansible-core 2.16 or later

## Installation

Before using this collection, you need to install it with the Ansible Galaxy command-line tool:

```shell
ansible-galaxy collection install dtvlinux.cis_hardening
```

You can also include it in a requirements.yml file and install it with ansible-galaxy collection install -r requirements.yml, using the format:

```yaml
collections:
  - name: dtvlinux.cis_hardening
```

If you install any collections from Ansible Galaxy, they will not be upgraded automatically when you upgrade the Ansible package.
To upgrade the collection to the latest available version, run the following command:

```shell
ansible-galaxy collection install dtvlinux.cis_hardening --upgrade
```

You can also install a specific version of the collection, for example, if you need to downgrade when something is broken in the latest version. Use the following syntax to install version 0.2.0:

```shell
ansible-galaxy collection install dtvlinux.cis_hardening:==0.2.0
```

See [using Ansible collections](https://docs.ansible.com/ansible/devel/user_guide/collections_using.html) for more details.

## Use Cases

This collection should be used for anyone wishing to harden systems to improve security posture.

Ideally hardening is performed during the provisioning stage of a system, where there would be no impact to end users. Following the initial run, the systems desired state can then be enforced on your chosen schedule.

The roles and modules in this collection can be used on systems that are in use, but keep in mind that you should:

1. Never deploy this collection to production systems without prior testing against non-production systems.
2. Ensure that multiple teams are involved in said testing to provide feedback on any issues in their areas of responsibility.
3. The above two points is applicable even when updating indiviudal variable values. You must confirm the impact of a change.
4. Always have a working backup, restore and disaster recovery process in place and confirmed as working.

It is worth noting that certain hardening tasks will trigger a system reboot or service restarts, which will impact the availability of a system. These tasks can be toggled on/off via Boolean variables, or by a dedicated reboot variable, so set according to your needs.

## Testing

The following ansible-core versions have been tested with this collection:

- ansible-core 2.20

## Support

This collection is provided on an as-is basis without any warranties, express or implied, and is not officially supported; however, issues logged via GitHub may be reviewed at the maintainer's sole discretion, with no guarantees of resolution, timeliness, or further assistance.

If you found the roles or modules in this collection helpful, please consider showing your support with a [donation](https://buymeacoffee.com/dtvlinux).

## Release Notes and Roadmap

See [changelog](https://github.com/dtvlinux/ansible_collection-cis_hardening/blob/main/CHANGELOG.rst) for more details.

## Related Information

This document was written using the following [template](https://access.redhat.com/articles/7068606).

- [Ansible user guide](https://docs.ansible.com/projects/ansible/devel/user_guide/index.html)
- [Ansible developer guide](https://docs.ansible.com/projects/ansible/devel/dev_guide/index.html)
- [Ansible collections requirements](https://docs.ansible.com/projects/ansible/devel/community/collection_contributors/collection_requirements.html)
- [Ansible community Code of Conduct](https://docs.ansible.com/projects/ansible/devel/community/code_of_conduct.html)
- [The Bullhorn (the Ansible contributor newsletter)](https://docs.ansible.com/projects/ansible/devel/community/communication.html#the-bullhorn)
- [Important announcements for maintainers](https://github.com/ansible-collections/news-for-maintainers)

## License Information

GNU General Public License v3.0 or later.

See [COPYING](https://www.gnu.org/licenses/gpl-3.0.txt) to see the full text.
