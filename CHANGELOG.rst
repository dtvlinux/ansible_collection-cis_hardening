=====================================
Dtvlinux.Cis\_Hardening Release Notes
=====================================

.. contents:: Topics

v0.5.0
======

Release Summary
---------------

This release now covers CIS rule 1.2.2.1 (Ensure updates, patches, and additional security software are installed).

Minor Changes
-------------

- Added task for CIS rule 1.2.2.1 (Ensure updates, patches, and additional security software are installed).

New Modules
-----------

- dtvlinux.cis_hardening.check_package_updates - Check for upgradable packages using apt for CIS auditing.

v0.4.0
======

Release Summary
---------------

This release now covers CIS rule 1.2.1.2 (Ensure package manager repositories are configured).

Minor Changes
-------------

- Added task for CIS rule 1.2.1.2 (Ensure package manager repositories are configured).

New Modules
-----------

- dtvlinux.cis_hardening.check_repositories - Gather APT repositories and metadata for CIS auditing.

v0.3.0
======

Release Summary
---------------

This release now covers CIS rule 1.2.1.1 (ensure GPG keys are configured).

Major Changes
-------------

- Added debug task to report on CIS rules that require manual actions.
- Added task for CIS rule 1.2.1.1 (ensure GPG keys are configured).

Minor Changes
-------------

- Moved unattended-upgrades service stop task to handlers so it only stops for reboots. Service no longer set to disabled.

New Modules
-----------

- dtvlinux.cis_hardening.check_gpg_keys - Gather GPG key information from APT trusted directories for CIS auditing.

v0.2.1
======

Release Summary
---------------

Added tagging and amended when clause logic for section 1.1. Filesystem section.

Minor Changes
-------------

- Accommodate check mode better.
- Add tagging to 1.1.2 tasks.
- Remount handlers no longer run after reboot.
- Updated when clause logics to ensure tagged tasks run only when prerequisite task output defined.

v0.2.0
======

Release Summary
---------------

Code refactor to simplify and improve readability of tasks.

Major Changes
-------------

- Code refactoring, better directory layout and file names.
- Filesystem sync module replaced with a module that does all but ensure nodev, nosuid & noexec are present.
- Reboot handler now using a listener and results checks to ensure rebooting only when required.
- Two new filters (current_mount_options and dedicated_disk_size) created to save on repetition or multiple tasks.
- Will now resize lvm online.

New Plugins
-----------

Filter
~~~~~~

- dtvlinux.cis_hardening.current_mount_options - Get current mount options from facts or task results.
- dtvlinux.cis_hardening.dedicated_disk_size - Get the size of a specific disk from ansible_devices.

New Modules
-----------

- dtvlinux.cis_hardening.dedicated_disk_partition - Manage LVM partitions and migrate filesystem data.
- dtvlinux.cis_hardening.disable_modules - Disable filesystem kernel modules.

v0.1.1
======

Release Summary
---------------

Initial deployment covering CIS Ubuntu 24.04 benchmarking topic 1.1 Filesystem.

Major Changes
-------------

- Initial deployment covering CIS Ubuntu 24.04 benchmarking topic 1.1 Filesystem.

New Modules
-----------

- dtvlinux.cis_hardening.disable_modules - Disable filesystem kernel modules.
- dtvlinux.cis_hardening.filesystem_sync - Synchronize filesystem data to a new device or partition.
