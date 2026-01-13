# dtvlinux.cis_hardening.ubuntu2404

> Role in development.

This Ansible role implements CIS benchmarks for Ubuntu 24.04 LTS, based on the official CIS Ubuntu Linux 24.04 LTS Benchmark v1.0.0. Currently, it covers all recommendations in section 1.1 (Filesystem), including kernel module configurations and filesystem partitions using Logical Volume Management (LVM) for dedicated disks where applicable.

## Requirements

- Ubuntu 24.04 LTS.
- Ansible and ansible-core (use the latest available versions for optimal compatibility).
- For dedicated disk partitioning (section 1.1.2), a separate block device must be available if `cis_ubuntu2404_dedicated_disk_apply` is enabled.
- Root privileges (use `become: true` in playbooks).

## Role Variables

All variables are defined in `defaults/main.yml` with their default values. They control the application of CIS rules. Variables are prefixed with `cis_ubuntu2404_` and allow fine-tuning of specific benchmarks. Key variables include:

- `cis_ubuntu2404_profile`: Sets the CIS profile level (e.g., `level_1_server`, `level_2_server`, `level_1_workstation`, `level_2_workstation`). Default: `level_1_server`.
- `cis_ubuntu2404_reboot`: Allows the role to reboot the system if needed (e.g., for partition changes). Default: `true`.

### 1.1.1 - Filesystem Kernel Modules

These variables enable or disable restrictions on specific kernel modules:

- `cis_ubuntu2404_cramfs_apply`: Apply cramfs restriction. Default: `true`.
- `cis_ubuntu2404_cramfs_conf`: Config file path for cramfs. Default: `/etc/modprobe.d/cis_cramfs.conf`.
- `cis_ubuntu2404_freevxfs_apply`: Apply freevxfs restriction. Default: `true`.
- `cis_ubuntu2404_freevxfs_conf`: Config file path for freevxfs. Default: `/etc/modprobe.d/cis_freevxfs.conf`.
- `cis_ubuntu2404_hfs_apply`: Apply hfs restriction. Default: `true`.
- `cis_ubuntu2404_hfs_conf`: Config file path for hfs. Default: `/etc/modprobe.d/cis_hfs.conf`.
- `cis_ubuntu2404_hfsplus_apply`: Apply hfsplus restriction. Default: `true`.
- `cis_ubuntu2404_hfsplus_conf`: Config file path for hfsplus. Default: `/etc/modprobe.d/cis_hfsplus.conf`.
- `cis_ubuntu2404_jffs2_apply`: Apply jffs2 restriction. Default: `true`.
- `cis_ubuntu2404_jffs2_conf`: Config file path for jffs2. Default: `/etc/modprobe.d/cis_jffs2.conf`.
- `cis_ubuntu2404_overlayfs_apply`: Apply overlayfs restriction (Level 2 only). Default: `{{ true if cis_ubuntu2404_profile in ['level_2_server', 'level_2_workstation'] else false }}`.
- `cis_ubuntu2404_overlayfs_conf`: Config file path for overlayfs. Default: `/etc/modprobe.d/cis_overlayfs.conf`.
- `cis_ubuntu2404_squashfs_apply`: Apply squashfs restriction (Level 2 only). Default: `{{ true if cis_ubuntu2404_profile in ['level_2_server', 'level_2_workstation'] else false }}`.
- `cis_ubuntu2404_squashfs_conf`: Config file path for squashfs. Default: `/etc/modprobe.d/cis_squashfs.conf`.
- `cis_ubuntu2404_udf_apply`: Apply udf restriction (Level 2 only). Default: `{{ true if cis_ubuntu2404_profile in ['level_2_server', 'level_2_workstation'] else false }}`.
- `cis_ubuntu2404_udf_conf`: Config file path for udf. Default: `/etc/modprobe.d/cis_udf.conf`.
- `cis_ubuntu2404_usb_storage_apply`: Apply usb-storage restriction (except Level 1 Workstation). Default: `{{ true if cis_ubuntu2404_profile != 'level_1_workstation' else false }}`.
- `cis_ubuntu2404_usb_storage_conf`: Config file path for usb-storage. Default: `/etc/modprobe.d/cis_usb_storage.conf`.
- `cis_ubuntu2404_unused_filesystems_apply`: Apply restrictions for unused filesystems. Default: `false`.
- `cis_ubuntu2404_unused_filesystems_conf`: Config file path for unused filesystems. Default: `/etc/modprobe.d/cis_unused_filesystems.conf`.
- `cis_ubuntu2404_unused_filesystems_afs`: Restrict AFS. Default: `false`.
- `cis_ubuntu2404_unused_filesystems_ceph`: Restrict Ceph. Default: `false`.
- `cis_ubuntu2404_unused_filesystems_exfat`: Restrict exFAT. Default: `false`.
- `cis_ubuntu2404_unused_filesystems_ext`: Restrict ext. Default: `false`.
- `cis_ubuntu2404_unused_filesystems_fat`: Restrict FAT. Default: `false`.
- `cis_ubuntu2404_unused_filesystems_fscache`: Restrict FSCache. Default: `false`.
- `cis_ubuntu2404_unused_filesystems_fuse`: Restrict FUSE. Default: `false`.
- `cis_ubuntu2404_unused_filesystems_gfs2`: Restrict GFS2. Default: `false`.
- `cis_ubuntu2404_unused_filesystems_nfs_common`: Restrict NFS common. Default: `false`.
- `cis_ubuntu2404_unused_filesystems_nfsd`: Restrict NFSD. Default: `false`.
- `cis_ubuntu2404_unused_filesystems_smbfs_common`: Restrict SMBFS common. Default: `false`.

