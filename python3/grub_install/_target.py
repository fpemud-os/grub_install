#!/usr/bin/env python3

# Copyright (c) 2020-2021 Fpemud <fpemud@sina.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


import os
import abc
import shutil
import pathlib
import subprocess
from ._util import force_rm, force_mkdir, rmdir_if_empty, mnt_probe
from ._const import TargetType, TargetAccessMode, PlatformType, PlatformInstallInfo
from ._handy import Handy, Grub
from ._source import Source


class Target(abc.ABC):

    def __init__(self, target_type, target_access_mode, **kwargs):
        assert isinstance(target_type, TargetType)
        assert isinstance(target_access_mode, TargetAccessMode)

        self._targetType = target_type
        self._mode = target_access_mode

        # target specific variables
        if self._targetType == TargetType.MOUNTED_HDD_DEV:
            self._rootfsDir = kwargs.get("rootfs_dir", None)
            self._bootDir = kwargs.get("boot_dir", os.path.join(self._rootfsDir, "boot"))
            self._dev = kwargs["dev"]
        elif self._targetType == TargetType.PYCDLIB_OBJ:
            assert self._mode in [TargetAccessMode.R, TargetAccessMode.W]
            self._iso = kwargs.get["obj"]
        elif self._targetType == TargetType.ISO_DIR:
            self._dir = kwargs["dir"]
            self._bootDir = os.path.join(self._dir, "boot")
        else:
            assert False

        # self._platforms
        self._platforms = dict()
        if self._mode in [TargetAccessMode.R, TargetAccessMode.RW]:
            if self._targetType == TargetType.MOUNTED_HDD_DEV:
                _Common.init_platforms(self)
                for pt in self._platforms:
                    # FIXME: detect unbootable item, add extra attributes
                    pass
            elif self._targetType == TargetType.PYCDLIB_OBJ:
                assert False                                                    # FIXME
            elif self._targetType == TargetType.ISO_DIR:
                _Common.init_platforms(self)
                for pt in self._platforms:
                    # FIXME: detect unbootable item, add extra attributes
                    pass
            else:
                assert False

    @property
    def target_type(self):
        return self._targetType

    @property
    def target_access_mode(self):
        return self._mode

    @property
    def platforms(self):
        return self._platforms.keys()

    def get_platform_install_info(self, platform_type):
        assert isinstance(platform_type, PlatformType)
        if platform_type in self._platforms:
            return self._platforms[platform_type]
        else:
            ret = PlatformInstallInfo()
            ret.status = PlatformInstallInfo.Status.NOT_EXIST
            return ret

    def install_platform(self, platform_type, source, **kwargs):
        assert self.get_platform_install_info(platform_type).status != PlatformInstallInfo.Status.BOOTABLE
        assert isinstance(source, Source)

        ret = PlatformInstallInfo()
        ret.status = PlatformInstallInfo.Status.BOOTABLE

        if self._targetType == TargetType.MOUNTED_HDD_DEV:
            _Common.install_platform(self, platform_type, source)
            if platform_type == PlatformType.I386_PC:
                ret.allow_floppy = kwargs.get("allow_floppy", False)
                ret.rs_codes = kwargs.get("rs_codes", True)
                _Bios.install_platform(platform_type, source, self._bootDir, self._dev,
                                       True,                                                # bInstallMbr
                                       False,                                               # bFloppyOrHdd
                                       ret.allow_floppy, ret.rs_codes)
            elif Handy.isPlatformEfi(platform_type):
                _Efi.install_platform(platform_type, source, self._bootDir)
            else:
                assert False
        elif self._targetType == TargetType.PYCDLIB_OBJ:
            # FIXME
            assert False
        elif self._targetType == TargetType.ISO_DIR:
            _Common.install_platform(self, platform_type, source)
            if platform_type == PlatformType.I386_PC:
                ret.allow_floppy = kwargs.get("allow_floppy", False)
                ret.rs_codes = kwargs.get("rs_codes", True)
                _Bios.install_platform(platform_type, source, self._bootDir, self._dev,
                                       False,                                               # bInstallMbr
                                       False,                                               # bFloppyOrHdd
                                       ret.allow_floppy, ret.rs_codes)
            elif Handy.isPlatformEfi(platform_type):
                _Efi.install_platform(platform_type, source, self._bootDir)
            else:
                assert False
        else:
            assert False

        self._platforms[platform_type] = ret

    def remove_platform(self, platform_type):
        assert isinstance(platform_type, PlatformType)
        
        if self._targetType == TargetType.MOUNTED_HDD_DEV:
            if platform_type == PlatformType.I386_PC:
                _Bios.remove_platform(platform_type, self._dev)
            elif Handy.isPlatformEfi(platform_type):
                _Efi.remove_platform(platform_type, self._bootDir)
            else:
                assert False
            _Common.remove_platform(self, platform_type)
        elif self._targetType == TargetType.PYCDLIB_OBJ:
            # FIXME
            assert False
        elif self._targetType == TargetType.ISO_DIR:
            _Common.remove_platform(self, platform_type)
        else:
            assert False

        del self._platforms[platform_type]

    def install_data(self, source, locales=None, fonts=None, themes=None):
        grubDir = os.path.join(self._bootDir, "grub")
        force_mkdir(grubDir)

        if locales is not None:
            Grub.copyLocaleFiles(source, grubDir, locales)
        if fonts is not None:
            Grub.copyFontFiles(source, grubDir, fonts)
        if themes is not None:
            Grub.copyThemeFiles(source, grubDir, themes)

    def remove_data(self):
        grubDir = os.path.join(self._bootDir, "grub")
        force_rm(os.path.join(grubDir, "locale"))
        force_rm(os.path.join(grubDir, "fonts"))
        force_rm(os.path.join(grubDir, "themes"))

    def install_env_file(self):
        grubEnvFile = os.path.join(self._bootDir, "grub", "grubenv")
        if not os.path.exists(grubEnvFile):
            Grub.createEnvBlkFile(grubEnvFile)

    def remove_env_file(self):
        grubEnvFile = os.path.join(self._bootDir, "grub", "grubenv")
        force_rm(grubEnvFile)

    def check(self, auto_fix=False):
        if self._targetType == TargetType.MOUNTED_HDD_DEV:
            _Common.check(self, auto_fix)
        elif self._targetType == TargetType.PYCDLIB_OBJ:
            # FIXME
            assert False
        elif self._targetType == TargetType.ISO_DIR:
            _Common.check(self, auto_fix)
        else:
            assert False

    def check_with_source(self, source, auto_fix=False):
        assert isinstance(source, Source)

        if self._targetType == TargetType.MOUNTED_HDD_DEV:
            _Common.check_with_source(self, source, auto_fix)
        elif self._targetType == TargetType.PYCDLIB_OBJ:
            # FIXME
            assert False
        elif self._targetType == TargetType.ISO_DIR:
            _Common.check_with_source(self, source, auto_fix)
        else:
            assert False


