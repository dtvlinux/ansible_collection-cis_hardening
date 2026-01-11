=====================================
Dtvlinux.Cis\_Hardening Release Notes
=====================================

.. contents:: Topics

v0.2.0
======

Major Changes
-------------

- Code refactering, better directory layout and file names
- Filesystem sync module replaced with a module that does all but ensure nodev, nosuid & noexec are present.
- Reboot handler now using a listener and results checks to ensure rebooting only when required
- Two new filters (current_mount_options and dedicated_disk_size) created to save on repitition or multiple tasks.
- Will now resize lvm online.

New Modules
-----------

- dtvlinux.cis_hardening.dedicated_disk_partition - Manage LVM partitions and migrate filesystem data.
- dtvlinux.cis_hardening.disable_modules - Disable filesystem kernel modules.

v0.1.1
======

Major Changes
-------------

- Initial deployment covering CIS Ubuntu 24.04 benmarking topic 1.1 Filesystem

New Modules
-----------

- dtvlinux.cis_hardening.disable_modules - Disable filesystem kernel modules.
- dtvlinux.cis_hardening.filesystem_sync - Synchronize filesystem data to a new device or partition.
