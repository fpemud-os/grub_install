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
import re
import abc
import shutil
import parted
import pathlib
from ._util import rel_path, force_rm, force_mkdir, rmdir_if_empty, compare_files, is_buffer_all_zero
from ._const import TargetType, TargetAccessMode, PlatformType, PlatformInstallInfo
from ._errors import TargetError, InstallError
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
            if "boot_dir" in kwargs:
                self._bootDir = kwargs["boot_dir"]
            else:
                self._bootDir = os.path.join(self._rootfsDir, "boot")
            self._dev = kwargs["dev"]
        elif self._targetType == TargetType.PYCDLIB_OBJ:
            assert self._mode in [TargetAccessMode.R, TargetAccessMode.W]
            self._iso = kwargs.get["obj"]
        elif self._targetType == TargetType.ISO_DIR:
            self._dir = kwargs["dir"]
            self._bootDir = os.path.join(self._dir, "boot")
        else:
            assert False

        # fill self._platforms
        self._platforms = dict()
        if self._mode in [TargetAccessMode.R, TargetAccessMode.RW]:
            if self._targetType == TargetType.MOUNTED_HDD_DEV:
                _Common.init_platforms(self)
                for k, v in self._platforms.items():
                    try:
                        if k == PlatformType.I386_PC:
                            _Bios.fill_platform_install_info(k, v, self._bootDir, self._dev)
                        elif Handy.isPlatformEfi(k):
                            _Efi.fill_platform_install_info(k, v, self._targetType, self._bootDir)
                        else:
                            assert False
                    except TargetError as e:
                        self._platforms[k] = _newUnbootablePlatformInstallInfo(str(e))
            elif self._targetType == TargetType.PYCDLIB_OBJ:
                _PyCdLib.init_platforms(self)
                for k, v in self._platforms.items():
                    try:
                        if k == PlatformType.I386_PC:
                            # FIXME
                            assert False
                        elif Handy.isPlatformEfi(k):
                            # FIXME
                            assert False
                        else:
                            assert False
                    except TargetError as e:
                        self._platforms[k] = _newUnbootablePlatformInstallInfo(str(e))
            elif self._targetType == TargetType.ISO_DIR:
                _Common.init_platforms(self)
                for k, v in self._platforms.items():
                    try:
                        if k == PlatformType.I386_PC:
                            _Bios.fill_platform_install_info(k, v, self._bootDir, None)
                        elif Handy.isPlatformEfi(k):
                            _Efi.fill_platform_install_info(k, v, self._targetType, self._bootDir)
                        else:
                            assert False
                    except TargetError as e:
                        self._platforms[k] = _newUnbootablePlatformInstallInfo(str(e))
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
        return [k for k, v in self._platforms.items() if v.status == PlatformInstallInfo.Status.BOOTABLE]

    def get_platform_install_info(self, platform_type):
        assert isinstance(platform_type, PlatformType)

        if platform_type in self._platforms:
            return self._platforms[platform_type]
        else:
            return _newNotExistPlatformInstallInfo()

    def install_platform(self, platform_type, source, **kwargs):
        assert self._mode in [TargetAccessMode.RW, TargetAccessMode.W]
        assert isinstance(platform_type, PlatformType)
        assert isinstance(source, Source)

        ret = PlatformInstallInfo()
        ret.status = PlatformInstallInfo.Status.BOOTABLE

        if self._targetType == TargetType.MOUNTED_HDD_DEV:
            _Common.install_platform(self, platform_type, source,
                                     tmpDir=kwargs.get("tmp_dir", None),
                                     debugImage=kwargs.get("debug_image", None))
            if platform_type == PlatformType.I386_PC:
                _Bios.install_boot_img(platform_type, ret, source, self._bootDir)
                if kwargs.get("bootsector", True):
                    _Bios.install_into_mbr(platform_type, ret, source, self._bootDir, self._dev,
                                           False,                                               # bFloppyOrHdd
                                           kwargs.get("allow_floppy", False),                   # bAllowFloppy
                                           kwargs.get("rs_codes", True))                        # bAddRsCodes
            elif Handy.isPlatformEfi(platform_type):
                _Efi.install_info_efi_dir(platform_type, ret, self._bootDir,
                                          kwargs.get("removable", False),                       # bRemovable
                                          kwargs.get("update_nvram", False))                    # bUpdateNvram
            else:
                assert False
        elif self._targetType == TargetType.PYCDLIB_OBJ:
            # FIXME
            assert False
        elif self._targetType == TargetType.ISO_DIR:
            _Common.install_platform(self, platform_type, source,
                                     tmpDir=kwargs.get("tmp_dir", None),
                                     debugImage=kwargs.get("debug_image", None))
            if platform_type == PlatformType.I386_PC:
                _Bios.install_boot_img(platform_type, ret, source, self._bootDir)
            elif Handy.isPlatformEfi(platform_type):
                _Efi.install_info_efi_dir(platform_type, ret, self._bootDir,
                                          kwargs.get("removable", False),                       # bRemovable
                                          False)                                                # bUpdateNvram
            else:
                assert False
        else:
            assert False

        self._platforms[platform_type] = ret

    def remove_platform(self, platform_type):
        assert self._mode in [TargetAccessMode.RW, TargetAccessMode.W]
        assert isinstance(platform_type, PlatformType)

        # do nothing if the specified platform does not exists
        if platform_type not in self._platforms:
            return

        # do remove
        if self._targetType == TargetType.MOUNTED_HDD_DEV:
            if platform_type == PlatformType.I386_PC:
                _Bios.remove_from_mbr(platform_type, self._dev)
            elif Handy.isPlatformEfi(platform_type):
                _Efi.remove_from_efi_dir(platform_type, self._bootDir)
            else:
                assert False
            _Common.remove_platform(self, platform_type)
        elif self._targetType == TargetType.PYCDLIB_OBJ:
            # FIXME
            assert False
        elif self._targetType == TargetType.ISO_DIR:
            if platform_type == PlatformType.I386_PC:
                pass
            elif Handy.isPlatformEfi(platform_type):
                _Efi.remove_from_efi_dir(platform_type, self._bootDir)
            else:
                assert False
            _Common.remove_platform(self, platform_type)
        else:
            assert False

        # delete PlatformInstallInfo object
        del self._platforms[platform_type]

    def install_data(self, source, locales=None, fonts=None, themes=None):
        assert self._mode in [TargetAccessMode.RW, TargetAccessMode.W]

        grubDir = os.path.join(self._bootDir, "grub")
        force_mkdir(grubDir)

        if locales is not None:
            Grub.copyLocaleFiles(source, grubDir, locales)
        if fonts is not None:
            Grub.copyFontFiles(source, grubDir, fonts)
        if themes is not None:
            Grub.copyThemeFiles(source, grubDir, themes)

    def remove_data(self):
        assert self._mode in [TargetAccessMode.RW, TargetAccessMode.W]

        grubDir = os.path.join(self._bootDir, "grub")
        force_rm(os.path.join(grubDir, "locale"))
        force_rm(os.path.join(grubDir, "fonts"))
        force_rm(os.path.join(grubDir, "themes"))

    def touch_env_file(self):
        assert self._mode in [TargetAccessMode.RW, TargetAccessMode.W]

        grubEnvFile = os.path.join(self._bootDir, "grub", "grubenv")
        if not os.path.exists(grubEnvFile):
            Grub.createEnvBlkFile(grubEnvFile)

    def remove_env_file(self):
        assert self._mode in [TargetAccessMode.RW, TargetAccessMode.W]

        grubEnvFile = os.path.join(self._bootDir, "grub", "grubenv")
        force_rm(grubEnvFile)

    def remove_all(self):
        assert self._mode in [TargetAccessMode.RW, TargetAccessMode.W]

        # remove platforms, some platform needs special processing
        for k in list(self._platforms.keys()):
            self.remove_platform(k)

        # remove remaining files
        _Efi.remove_remaining_crufts(self._bootDir)
        _Common.remove_remaining_crufts(self)

    def check_with_source(self, source, auto_fix=False):
        assert self._mode in [TargetAccessMode.R, TargetAccessMode.RW]
        assert isinstance(source, Source)

        for pt in self._platforms:
            if self._targetType == TargetType.MOUNTED_HDD_DEV:
                _Common.check_with_source(self, pt, source, auto_fix)
            elif self._targetType == TargetType.PYCDLIB_OBJ:
                # FIXME
                assert False
            elif self._targetType == TargetType.ISO_DIR:
                _Common.check_with_source(self, pt, source, auto_fix)
            else:
                assert False