class _Common:

    def init_platforms(p):
        grubDir = os.path.join(p._bootDir, "grub")
        if os.path.isdir(grubDir):
            for fn in os.listdir(grubDir):
                for pt in PlatformType:
                    if fn == pt.value:
                        p._platforms[pt] = PlatformInstallInfo()
                        p._platforms[pt].status = PlatformInstallInfo.Status.BOOTABLE

    def install_platform(p, platform_type, source):
        mnt = mnt_probe(p._bootDir)
        if mnt.fs_uuid is None:
            raise Exception("")     # FIXME

        grubDir = os.path.join(p._bootDir, "grub")
        relGrubDir = grubDir.replace(mnt.mnt_pt, "")

        moduleList = []

        # disk module
        if platform_type == PlatformType.I386_PC:
            disk_module = "biosdisk"
        elif platform_type == PlatformType.I386_MULTIBOOT:
            disk_module = "native"
        elif Handy.isPlatformCoreboot(platform_type):
            disk_module = "native"
        elif Handy.isPlatformQemu(platform_type):
            disk_module = "native"
        elif platform_type == PlatformType.MIPSEL_LOONGSON:
            disk_module = "native"
        else:
            disk_module = None

        if disk_module is None:
            pass
        elif disk_module == "biosdisk":
            moduleList.append("biosdisk")
        elif disk_module == "native":
            moduleList += ["pata"]                              # for IDE harddisk
            moduleList += ["ahci"]                              # for SCSI harddisk
            moduleList += ["ohci", "uhci", "ehci", "ubms"]      # for USB harddisk
        else:
            assert False

        # fs module
        if Handy.isPlatformEfi(platform_type):
            if mnt.fs_name != "vfat":
                raise Exception("%s doesn't look like an EFI partition" % (p._bootDir))
        moduleList.append(Grub.getGrubFsName(mnt.fs_name))

        # install files
        Grub.copyPlatformFiles(platform_type, source, grubDir)

        # generate load.cfg for core.img
        loadCfgFile = os.path.join(grubDir, platform_type.value, "load.cfg")
        with open(loadCfgFile, "w") as f:
            moduleList.append("search_fs_uuid")
            f.write("search.fs_uuid %s root %s\n" % (mnt.fs_uuid, ""))  # FIXME: should add hints to raise performance
            f.write("set prefix=($root)'%s'\n" % (relGrubDir))          # FIXME: relGrubDir should be escaped

        # make core.img
        coreName, mkimageTarget = Grub.getCoreImgNameAndTarget()
        coreImgFile = os.path.join(grubDir, platform_type.value, coreName)
        subprocess.check_call(["grub-mkimage", "-c", loadCfgFile, "-O", mkimageTarget, "-d", source.get_platform_dir(platform_type), "-o", coreImgFile])

    def remove_platform(p, platform_type):
        platDir = os.path.join(p._bootDir, "grub", platform_type.value)
        force_rm(platDir)

    def check(p, auto_fix):
        grubDir = os.path.join(p._bootDir, "grub")
        if os.path.isdir(grubDir):
            pset = set([x.value for x in p._platforms])
            fset = set(os.listdir(grubDir)) - set(["locale", "fonts", "themes"])
            # FIXME: check every platform
            # FIXME: check redundant files
        else:
            if len(p._platforms) > 0:
                raise Exception("")     # FIXME

    def check_with_source(p, source, auto_fix):
        # FIXME
        pass




