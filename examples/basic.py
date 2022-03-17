#!/usr/bin/python

import psutil
import grub_install

rootfs_mnt = None
boot_mnt = None
for m in psutil.disk_partitions():
    if m.mountpoint == "/":
        rootfs_mnt = m
    elif m.mountpoint == "/boot":
        boot_mnt = m

t = grub_install.Target(grub_install.TargetType.MOUNTED_HDD_DEV, grub_install.TargetAccessMode.R, rootfs_mount_point=rootfs_mnt, boot_mount_point=boot_mnt)
print("target-type:        " + str(t.target_type))
print("target-access-mode: " + str(t.target_access_mode))

for pt in grub_install.PlatformType:
    print("target-platform:    %-17s %s" % (pt.value, t.get_platform_install_info(pt)))

s = grub_install.Source("/")
try:
    t.compare_with_source(s)
except grub_install.CompareWithSourceError as e:
    print("different with source: %s" % (e))