class _Common:

    @staticmethod
    def init_platforms(p):
        grubDir = os.path.join(p._bootDir, "grub")
        if os.path.isdir(grubDir):
            for fn in os.listdir(grubDir):
                try:
                    obj = PlatformInstallInfo()
                    obj.status = PlatformInstallInfo.Status.BOOTABLE
                    p._platforms[PlatformType(fn)] = obj
                except ValueError:
                    pass

    @staticmethod
    def install_platform(p, platform_type, source, tmpDir=None, debugImage=None):
        mnt = Grub.probeMnt(p._bootDir)
        if mnt.fs_uuid is None:
            raise InstallError("no fsuuid found")
        if Handy.isPlatformEfi(platform_type) and (mnt.mnt_dir != p._bootDir or mnt.fs != "fat"):
            raise InstallError("%s doesn't look like an EFI partition" % (p._bootDir))

        grubDir = os.path.join(p._bootDir, "grub")
        moduleList = []

        # disk module
        if platform_type == PlatformType.I386_PC:
            disk_module = "biosdisk"
            hints = mnt.bios_hints
        elif platform_type == PlatformType.I386_MULTIBOOT:
            disk_module = "native"
            hints = ""
        elif Handy.isPlatformEfi(platform_type):
            disk_module = None
            hints = mnt.efi_hints
        elif Handy.isPlatformCoreboot(platform_type):
            disk_module = "native"
            hints = ""
        elif Handy.isPlatformQemu(platform_type):
            disk_module = "native"
            hints = ""
        elif platform_type == PlatformType.MIPSEL_LOONGSON:
            disk_module = "native"
            hints = ""
        else:
            disk_module = None
            hints = ""

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
        moduleList.append(mnt.fs)
        moduleList.append("search_fs_uuid")

        # install module files
        # FIXME: install only required modules
        Grub.copyPlatformFiles(platform_type, source, grubDir)

        # generate load.cfg for core.img
        buf = ""
        if debugImage is not None:
            buf += "set debug='%s'\n" % (debugImage)
        buf += "search.fs_uuid %s root%s\n" % (mnt.fs_uuid, (" " + hints) if hints != "" else "")
        buf += "set prefix=($root)'%s'\n" % (Grub.escape(rel_path(mnt.mnt_dir, grubDir)))

        # make core.img
        coreName, mkimageTarget = Grub.getCoreImgNameAndTarget(platform_type)
        coreImgPath = os.path.join(grubDir, platform_type.value, coreName)
        Grub.makeCoreImage(source, platform_type, buf, mkimageTarget, moduleList, coreImgPath, tmp_dir=tmpDir)

    @staticmethod
    def remove_platform(p, platform_type):
        platDir = os.path.join(p._bootDir, "grub", platform_type.value)
        force_rm(platDir)

    @staticmethod
    def remove_remaining_crufts(p):
        force_rm(os.path.join(p._bootDir, "grub"))

    @staticmethod
    def check(p, platform_type, auto_fix):
        grubDir = os.path.join(p._bootDir, "grub")
        if os.path.isdir(grubDir):
            pset = set([x.value for x in p._platforms])
            fset = set(os.listdir(grubDir)) - set(["locale", "fonts", "themes"])
            # FIXME: check every platform
            # FIXME: check redundant files
        else:
            if len(p._platforms) > 0:
                raise Exception("")     # FIXME

    @staticmethod
    def check_with_source(p, platform_type, source, auto_fix):
        grubDir = os.path.join(p._bootDir, "grub")
        Grub.checkPlatformFiles(platform_type, source, grubDir)


        # FIXME
        pass