### 1.1.2 - Filesystem Partitions

These variables manage partition creation and mount options using LVM on a dedicated disk:

- `cis_ubuntu2404_dedicated_disk_apply`: Use dedicated disk for partitioning. Default: `true`.
- `cis_ubuntu2404_dedicated_disk_vgname`: Volume group name. Default: `vg_hardening`.

#### /tmp

- `cis_ubuntu2404_dedicated_disk_tmp_apply`: Apply /tmp partition. Default: `true`.
- `cis_ubuntu2404_dedicated_disk_tmp_lvol`: Logical volume name. Default: `lv_tmp`.
- `cis_ubuntu2404_dedicated_disk_tmp_type`: Filesystem type. Default: `ext4`.
- `cis_ubuntu2404_dedicated_disk_tmp_size`: Initial size. Default: `4G`.
- `cis_ubuntu2404_tmp_nodev_apply`: Set nodev option. Default: `true`.
- `cis_ubuntu2404_tmp_nosuid_apply`: Set nosuid option. Default: `true`.
- `cis_ubuntu2404_tmp_noexec_apply`: Set noexec option. Default: `true`.

#### /dev/shm

- `cis_ubuntu2404_dev_shm_apply`: Apply /dev/shm configuration. Default: `true`.
- `cis_ubuntu2404_dev_shm_nodev_apply`: Set nodev option. Default: `true`.
- `cis_ubuntu2404_dev_shm_nosuid_apply`: Set nosuid option. Default: `true`.
- `cis_ubuntu2404_dev_shm_noexec_apply`: Set noexec option. Default: `true`.

#### /home (Level 2 only)

- `cis_ubuntu2404_dedicated_disk_home_apply`: Apply /home partition. Default: `{{ true if cis_ubuntu2404_profile in ['level_2_server', 'level_2_workstation'] else false }}`.
- `cis_ubuntu2404_dedicated_disk_home_lvol`: Logical volume name. Default: `lv_home`.
- `cis_ubuntu2404_dedicated_disk_home_type`: Filesystem type. Default: `ext4`.
- `cis_ubuntu2404_dedicated_disk_home_size`: Initial size. Default: `2G`.
- `cis_ubuntu2404_home_nodev_apply`: Set nodev option. Default: `true`.
- `cis_ubuntu2404_home_nosuid_apply`: Set nosuid option. Default: `true`.

#### /var (Level 2 only)