class _Bios:

    @staticmethod
    def install_platform(platform_type, source, bootDir, dev, bInstallMbr, bFloppyOrHdd, bAllowFloppy, bAddRsCodes):
        assert bFloppyOrHdd and not bAllowFloppy and bAddRsCodes

        coreImgFile = os.path.join(bootDir, "grub", "core.img")
        bootImgFile = os.path.join(bootDir, "grub", "boot.img")

        # copy boot.img file
        shutil.copy(os.path.join(source.get_platform_dir(platform_type), "boot.img"), bootImgFile)

        # install into device bios mbr
        if bInstallMbr:
            bootBuf = pathlib.Path(bootImgFile).read_bytes()
            if len(bootBuf) != Grub.DISK_SECTOR_SIZE:
                raise Exception("the size of '%s' is not %u" % (bootImgFile, Grub.DISK_SECTOR_SIZE))

            coreBuf = pathlib.Path(coreImgFile).read_bytes()
            if len(coreBuf) < Grub.DISK_SECTOR_SIZE:
                raise Exception("the size of '%s' is too small" % (coreImgFile))
            if len(coreBuf) > 0xFFFF * Grub.DISK_SECTOR_SIZE:
                raise Exception("the size of '%s' is too large" % (coreImgFile))
            coreSectors = (len(coreBuf) + Grub.DISK_SECTOR_SIZE - 1) // Grub.DISK_SECTOR_SIZE

            bootBuf = bytearray(bootBuf)
            with open(dev, "rb") as f:
                tmpBuf = f.read(Grub.DISK_SECTOR_SIZE)

                # Copy the possible DOS BPB.
                s, e = Grub.BOOT_MACHINE_BPB_START, Grub.BOOT_MACHINE_BPB_END
                bootBuf[s:e] = tmpBuf[s:e]

                # If DEST_DRIVE is a hard disk, enable the workaround, which is
                # for buggy BIOSes which don't pass boot drive correctly. Instead,
                # they pass 0x00 or 0x01 even when booted from 0x80.
                if not bAllowFloppy and not bFloppyOrHdd:
                    # Replace the jmp (2 bytes) with double nop's.
                    bootBuf[Grub.BOOT_MACHINE_DRIVE_CHECK] = 0x90
                    bootBuf[Grub.BOOT_MACHINE_DRIVE_CHECK+1] = 0x90

                # Copy the partition table.
                if not bAllowFloppy and not bFloppyOrHdd:
                    s, e = Grub.BOOT_MACHINE_WINDOWS_NT_MAGIC, Grub.BOOT_MACHINE_PART_END
                    bootBuf[s:e] = tmpBuf[s:e]

            # FIXME
            # grub_util_warn ("%s", _("Attempting to install GRUB to a disk with multiple partition labels or both partition label and filesystem.  This is not supported yet."));

            # FIXME
            #   grub_util_error (_("%s appears to contain a %s filesystem which isn't known to "
            # 		     "reserve space for DOS-style boot.  Installing GRUB there could "
            # 		     "result in FILESYSTEM DESTRUCTION if valuable data is overwritten "
            # 		     "by grub-setup (--skip-fs-probe disables this "
            # 		     "check, use at your own risk)"), dest_dev->disk->name, fs->name);

            # FIXME
            #   grub_util_error (_("%s appears to contain a %s partition map which isn't known to "
            # 		     "reserve space for DOS-style boot.  Installing GRUB there could "
            # 		     "result in FILESYSTEM DESTRUCTION if valuable data is overwritten "
            # 		     "by grub-setup (--skip-fs-probe disables this "
            # 		     "check, use at your own risk)"), dest_dev->disk->name, ctx.dest_partmap->name);

            # FIXME
            #   grub_util_error (_("%s appears to contain a %s partition map and "
            # 		     "LDM which isn't known to be a safe combination."
            # 		     "  Installing GRUB there could "
            # 		     "result in FILESYSTEM DESTRUCTION if valuable data"
            # 		     " is overwritten "
            # 		     "by grub-setup (--skip-fs-probe disables this "
            # 		     "check, use at your own risk)"),
            # 		   dest_dev->disk->name, ctx.dest_partmap->name);

            # FIXME
            #	grub_util_warn ("%s", _("Attempting to install GRUB to a partitionless disk or to a partition.  This is a BAD idea."));

            # FIXME
            #	grub_util_warn ("%s", _("Attempting to install GRUB to a disk with multiple partition labels.  This is not supported yet."));

            # FIXME
            #	grub_util_warn (_("Partition style `%s' doesn't support embedding"),

            # FIXME
            #	grub_util_warn (_("File system `%s' doesn't support embedding"),

            nsec = coreSectors
            if not bAddRsCodes:
                maxsec = coreSectors
            else:
                maxsec = 2 * coreSectors

            if maxsec > ((0x78000 - Grub.KERNEL_I386_PC_LINK_ADDR) // Grub.DISK_SECTOR_SIZE)
                maxsec = ((0x78000 - Grub.KERNEL_I386_PC_LINK_ADDR) // Grub.DISK_SECTOR_SIZE)

            # FIXME
            #			  N_("Your embedding area is unusually small.  core.img won't fit in it."));


        # grub_util_bios_setup("boot.img", "core.img", dev, fs_probe, True, )
        # grub_set_install_backup_ponr()

    @staticmethod
    def remove_platform(platform_type, bootDir):
        pass

    @staticmethod
    def install_platform_for_iso(platform_type, source, bootDir, dev, bHddOrFloppy, bInstallMbr):

        if 



        char *output = grub_util_path_concat (3, boot_grub, "i386-pc", "eltorito.img");
      load_cfg = grub_util_make_temporary_file ();



      grub_install_push_module ("biosdisk");
      grub_install_push_module ("iso9660");
      grub_install_make_image_wrap (source_dirs[GRUB_INSTALL_PLATFORM_I386_PC],
				    "/boot/grub", output,
				    0, load_cfg,
				    "i386-pc-eltorito", 0);
      xorriso_push ("-boot-load-size");
      xorriso_push ("4");
      xorriso_push ("-boot-info-table");

	      char *boot_hybrid = grub_util_path_concat (2, source_dirs[GRUB_INSTALL_PLATFORM_I386_PC],
							 "boot_hybrid.img");
	      xorriso_push ("--grub2-boot-info");
	      xorriso_push ("--grub2-mbr");
	      xorriso_push (boot_hybrid);

  /** build multiboot core.img */
  grub_install_push_module ("pata");
  grub_install_push_module ("ahci");
  grub_install_push_module ("at_keyboard");
  make_image (GRUB_INSTALL_PLATFORM_I386_MULTIBOOT, "i386-multiboot", "i386-multiboot/core.elf");
  grub_install_pop_module ();
  grub_install_pop_module ();
  grub_install_pop_module ();
  make_image_fwdisk (GRUB_INSTALL_PLATFORM_I386_IEEE1275, "i386-ieee1275", "ofwx86.elf");

  grub_install_push_module ("part_apple");
  make_image_fwdisk (GRUB_INSTALL_PLATFORM_POWERPC_IEEE1275, "powerpc-ieee1275", "powerpc-ieee1275/core.elf");
  grub_install_pop_module ();

  make_image_fwdisk (GRUB_INSTALL_PLATFORM_SPARC64_IEEE1275,
		     "sparc64-ieee1275-cdcore", "sparc64-ieee1275/core.img");




class _Efi:

    """We only support removable, and not upgrading NVRAM"""

    @staticmethod
    def install_platform(platform_type, source, bootDir):
        grubDir = os.path.join(bootDir, "grub")
        grubPlatDir = os.path.join(grubDir, platform_type.value)
        efiDir = os.path.join(bootDir, "EFI")
        efiDirLv2 = os.path.join(bootDir, "EFI", "BOOT")
        efiFn = Handy.getStandardEfiFile(platform_type)

        # create efi dir
        force_mkdir(efiDir)

        # create level 2 efi dir
        force_mkdir(efiDirLv2)

        # copy efi file
        coreName = Grub.getCoreImgNameAndTarget()[0]
        shutil.copy(os.path.join(grubPlatDir, coreName), os.path.join(efiDirLv2, efiFn))

    @staticmethod
    def remove_platform(platform_type, bootDir):
        efiDir = os.path.join(bootDir, "EFI")
        efiDirLv2 = os.path.join(bootDir, "EFI", "BOOT")
        efiFn = Handy.getStandardEfiFile(platform_type)

        # remove efi file
        force_rm(os.path.join(efiDirLv2, efiFn))

        # remove empty level 2 efi dir
        rmdir_if_empty(efiDirLv2)

        # remove empty efi dir
        rmdir_if_empty(efiDir)



# class _Sparc:
#
#     @staticmethod
#     def install_platform(p, platform_type, source):
#         grub_util_sparc_setup("boot.img", "core.img", dev, force?, fs_probe?, allow_floppy?, add_rs_codes?, )
#         grub_set_install_backup_ponr()








# self.allow_floppy = XXX   # --allow-floppy
# self.themes = XXX         # --themes=THEMES
# self.locales = XXX        # --locales=LOCALES
# self.pubkey = XXX         # --pubkey=FILE
# self.modules = XXX        # --install-modules=MODULES
# self.fonts = XXX          # --fonts=FONTS
# self.compress = XXX       # --compress=no|xz|gz|lzo

# we won't support:
# 1. 








# ia64-efi

# mips-arc
# mips-qemu_mips-flash
# mips-qemu_mips-elf

# mipsel-arc
# mipsel-fuloong2f-flash
# mipsel-loongson
# mipsel-loongson-elf
# mipsel-qemu_mips-elf
# mipsel-qemu_mips-flash
# mipsel-yeeloong-flash

# powerpc-ieee1275

# riscv32-efi

# riscv64-efi

# sparc64-ieee1275-raw
# sparc64-ieee1275-cdcore
# sparc64-ieee1275-aout