class _Bios:

    @classmethod
    def fill_platform_install_info(cls, platform_type, platform_install_info, bootDir, dev):
        bootBuf = bytearray(cls._checkAndReadBootImg(platform_type, bootDir, TargetError))     # bootBuf needs to be writable
        coreBuf = cls._checkAndReadCoreImg(platform_type, bootDir, TargetError)

        # no MBR probe needed
        if dev is None:
            platform_install_info.mbr_installed = False
            platform_install_info.allow_floppy = True
            platform_install_info.rs_codes = False
            return

        # read MBR and MBR-gap
        tmpBootBuf, tmpCoreBuf, tmpRestBuf = None, None, None
        with open(dev, "rb") as f:
            tmpBootBuf = f.read(len(bootBuf))
            tmpCoreBuf = f.read(len(coreBuf))
            tmpRestBuf = f.read(cls._getCoreImgMaxSize() - len(coreBuf) - len(bootBuf))

        # boot.img and core.img is not installed
        if tmpBootBuf == cls._getAllZeroBootBuf(tmpBootBuf) and is_buffer_all_zero(tmpCoreBuf) and is_buffer_all_zero(tmpRestBuf):
            platform_install_info.mbr_installed = False
            platform_install_info.allow_floppy = True
            platform_install_info.rs_codes = False
            return

        # prepare bootBuf
        if True:
            # see comment in cls.install_into_mbr()
            s, e = Grub.BOOT_MACHINE_BPB_START, Grub.BOOT_MACHINE_BPB_END
            bootBuf[s:e] = tmpBootBuf[s:e]

            # see comment in cls.install_into_mbr()
            s, e = Grub.BOOT_MACHINE_DRIVE_CHECK, Grub.BOOT_MACHINE_DRIVE_CHECK + 2
            if tmpBootBuf[s:e] == b'\x90\x90':
                bootBuf[s:e] = tmpBootBuf[s:e]
                bAllowFloppy = False
            else:
                bAllowFloppy = True

            # see comment in cls.install_into_mbr()
            s, e = Grub.BOOT_MACHINE_WINDOWS_NT_MAGIC, Grub.BOOT_MACHINE_PART_END
            bootBuf[s:e] = tmpBootBuf[s:e]

        # compare
        if tmpBootBuf != bootBuf:
            raise TargetError("invalid MBR record content")
        if tmpCoreBuf != coreBuf:
            raise TargetError("invalid on-disk core.img content")
        if not is_buffer_all_zero(tmpRestBuf):
            raise TargetError("disk content after core.img should be all zero")

        # return
        platform_install_info.mbr_installed = True
        platform_install_info.allow_floppy = bAllowFloppy
        platform_install_info.rs_codes = False
        return

    @classmethod
    def install_boot_img(cls, platform_type, platform_install_info, source, bootDir):
        shutil.copy(os.path.join(source.get_platform_directory(platform_type), "boot.img"), os.path.join(bootDir, "grub", platform_type.value))

        # fill custom attributes
        platform_install_info.mbr_installed = False
        platform_install_info.allow_floppy = True
        platform_install_info.rs_codes = False

    @classmethod
    def install_into_mbr(cls, platform_type, platform_install_info, bootDir, dev, bFloppyOrHdd, bAllowFloppy, bAddRsCodes):
        assert not bFloppyOrHdd and not bAllowFloppy and not bAddRsCodes        # FIXME

        bootBuf = bytearray(cls._checkAndReadBootImg(platform_type, bootDir, InstallError))     # bootBuf needs to be writable
        coreBuf = cls._checkAndReadCoreImg(platform_type, bootDir, InstallError)
        cls._checkDisk(dev, InstallError)

        with open(dev, "rb+") as f:
            tmpBootBuf = f.read(len(bootBuf))

            # prepare bootBuf
            if True:
                # Copy the possible DOS BPB.
                s, e = Grub.BOOT_MACHINE_BPB_START, Grub.BOOT_MACHINE_BPB_END
                bootBuf[s:e] = tmpBootBuf[s:e]

                # If DEST_DRIVE is a hard disk, enable the workaround, which is
                # for buggy BIOSes which don't pass boot drive correctly. Instead,
                # they pass 0x00 or 0x01 even when booted from 0x80.
                if not bAllowFloppy and not bFloppyOrHdd:
                    # Replace the jmp (2 bytes) with double nop's.
                    s, e = Grub.BOOT_MACHINE_DRIVE_CHECK, Grub.BOOT_MACHINE_DRIVE_CHECK + 2
                    bootBuf[s:e] == b'\x90\x90'

                # Copy the partition table.
                if not bAllowFloppy and not bFloppyOrHdd:
                    s, e = Grub.BOOT_MACHINE_WINDOWS_NT_MAGIC, Grub.BOOT_MACHINE_PART_END
                    bootBuf[s:e] = tmpBootBuf[s:e]

            # write up to cls._getCoreImgMaxSize()
            f.seek(0)
            if bAddRsCodes:
                assert False
            else:
                f.write(bootBuf)
                f.write(coreBuf)
                for i in range(0, cls._getCoreImgMaxSize() - len(coreBuf) - len(bootBuf)):
                    f.write(b'\x00')

        # fill custom attributes
        platform_install_info.mbr_installed = True
        platform_install_info.allow_floppy = bAllowFloppy
        platform_install_info.rs_codes = bAddRsCodes

    @classmethod
    def remove_from_mbr(cls, platform_type, dev):
        cls._checkDisk(dev, None)

        with open(dev, "rb+") as f:
            # prepare allZeroBootBuf
            tmpBootBuf = f.read(Grub.DISK_SECTOR_SIZE)
            allZeroBootBuf = cls._getAllZeroBootBuf(tmpBootBuf)

            # write up to cls._getCoreImgMaxSize()
            f.seek(0)
            f.write(allZeroBootBuf)
            for i in range(0, cls._getCoreImgMaxSize() - len(allZeroBootBuf)):
                f.write(b'\x00')

    @staticmethod
    def _getCoreImgMaxSize():
        return Grub.DISK_SECTOR_SIZE * 1024

    @classmethod
    def _checkDisk(cls, dev, exceptionClass):
        if not re.fullmatch(".*[0-9]+$", dev):
            if exceptionClass is not None:
                raise exceptionClass("'%s' must be a disk" % (dev))
            else:
                assert False

        pDev = parted.getDevice(dev)
        try:
            pDisk = parted.newDisk(pDev)
            try:
                if pDisk.type != "msdos":
                    if exceptionClass is not None:
                        raise exceptionClass("'%s' must have a MBR partition table" % (dev))
                    else:
                        assert False
                pPartiList = pDisk.getPrimaryPartitions()
                if len(pPartiList) > 0:
                    if exceptionClass is not None:
                        raise exceptionClass("'%s' must have no partition" % (dev))
                    else:
                        assert False
                if pPartiList[0].geometry.start * pDev.sectorSize < cls._getCoreImgMaxSize():
                    if exceptionClass is not None:
                        raise exceptionClass("'%s' has no MBR gap or its MBR gap is too small" % (dev))
                    else:
                        assert False
            finally:
                pDisk.destroy()
        finally:
            pDev.destroy()

    @staticmethod
    def _checkAndReadBootImg(platform_type, bootDir, exceptionClass):
        bootImgFile = os.path.join(bootDir, "grub", platform_type.value, "boot.img")
        if not os.path.exists(bootImgFile):
            raise exceptionClass("'%s' does not exist" % (bootImgFile))
        bootBuf = pathlib.Path(bootImgFile).read_bytes()
        if len(bootBuf) != Grub.DISK_SECTOR_SIZE:
            raise exceptionClass("the size of '%s' is not %u" % (bootImgFile, Grub.DISK_SECTOR_SIZE))
        return bootBuf

    @classmethod
    def _checkAndReadCoreImg(cls, platform_type, bootDir, exceptionClass):
        coreImgFile = os.path.join(bootDir, "grub", platform_type.value, Grub.getCoreImgNameAndTarget(platform_type)[0])
        if not os.path.exists(coreImgFile):
            raise exceptionClass("'%s' does not exist" % (coreImgFile))
        coreBuf = pathlib.Path(coreImgFile).read_bytes()
        if not (Grub.DISK_SECTOR_SIZE <= len(coreBuf) <= cls._getCoreImgMaxSize()):
            raise exceptionClass("the size of '%s' is invalid" % (coreImgFile))
        return coreBuf

    @staticmethod
    def _getAllZeroBootBuf(onDiskBootBuf):
        allZeroBootBuf = bytearray(Grub.DISK_SECTOR_SIZE - 2) + b'\x55\xAA'

        # see comment in cls.install_into_mbr()
        s, e = Grub.BOOT_MACHINE_BPB_START, Grub.BOOT_MACHINE_BPB_END
        allZeroBootBuf[s:e] = onDiskBootBuf[s:e]

        # see comment in cls.install_into_mbr()
        s, e = Grub.BOOT_MACHINE_WINDOWS_NT_MAGIC, Grub.BOOT_MACHINE_PART_END
        allZeroBootBuf[s:e] = onDiskBootBuf[s:e]

        return bytes(allZeroBootBuf)