- `cis_ubuntu2404_dedicated_disk_var_apply`: Apply /var partition. Default: `{{ true if cis_ubuntu2404_profile in ['level_2_server', 'level_2_workstation'] else false }}`.
- `cis_ubuntu2404_dedicated_disk_var_lvol`: Logical volume name. Default: `lv_var`.
- `cis_ubuntu2404_dedicated_disk_var_type`: Filesystem type. Default: `ext4`.
- `cis_ubuntu2404_dedicated_disk_var_size`: Initial size. Default: `8G`.
- `cis_ubuntu2404_var_nodev_apply`: Set nodev option. Default: `true`.
- `cis_ubuntu2404_var_nosuid_apply`: Set nosuid option. Default: `true`.

#### /var/tmp (Level 2 only)

- `cis_ubuntu2404_dedicated_disk_var_tmp_apply`: Apply /var/tmp partition. Default: `{{ true if cis_ubuntu2404_profile in ['level_2_server', 'level_2_workstation'] else false }}`.
- `cis_ubuntu2404_dedicated_disk_var_tmp_lvol`: Logical volume name. Default: `lv_var_tmp`.
- `cis_ubuntu2404_dedicated_disk_var_tmp_type`: Filesystem type. Default: `ext4`.
- `cis_ubuntu2404_dedicated_disk_var_tmp_size`: Initial size. Default: `2G`.
- `cis_ubuntu2404_var_tmp_nodev_apply`: Set nodev option. Default: `true`.
- `cis_ubuntu2404_var_tmp_nosuid_apply`: Set nosuid option. Default: `true`.
- `cis_ubuntu2404_var_tmp_noexec_apply`: Set noexec option. Default: `true`.

#### /var/log (Level 2 only)

- `cis_ubuntu2404_dedicated_disk_var_log_apply`: Apply /var/log partition. Default: `{{ true if cis_ubuntu2404_profile in ['level_2_server', 'level_2_workstation'] else false }}`.
- `cis_ubuntu2404_dedicated_disk_var_log_lvol`: Logical volume name. Default: `lv_var_log`.
- `cis_ubuntu2404_dedicated_disk_var_log_type`: Filesystem type. Default: `ext4`.
- `cis_ubuntu2404_dedicated_disk_var_log_size`: Initial size. Default: `4G`.
- `cis_ubuntu2404_var_log_nodev_apply`: Set nodev option. Default: `true`.
- `cis_ubuntu2404_var_log_nosuid_apply`: Set nosuid option. Default: `true`.
- `cis_ubuntu2404_var_log_noexec_apply`: Set noexec option. Default: `true`.

#### /var/log/audit (Level 2 only)

- `cis_ubuntu2404_dedicated_disk_var_log_audit_apply`: Apply /var/log/audit partition. Default: `{{ true if cis_ubuntu2404_profile in ['level_2_server', 'level_2_workstation'] else false }}`.
- `cis_ubuntu2404_dedicated_disk_var_log_audit_lvol`: Logical volume name. Default: `lv_var_log_audit`.
- `cis_ubuntu2404_dedicated_disk_var_log_audit_type`: Filesystem type. Default: `ext4`.
- `cis_ubuntu2404_dedicated_disk_var_log_audit_size`: Initial size. Default: `4G`.
- `cis_ubuntu2404_var_log_audit_nodev_apply`: Set nodev option. Default: `true`.
- `cis_ubuntu2404_var_log_audit_nosuid_apply`: Set nosuid option. Default: `true`.
- `cis_ubuntu2404_var_log_audit_noexec_apply`: Set noexec option. Default: `true`.

> Partition-related variables trigger LVM setup on a dedicated disk if enabled. Existing data is copied during setup, and changes may require a reboot. For non-dedicated setups, only /dev/shm is managed.

## Dependencies

None (relies on core Ansible modules).

## Example Playbook

```yaml
- name: Include roles
  hosts: all
  become: true
  roles:
    - role: dtvlinux.cis_hardening.ubuntu2404
```

Override variables as needed, e.g., via `vars` or inventory.

## Additional Notes

- **Check Mode**: Fully supported for dry-run testing.
- **Tags**: All tasks are tagged with CIS rule numbers (e.g., `cis_1.1.1.1`), control numbers, implementation groups, and levels (server/workstation).
- **Handlers**: Section 1.1.2 tasks may trigger reboot and remount handlers for partition changes.
- Developed by @dtvlinux. For full collection details, see the parent collection README.
