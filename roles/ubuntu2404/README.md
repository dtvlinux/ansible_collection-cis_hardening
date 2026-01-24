<!-- DOCSIBLE START -->

# 📃 Role overview

## ubuntu2404



Description: System hardening tasks for security

| Field                | Value           |
|--------------------- |-----------------|
| Readme update        | 2026/01/22 |








### Defaults

**These are static variables with lower priority**

#### File: defaults/main.yml

| Var          | Type         | Value       |
|--------------|--------------|-------------|
| [cis_ubuntu2404_profile](defaults/main.yml#L3)   | str | `level_1_server` |    
| [cis_ubuntu2404_reboot](defaults/main.yml#L6)   | bool | `True` |    
| [cis_ubuntu2404_cramfs_apply](defaults/main.yml#L18)   | bool | `True` |    
| [cis_ubuntu2404_cramfs_conf](defaults/main.yml#L19)   | str | `/etc/modprobe.d/cis_cramfs.conf` |    
| [cis_ubuntu2404_freevxfs_apply](defaults/main.yml#L22)   | bool | `True` |    
| [cis_ubuntu2404_freevxfs_conf](defaults/main.yml#L23)   | str | `/etc/modprobe.d/cis_freevxfs.conf` |    
| [cis_ubuntu2404_hfs_apply](defaults/main.yml#L26)   | bool | `True` |    
| [cis_ubuntu2404_hfs_conf](defaults/main.yml#L27)   | str | `/etc/modprobe.d/cis_hfs.conf` |    
| [cis_ubuntu2404_hfsplus_apply](defaults/main.yml#L30)   | bool | `True` |    
| [cis_ubuntu2404_hfsplus_conf](defaults/main.yml#L31)   | str | `/etc/modprobe.d/cis_hfsplus.conf` |    
| [cis_ubuntu2404_jffs2_apply](defaults/main.yml#L34)   | bool | `True` |    
| [cis_ubuntu2404_jffs2_conf](defaults/main.yml#L35)   | str | `/etc/modprobe.d/cis_jffs2.conf` |    
| [cis_ubuntu2404_overlayfs_apply](defaults/main.yml#L38)   | str | `{{ true if cis_ubuntu2404_profile in ['level_2_server', 'level_2_workstation'] else false }}` |    
| [cis_ubuntu2404_overlayfs_conf](defaults/main.yml#L39)   | str | `/etc/modprobe.d/cis_overlayfs.conf` |    
| [cis_ubuntu2404_squashfs_apply](defaults/main.yml#L42)   | str | `{{ true if cis_ubuntu2404_profile in ['level_2_server', 'level_2_workstation'] else false }}` |    
| [cis_ubuntu2404_squashfs_conf](defaults/main.yml#L43)   | str | `/etc/modprobe.d/cis_squashfs.conf` |    
| [cis_ubuntu2404_udf_apply](defaults/main.yml#L46)   | str | `{{ true if cis_ubuntu2404_profile in ['level_2_server', 'level_2_workstation'] else false }}` |    
| [cis_ubuntu2404_udf_conf](defaults/main.yml#L47)   | str | `/etc/modprobe.d/cis_udf.conf` |    
| [cis_ubuntu2404_usb_storage_apply](defaults/main.yml#L50)   | str | `{{ true if cis_ubuntu2404_profile != 'level_1_workstation' else false }}` |    
| [cis_ubuntu2404_usb_storage_conf](defaults/main.yml#L51)   | str | `/etc/modprobe.d/cis_usb_storage.conf` |    
| [cis_ubuntu2404_unused_filesystems_apply](defaults/main.yml#L54)   | bool | `False` |    
| [cis_ubuntu2404_unused_filesystems_conf](defaults/main.yml#L55)   | str | `/etc/modprobe.d/cis_unused_filesystems.conf` |    
| [cis_ubuntu2404_unused_filesystems_afs](defaults/main.yml#L56)   | bool | `False` |    
| [cis_ubuntu2404_unused_filesystems_ceph](defaults/main.yml#L57)   | bool | `False` |    
| [cis_ubuntu2404_unused_filesystems_exfat](defaults/main.yml#L58)   | bool | `False` |    
| [cis_ubuntu2404_unused_filesystems_ext](defaults/main.yml#L59)   | bool | `False` |    
| [cis_ubuntu2404_unused_filesystems_fat](defaults/main.yml#L60)   | bool | `False` |    
| [cis_ubuntu2404_unused_filesystems_fscache](defaults/main.yml#L61)   | bool | `False` |    
| [cis_ubuntu2404_unused_filesystems_fuse](defaults/main.yml#L62)   | bool | `False` |    
| [cis_ubuntu2404_unused_filesystems_gfs2](defaults/main.yml#L63)   | bool | `False` |    
| [cis_ubuntu2404_unused_filesystems_nfs_common](defaults/main.yml#L64)   | bool | `False` |    
| [cis_ubuntu2404_unused_filesystems_nfsd](defaults/main.yml#L65)   | bool | `False` |    
| [cis_ubuntu2404_unused_filesystems_smbfs_common](defaults/main.yml#L66)   | bool | `False` |    
| [cis_ubuntu2404_dedicated_disk_apply](defaults/main.yml#L89)   | bool | `True` |    
| [cis_ubuntu2404_dedicated_disk_vgname](defaults/main.yml#L98)   | str | `vg_hardening` |    
| [cis_ubuntu2404_dedicated_disk_tmp_apply](defaults/main.yml#L103)   | bool | `True` |    
| [cis_ubuntu2404_dedicated_disk_tmp_lvol](defaults/main.yml#L104)   | str | `lv_tmp` |    
| [cis_ubuntu2404_dedicated_disk_tmp_type](defaults/main.yml#L105)   | str | `ext4` |    
| [cis_ubuntu2404_dedicated_disk_tmp_size](defaults/main.yml#L106)   | str | `4G` |    
| [cis_ubuntu2404_tmp_nodev_apply](defaults/main.yml#L109)   | bool | `True` |    
| [cis_ubuntu2404_tmp_nosuid_apply](defaults/main.yml#L112)   | bool | `True` |    
| [cis_ubuntu2404_tmp_noexec_apply](defaults/main.yml#L115)   | bool | `True` |    
| [cis_ubuntu2404_dev_shm_apply](defaults/main.yml#L120)   | bool | `True` |    
| [cis_ubuntu2404_dev_shm_nodev_apply](defaults/main.yml#L123)   | bool | `True` |    
| [cis_ubuntu2404_dev_shm_nosuid_apply](defaults/main.yml#L126)   | bool | `True` |    
| [cis_ubuntu2404_dev_shm_noexec_apply](defaults/main.yml#L129)   | bool | `True` |    
| [cis_ubuntu2404_dedicated_disk_home_apply](defaults/main.yml#L134)   | str | `{{ true if cis_ubuntu2404_profile in ['level_2_server', 'level_2_workstation'] else false }}` |    
| [cis_ubuntu2404_dedicated_disk_home_lvol](defaults/main.yml#L135)   | str | `lv_home` |    
| [cis_ubuntu2404_dedicated_disk_home_type](defaults/main.yml#L136)   | str | `ext4` |    
| [cis_ubuntu2404_dedicated_disk_home_size](defaults/main.yml#L137)   | str | `2G` |    
| [cis_ubuntu2404_home_nodev_apply](defaults/main.yml#L140)   | bool | `True` |    
| [cis_ubuntu2404_home_nosuid_apply](defaults/main.yml#L143)   | bool | `True` |    
| [cis_ubuntu2404_dedicated_disk_var_apply](defaults/main.yml#L148)   | str | `{{ true if cis_ubuntu2404_profile in ['level_2_server', 'level_2_workstation'] else false }}` |    
| [cis_ubuntu2404_dedicated_disk_var_lvol](defaults/main.yml#L149)   | str | `lv_var` |    
| [cis_ubuntu2404_dedicated_disk_var_type](defaults/main.yml#L150)   | str | `ext4` |    
| [cis_ubuntu2404_dedicated_disk_var_size](defaults/main.yml#L151)   | str | `8G` |    
| [cis_ubuntu2404_var_nodev_apply](defaults/main.yml#L154)   | bool | `True` |    
| [cis_ubuntu2404_var_nosuid_apply](defaults/main.yml#L157)   | bool | `True` |    
| [cis_ubuntu2404_dedicated_disk_var_tmp_apply](defaults/main.yml#L162)   | str | `{{ true if cis_ubuntu2404_profile in ['level_2_server', 'level_2_workstation'] else false }}` |    
| [cis_ubuntu2404_dedicated_disk_var_tmp_lvol](defaults/main.yml#L163)   | str | `lv_var_tmp` |    
| [cis_ubuntu2404_dedicated_disk_var_tmp_type](defaults/main.yml#L164)   | str | `ext4` |    
| [cis_ubuntu2404_dedicated_disk_var_tmp_size](defaults/main.yml#L165)   | str | `2G` |    
| [cis_ubuntu2404_var_tmp_nodev_apply](defaults/main.yml#L168)   | bool | `True` |    
| [cis_ubuntu2404_var_tmp_nosuid_apply](defaults/main.yml#L171)   | bool | `True` |    
| [cis_ubuntu2404_var_tmp_noexec_apply](defaults/main.yml#L174)   | bool | `True` |    
| [cis_ubuntu2404_dedicated_disk_var_log_apply](defaults/main.yml#L179)   | str | `{{ true if cis_ubuntu2404_profile in ['level_2_server', 'level_2_workstation'] else false }}` |    
| [cis_ubuntu2404_dedicated_disk_var_log_lvol](defaults/main.yml#L180)   | str | `lv_var_log` |    
| [cis_ubuntu2404_dedicated_disk_var_log_type](defaults/main.yml#L181)   | str | `ext4` |    
| [cis_ubuntu2404_dedicated_disk_var_log_size](defaults/main.yml#L182)   | str | `4G` |    
| [cis_ubuntu2404_var_log_nodev_apply](defaults/main.yml#L185)   | bool | `True` |    
| [cis_ubuntu2404_var_log_nosuid_apply](defaults/main.yml#L188)   | bool | `True` |    
| [cis_ubuntu2404_var_log_noexec_apply](defaults/main.yml#L191)   | bool | `True` |    
| [cis_ubuntu2404_dedicated_disk_var_log_audit_apply](defaults/main.yml#L196)   | str | `{{ true if cis_ubuntu2404_profile in ['level_2_server', 'level_2_workstation'] else false }}` |    
| [cis_ubuntu2404_dedicated_disk_var_log_audit_lvol](defaults/main.yml#L197)   | str | `lv_var_log_audit` |    
| [cis_ubuntu2404_dedicated_disk_var_log_audit_type](defaults/main.yml#L198)   | str | `ext4` |    
| [cis_ubuntu2404_dedicated_disk_var_log_audit_size](defaults/main.yml#L199)   | str | `4G` |    
| [cis_ubuntu2404_var_log_audit_nodev_apply](defaults/main.yml#L202)   | bool | `True` |    
| [cis_ubuntu2404_var_log_audit_nosuid_apply](defaults/main.yml#L205)   | bool | `True` |    
| [cis_ubuntu2404_var_log_audit_noexec_apply](defaults/main.yml#L208)   | bool | `True` |    
| [cis_ubuntu2404_gpg_key_check_report](defaults/main.yml#L217)   | bool | `True` |    
| [cis_ubuntu2404_repositories_check_report](defaults/main.yml#L220)   | bool | `True` |    


### Vars

**These are variables with higher priority**
#### File: vars/main.yml

| Var          | Type         | Value       |
|--------------|--------------|-------------|
| [cis_ubuntu2404_unused_filesystems_module_list](vars/main.yml#L3)   | str | `<multiline value: folded_strip>` |    
| [cis_ubuntu2404_partitions](vars/main.yml#L15)   | list | `[]` |    
| [cis_ubuntu2404_partitions.**0**](vars/main.yml#L15)   | dict | `{}` |    
| [cis_ubuntu2404_partitions.0.**apply**](vars/main.yml#L16)   | str | `{{ cis_ubuntu2404_dedicated_disk_tmp_apply }}` |    
| [cis_ubuntu2404_partitions.0.**size**](vars/main.yml#L16)   | str | `{{ cis_ubuntu2404_dedicated_disk_tmp_size }}` |    
| [cis_ubuntu2404_partitions.**1**](vars/main.yml#L16)   | dict | `{}` |    
| [cis_ubuntu2404_partitions.1.**apply**](vars/main.yml#L16)   | str | `{{ cis_ubuntu2404_dedicated_disk_home_apply }}` |    
| [cis_ubuntu2404_partitions.1.**size**](vars/main.yml#L16)   | str | `{{ cis_ubuntu2404_dedicated_disk_home_size }}` |    
| [cis_ubuntu2404_partitions.**2**](vars/main.yml#L16)   | dict | `{}` |    
| [cis_ubuntu2404_partitions.2.**apply**](vars/main.yml#L16)   | str | `{{ cis_ubuntu2404_dedicated_disk_var_apply }}` |    
| [cis_ubuntu2404_partitions.2.**size**](vars/main.yml#L16)   | str | `{{ cis_ubuntu2404_dedicated_disk_var_size }}` |    
| [cis_ubuntu2404_partitions.**3**](vars/main.yml#L16)   | dict | `{}` |    
| [cis_ubuntu2404_partitions.3.**apply**](vars/main.yml#L16)   | str | `{{ cis_ubuntu2404_dedicated_disk_var_tmp_apply }}` |    
| [cis_ubuntu2404_partitions.3.**size**](vars/main.yml#L16)   | str | `{{ cis_ubuntu2404_dedicated_disk_var_tmp_size }}` |    
| [cis_ubuntu2404_partitions.**4**](vars/main.yml#L16)   | dict | `{}` |    
| [cis_ubuntu2404_partitions.4.**apply**](vars/main.yml#L16)   | str | `{{ cis_ubuntu2404_dedicated_disk_var_log_apply }}` |    
| [cis_ubuntu2404_partitions.4.**size**](vars/main.yml#L16)   | str | `{{ cis_ubuntu2404_dedicated_disk_var_log_size }}` |    
| [cis_ubuntu2404_partitions.**5**](vars/main.yml#L16)   | dict | `{}` |    
| [cis_ubuntu2404_partitions.5.**apply**](vars/main.yml#L16)   | str | `{{ cis_ubuntu2404_dedicated_disk_var_log_audit_apply }}` |    
| [cis_ubuntu2404_partitions.5.**size**](vars/main.yml#L16)   | str | `{{ cis_ubuntu2404_dedicated_disk_var_log_audit_size }}` |    
| [cis_ubuntu2404_required_bytes](vars/main.yml#L23)   | str | `<multiline value: folded_strip>` |    


### Tasks


#### File: tasks/1_initial_setup/1_1_filesystem/1_1_1_kernel_modules/main.yml

| Name | Module | Has Conditions | Tags |
| ---- | ------ | -------------- | -----|
| 1.1.1.1 ¦ Ensure cramfs kernel module is not available | dtvlinux.cis_hardening.disable_modules | True |  |
| 1.1.1.2 ¦ Ensure freevxfs kernel module is not available | dtvlinux.cis_hardening.disable_modules | True |  |
| 1.1.1.3 ¦ Ensure hfs kernel module is not available | dtvlinux.cis_hardening.disable_modules | True |  |
| 1.1.1.4 ¦ Ensure hfsplus kernel module is not available | dtvlinux.cis_hardening.disable_modules | True |  |
| 1.1.1.5 ¦ Ensure jffs2 kernel module is not available | dtvlinux.cis_hardening.disable_modules | True |  |
| 1.1.1.6 ¦ Ensure overlayfs kernel module is not available | dtvlinux.cis_hardening.disable_modules | True |  |
| 1.1.1.7 ¦ Ensure squashfs kernel module is not available | dtvlinux.cis_hardening.disable_modules | True |  |
| 1.1.1.8 ¦ Ensure udf kernel module is not available | dtvlinux.cis_hardening.disable_modules | True |  |
| 1.1.1.9 ¦ Ensure usb-storage kernel module is not available | dtvlinux.cis_hardening.disable_modules | True |  |
| 1.1.1.10 ¦ Ensure unused_filesystems kernel modules are not available | dtvlinux.cis_hardening.disable_modules | True |  |

#### File: tasks/1_initial_setup/1_1_filesystem/1_1_2_partitions/1_1_2_1_configure_tmp.yml

| Name | Module | Has Conditions | Tags |
| ---- | ------ | -------------- | -----|
| 1.1.2.1.1 ¦ Ensure /tmp is a separate partition | dtvlinux.cis_hardening.dedicated_disk_partition | False |  |
| 1.1.2.1.x ¦ Configure /tmp ¦ Task block | block | True |  |
| 1.1.2.1.2 ¦ Ensure nodev option set on /tmp partition | ansible.posix.mount | True |  |
| 1.1.2.1.3 ¦ Ensure nosuid option set on /tmp partition | ansible.posix.mount | True |  |
| 1.1.2.1.4 ¦ Ensure noexec option set on /tmp partition | ansible.posix.mount | True |  |

#### File: tasks/1_initial_setup/1_1_filesystem/1_1_2_partitions/1_1_2_2_configure_dev_shm.yml

| Name | Module | Has Conditions | Tags |
| ---- | ------ | -------------- | -----|
| 1.1.2.2.1 ¦ Ensure /dev/shm is a separate partition ¦ Task block | block | False |  |
| 1.1.2.2.1 ¦ Ensure /dev/shm is a separate partition ¦ Gather /dev/shm mount info | ansible.builtin.shell | False |  |
| 1.1.2.2.1 ¦ Ensure /dev/shm is a separate partition ¦ Mount | ansible.posix.mount | False |  |
| 1.1.2.2.x ¦ Ensure option set on /dev/shm ¦ Task block | block | True |  |
| 1.1.2.2.2 ¦ Ensure nodev option set on /dev/shm partition | ansible.builtin.replace | True |  |
| 1.1.2.2.3 ¦ Ensure nosuid option set on /dev/shm partition | ansible.builtin.replace | True |  |
| 1.1.2.2.4 ¦ Ensure noexec option set on /dev/shm partition | ansible.builtin.replace | True |  |

#### File: tasks/1_initial_setup/1_1_filesystem/1_1_2_partitions/1_1_2_3_configure_home.yml

| Name | Module | Has Conditions | Tags |
| ---- | ------ | -------------- | -----|
| 1.1.2.3.1 ¦ Ensure /home is a separate partition | dtvlinux.cis_hardening.dedicated_disk_partition | False |  |
| 1.1.2.3.x ¦ Configure /home ¦ Task block | block | True |  |
| 1.1.2.3.2 ¦ Ensure nodev option set on /home partition | ansible.posix.mount | True |  |
| 1.1.2.3.3 ¦ Ensure nosuid option set on /home partition | ansible.posix.mount | True |  |

#### File: tasks/1_initial_setup/1_1_filesystem/1_1_2_partitions/1_1_2_4_configure_var.yml

| Name | Module | Has Conditions | Tags |
| ---- | ------ | -------------- | -----|
| 1.1.2.4.1 ¦ Ensure /var is a separate partition | dtvlinux.cis_hardening.dedicated_disk_partition | False |  |
| 1.1.2.4.x ¦ Configure /var ¦ Task block | block | True |  |
| 1.1.2.4.2 ¦ Ensure nodev option set on /var partition | ansible.posix.mount | True |  |
| 1.1.2.4.3 ¦ Ensure nosuid option set on /var partition | ansible.posix.mount | True |  |

#### File: tasks/1_initial_setup/1_1_filesystem/1_1_2_partitions/1_1_2_5_configure_var_tmp.yml

| Name | Module | Has Conditions | Tags |
| ---- | ------ | -------------- | -----|
| 1.1.2.5.1 ¦ Ensure /var/tmp is a separate partition | dtvlinux.cis_hardening.dedicated_disk_partition | False |  |
| 1.1.2.5.x ¦ Configure /var/tmp ¦ Task block | block | True |  |
| 1.1.2.5.2 ¦ Ensure nodev option set on /var/tmp partition | ansible.posix.mount | True |  |
| 1.1.2.5.3 ¦ Ensure nosuid option set on /var/tmp partition | ansible.posix.mount | True |  |
| 1.1.2.5.4 ¦ Ensure noexec option set on /var/tmp partition | ansible.posix.mount | True |  |

#### File: tasks/1_initial_setup/1_1_filesystem/1_1_2_partitions/1_1_2_6_configure_var_log.yml

| Name | Module | Has Conditions | Tags |
| ---- | ------ | -------------- | -----|
| 1.1.2.6.1 ¦ Ensure /var/log is a separate partition | dtvlinux.cis_hardening.dedicated_disk_partition | False |  |
| 1.1.2.6.x ¦ Configure /var/log ¦ Task block | block | True |  |
| 1.1.2.6.2 ¦ Ensure nodev option set on /var/log partition | ansible.posix.mount | True |  |
| 1.1.2.6.3 ¦ Ensure nosuid option set on /var/log partition | ansible.posix.mount | True |  |
| 1.1.2.6.4 ¦ Ensure noexec option set on /var/log partition | ansible.posix.mount | True |  |

#### File: tasks/1_initial_setup/1_1_filesystem/1_1_2_partitions/1_1_2_7_configure_var_log_audit.yml

| Name | Module | Has Conditions | Tags |
| ---- | ------ | -------------- | -----|
| 1.1.2.7.1 ¦ Ensure /var/log/audit is a separate partition | dtvlinux.cis_hardening.dedicated_disk_partition | False |  |
| 1.1.2.7.x ¦ Configure /var/log/audit ¦ Task block | block | True |  |
| 1.1.2.7.2 ¦ Ensure nodev option set on /var/log/audit partition | ansible.posix.mount | True |  |
| 1.1.2.7.3 ¦ Ensure nosuid option set on /var/log/audit partition | ansible.posix.mount | True |  |
| 1.1.2.7.4 ¦ Ensure noexec option set on /var/log/audit partition | ansible.posix.mount | True |  |

#### File: tasks/1_initial_setup/1_1_filesystem/1_1_2_partitions/main.yml

| Name | Module | Has Conditions | Tags |
| ---- | ------ | -------------- | -----|
| 1.1.2 ¦ Configure filesystem partitions ¦ Dedicated disk checks | block | True |  |
| 1.1.2 ¦ Configure filesystem partitions ¦ Resolve device real name | ansible.builtin.shell | False |  |
| 1.1.2 ¦ Configure filesystem partitions ¦ Dedicated disk check | ansible.builtin.set_fact | False |  |
| 1.1.2.2 ¦ Configure /dev/shm | ansible.builtin.include_tasks | True |  |
| 1.1.2 ¦ Configure filesystem partitions | block | True |  |
| 1.1.2.1 ¦ Configure /tmp | ansible.builtin.include_tasks | True |  |
| 1.1.2.3 ¦ Configure /home | ansible.builtin.include_tasks | True |  |
| 1.1.2.4 ¦ Configure /var | ansible.builtin.include_tasks | True |  |
| 1.1.2.5 ¦ Configure /var/tmp | ansible.builtin.include_tasks | True |  |
| 1.1.2.6 ¦ Configure /var/log | ansible.builtin.include_tasks | True |  |
| 1.1.2.7 ¦ Configure /var/log/audit | ansible.builtin.include_tasks | True |  |

#### File: tasks/1_initial_setup/1_1_filesystem/main.yml

| Name | Module | Has Conditions |
| ---- | ------ | -------------- |
| 1.1.1 ¦ Configure filesystem kernel modules ¦ Import tasks | ansible.builtin.import_tasks | False |
| 1.1.1 ¦ Configure filesystem kernel modules ¦ Import tasks | ansible.builtin.import_tasks | False |

#### File: tasks/1_initial_setup/1_2_package_management/1_2_1_package_repos/main.yml

| Name | Module | Has Conditions | Tags |
| ---- | ------ | -------------- | -----|
| 1.2.1.1 ¦ Ensure GPG keys are configured ¦ Manual Actions Report | dtvlinux.cis_hardening.check_gpg_keys | True |  |
| 1.2.1.2 ¦ Ensure package manager repositories are configured ¦ Manual Actions Report | dtvlinux.cis_hardening.check_repositories | True |  |

#### File: tasks/1_initial_setup/1_2_package_management/main.yml

| Name | Module | Has Conditions |
| ---- | ------ | -------------- |
| 1.2.1 ¦ Configure Package Repositories ¦ Import tasks | ansible.builtin.import_tasks | False |

#### File: tasks/1_initial_setup/main.yml

| Name | Module | Has Conditions |
| ---- | ------ | -------------- |
| 1.1 ¦ Filesystem ¦ Import tasks | ansible.builtin.import_tasks | False |
| 1.2 ¦ Package management ¦ Import tasks | ansible.builtin.import_tasks | False |

#### File: tasks/main.yml

| Name | Module | Has Conditions | Tags |
| ---- | ------ | -------------- | -----|
| Import tasks for role | block | True | c,i,s,_,u,b,u,n,t,u,2,4,0,4 |
| 1 ¦ Initial setup ¦ Import tasks | ansible.builtin.import_tasks | False |  |
| Flush handlers | ansible.builtin.meta | False |  |







## Author Information
dtvlinux

#### License

GNU General Public License v3.0 or later

#### Minimum Ansible Version

2.16.0

#### Platforms

- **Ubuntu**: ['noble']


#### Dependencies

No dependencies specified.
<!-- DOCSIBLE END -->