class _Efi:

    """We only support removable, and not upgrading NVRAM"""

    @staticmethod
    def fill_platform_install_info(platform_type, platform_install_info, target_type, bootDir):
        coreFullfn = os.path.join(bootDir, "grub", platform_type.value, Grub.getCoreImgNameAndTarget(platform_type)[0])
        efiFullfn = os.path.join(bootDir, "EFI", "BOOT", Handy.getStandardEfiFilename(platform_type))

        if not os.path.exists(coreFullfn):
            raise TargetError("%s does not exist" % (coreFullfn))
        if not os.path.exists(efiFullfn):
            raise TargetError("%s does not exist" % (efiFullfn))
        if not compare_files(coreFullfn, efiFullfn):
            raise TargetError("%s and %s are different" % (coreFullfn, efiFullfn))

        platform_install_info.removable = True
        platform_install_info.nvram = False

    @staticmethod
    def install_info_efi_dir(platform_type, platform_install_info, bootDir, bRemovable, bUpdateNvram):
        assert bRemovable and not bUpdateNvram          # FIXME

        grubPlatDir = os.path.join(bootDir, "grub", platform_type.value)
        efiDir = os.path.join(bootDir, "EFI")
        efiDirLv2 = os.path.join(bootDir, "EFI", "BOOT")
        efiFn = Handy.getStandardEfiFilename(platform_type)

        # create efi dir
        force_mkdir(efiDir)

        # create level 2 efi dir
        force_mkdir(efiDirLv2)

        # copy efi file
        coreName = Grub.getCoreImgNameAndTarget(platform_type)[0]
        shutil.copy(os.path.join(grubPlatDir, coreName), os.path.join(efiDirLv2, efiFn))

        # fill custom attributes
        platform_install_info.removable = bRemovable
        platform_install_info.nvram = bUpdateNvram

    @staticmethod
    def remove_from_efi_dir(platform_type, bootDir):
        efiDir = os.path.join(bootDir, "EFI")
        efiDirLv2 = os.path.join(bootDir, "EFI", "BOOT")
        efiFn = Handy.getStandardEfiFilename(platform_type)

        # remove efi file
        force_rm(os.path.join(efiDirLv2, efiFn))

        # remove empty level 2 efi dir
        rmdir_if_empty(efiDirLv2)

        # remove empty efi dir
        rmdir_if_empty(efiDir)

    @staticmethod
    def remove_remaining_crufts(bootDir):
        force_rm(os.path.join(bootDir, "EFI"))


class _PyCdLib:

    @staticmethod
    def init_platforms(p):
        pass


def _newUnbootablePlatformInstallInfo(unbootable_reason):
    ret = PlatformInstallInfo()
    ret.status = PlatformInstallInfo.Status.UNBOOTABLE
    ret.unbootable_reason = unbootable_reason
    return ret


def _newNotExistPlatformInstallInfo():
    ret = PlatformInstallInfo()
    ret.status = PlatformInstallInfo.Status.NOT_EXIST
    return ret


#     @staticmethod
#     def install_platform_for_iso(platform_type, source, bootDir, dev, bHddOrFloppy, bInstallMbr):

#         if



#         char *output = grub_util_path_concat (3, boot_grub, "i386-pc", "eltorito.img");
#       load_cfg = grub_util_make_temporary_file ();



#       grub_install_push_module ("biosdisk");
#       grub_install_push_module ("iso9660");
#       grub_install_make_image_wrap (source_dirs[GRUB_INSTALL_PLATFORM_I386_PC],
#             "/boot/grub", output,
#             0, load_cfg,
#             "i386-pc-eltorito", 0);
#       xorriso_push ("-boot-load-size");
#       xorriso_push ("4");
#       xorriso_push ("-boot-info-table");

# 	      char *boot_hybrid = grub_util_path_concat (2, source_dirs[GRUB_INSTALL_PLATFORM_I386_PC],
#             	 "boot_hybrid.img");
# 	      xorriso_push ("--grub2-boot-info");
# 	      xorriso_push ("--grub2-mbr");
# 	      xorriso_push (boot_hybrid);

#   /** build multiboot core.img */
#   grub_install_push_module ("pata");
#   grub_install_push_module ("ahci");
#   grub_install_push_module ("at_keyboard");
#   make_image (GRUB_INSTALL_PLATFORM_I386_MULTIBOOT, "i386-multiboot", "i386-multiboot/core.elf");
#   grub_install_pop_module ();
#   grub_install_pop_module ();
#   grub_install_pop_module ();
#   make_image_fwdisk (GRUB_INSTALL_PLATFORM_I386_IEEE1275, "i386-ieee1275", "ofwx86.elf");

#   grub_install_push_module ("part_apple");
#   make_image_fwdisk (GRUB_INSTALL_PLATFORM_POWERPC_IEEE1275, "powerpc-ieee1275", "powerpc-ieee1275/core.elf");
#   grub_install_pop_module ();

#   make_image_fwdisk (GRUB_INSTALL_PLATFORM_SPARC64_IEEE1275,
#          "sparc64-ieee1275-cdcore", "sparc64-ieee1275/core.img");






# self.pubkey = XXX         # --pubkey=FILE
# self.compress = XXX       # --compress=no|xz|gz|lzo







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
