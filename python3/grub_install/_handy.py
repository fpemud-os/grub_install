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
import glob
import shutil
import psutil
import tempfile
import subprocess
from ._util import rel_path, force_mkdir, compare_files
from ._const import PlatformType
from ._errors import CheckError


class Handy:

    @staticmethod
    def isPlatformBigEndianOrLittleEndian(platform_type):
        if platform_type.value.startswith("i386-"):
            return False
        elif platform_type.value.startswith("x86_64-"):
            return False
        elif platform_type.value.startswith("arm-"):
            return False
        elif platform_type.value.startswith("arm64-"):
            return False
        elif platform_type.value.startswith("ia64-"):
            return False
        elif platform_type.value.startswith("sparc64-"):
            return True
        elif platform_type.value.startswith("powerpc-"):
            return True
        elif platform_type.value.startswith("mips-"):
            return True
        elif platform_type.value.startswith("mipsel-"):
            return False
        elif platform_type.value.startswith("riscv32-"):
            return False
        elif platform_type.value.startswith("riscv64-"):
            return False
        else:
            assert False

    @staticmethod
    def isPlatformEfi(platform_type):
        return platform_type in [
            PlatformType.I386_EFI,
            PlatformType.X86_64_EFI,
            PlatformType.IA64_EFI,
            PlatformType.ARM_EFI,
            PlatformType.ARM64_EFI,
            PlatformType.RISCV32_EFI,
            PlatformType.RISCV64_EFI
        ]

    @staticmethod
    def isPlatformCoreboot(platform_type):
        return platform_type in [
            PlatformType.I386_COREBOOT,
            PlatformType.ARM_COREBOOT,
        ]

    @staticmethod
    def isPlatformXen(platform_type):
        return platform_type in [
            PlatformType.I386_XEN,
            PlatformType.I386_XEN_PVH,
            PlatformType.X86_64_XEN,
        ]

    @staticmethod
    def isPlatformQemu(platform_type):
        return platform_type in [
            PlatformType.I386_QEMU,
            PlatformType.MIPS_QEMU_MIPS,
            PlatformType.MIPSEL_QEMU_MIPS,
        ]

    @staticmethod
    def isPlatformIeee1275(platform_type):
        return platform_type in [
            PlatformType.I386_IEEE1275,
            PlatformType.POWERPC_IEEE1275,
            PlatformType.SPARC64_IEEE1275,
        ]

    @staticmethod
    def getStandardEfiFilename(platform_type):
        # The specification makes stricter requirements of removable
        #  devices, in order that only one image can be automatically loaded
        #  from them.  The image must always reside under /EFI/BOOT, and it
        #  must have a specific file name depending on the architecture.

        if platform_type == PlatformType.I386_EFI:
            return "BOOTIA32.EFI"
        if platform_type == PlatformType.X86_64_EFI:
            return "BOOTX64.EFI"
        if platform_type == PlatformType.IA64_EFI:
            return "BOOTIA64.EFI"
        if platform_type == PlatformType.ARM_EFI:
            return "BOOTARM.EFI"
        if platform_type == PlatformType.ARM64_EFI:
            return "BOOTAA64.EFI"
        if platform_type == PlatformType.RISCV32_EFI:
            return "BOOTRISCV32.EFI"
        if platform_type == PlatformType.RISCV64_EFI:
            return "BOOTRISCV64.EFI"
        assert False


class Grub:

    DISK_SECTOR_SIZE = 0x200

    # The offset of the start of BPB (BIOS Parameter Block).
    BOOT_MACHINE_BPB_START = 0x3

    # The offset of the end of BPB (BIOS Parameter Block).
    BOOT_MACHINE_BPB_END = 0x5a                                 # note: this is end+1

    # The offset of BOOT_DRIVE_CHECK.
    BOOT_MACHINE_DRIVE_CHECK = 0x66

    # The offset of a magic number used by Windows NT.
    BOOT_MACHINE_WINDOWS_NT_MAGIC = 0x1b8

    # The offset of the start of the partition table.
    BOOT_MACHINE_PART_START = 0x1be

    # The offset of the end of the partition table.
    BOOT_MACHINE_PART_END = 0x1fe                               # note: this is end+1

    KERNEL_I386_PC_LINK_ADDR = 0x9000

    # Offset of field holding no reed solomon length.
    KERNEL_I386_PC_NO_REED_SOLOMON_LENGTH = 0x14

    PLATFORM_ADDON_FILES = ["moddep.lst", "command.lst", "fs.lst", "partmap.lst", "parttool.lst", "video.lst", "crypto.lst", "terminal.lst", "modinfo.sh"]

    PLATFORM_OPTIONAL_ADDON_FILES = ["efiemu32.o", "efiemu64.o"]

    @staticmethod
    def getCoreImgNameAndTarget(platform_type):
        if platform_type == PlatformType.I386_PC:
            core_name = "core.img"
            mkimage_target = platform_type.value
        elif platform_type == PlatformType.I386_QEMU:
            core_name = "core.img"
            mkimage_target = platform_type.value
        elif Handy.isPlatformEfi(platform_type):
            core_name = "core.efi"
            mkimage_target = platform_type.value
        elif Handy.isPlatformCoreboot(platform_type) or Handy.isPlatformXen(platform_type):
            core_name = "core.elf"
            mkimage_target = platform_type.value
        elif Handy.isPlatformIeee1275(platform_type):
            if platform_type in [PlatformType.I386_IEEE1275, PlatformType.POWERPC_IEEE1275]:
                core_name = "core.elf"
                mkimage_target = platform_type.value
            elif platform_type == PlatformType.SPARC64_IEEE1275:
                core_name = "core.img"
                mkimage_target = "sparc64-ieee1275-raw"
            else:
                assert False
        elif platform_type == PlatformType.I386_MULTIBOOT:
            core_name = "core.elf"
            mkimage_target = platform_type.value
        elif platform_type in [PlatformType.MIPSEL_LOONGSON, PlatformType.MIPSEL_QEMU_MIPS, PlatformType.MIPS_QEMU_MIPS]:
            core_name = "core.elf"
            mkimage_target = platform_type.value + "-elf"
        elif platform_type in [PlatformType.MIPSEL_ARC, PlatformType.MIPS_ARC, PlatformType.ARM_UBOOT]:
            core_name = "core.img"
            mkimage_target = platform_type.value
        else:
            assert False

        return (core_name, mkimage_target)

    @staticmethod
    def createEnvBlkFile(name):
        DEFAULT_ENVBLK_SIZE = 1024
        GRUB_ENVBLK_SIGNATURE = "# GRUB Environment Block\n"
        GRUB_ENVBLK_MESSAGE = "# WARNING: Do not edit this file by tools other than grub-editenv!!!\n"

        tmpName = name + ".new"

        with open(tmpName, "w") as f:
            f.write(GRUB_ENVBLK_SIGNATURE)
            f.write(GRUB_ENVBLK_MESSAGE)
            f.write("#" * (DEFAULT_ENVBLK_SIZE - len(GRUB_ENVBLK_SIGNATURE) - len(GRUB_ENVBLK_MESSAGE)))

        os.rename(tmpName, name)

    @classmethod
    def checkPlatformModuleFilesAndRedundants(cls, platform_type, source, grub_dir):
        platDirSrc = source.get_platform_directory(platform_type)
        platDirDst = os.path.join(grub_dir, platform_type.value)
        fileSet = set()

        if not os.path.exists(platDirDst):
            raise CheckError("%s does not exist" % (platDirDst))

        def __check(fullfn, fullfn2):
            # FIXME: check owner, group, mode?
            if not os.path.exists(fullfn2):
                raise CheckError("%s does not exist" % (fullfn2))
            if not compare_files(fullfn, fullfn2):
                raise CheckError("%s and %s are different" % (fullfn, fullfn2))
            fileSet.add(fullfn2)

        # check module files
        for fullfn in glob.glob(os.path.join(platDirSrc, "*.mod")):
            __check(fullfn, os.path.join(platDirDst, os.path.basename(fullfn)))

        # check addon files
        for fn in cls.PLATFORM_ADDON_FILES:
            __check(os.path.join(platDirSrc, fn), os.path.join(platDirDst, fn))

        # check optional addon files
        for fn in cls.PLATFORM_OPTIONAL_ADDON_FILES:
            fullfn, fullfn2 = os.path.join(platDirSrc, fn), os.path.join(platDirDst, fn)
            if os.path.exists(fullfn):
                __check(fullfn, fullfn2)

        # return redundant files
        ret = set(glob.glob(os.path.join(platDirDst, "*"))) - fileSet
        return [os.path.basename(ret) for x in ret]

    @staticmethod
    def copyLocaleFiles(source, grub_dir, locales):
        assert source.supports(source.CAP_NLS)

        dstDir = os.path.join(grub_dir, "locales")
        force_mkdir(dstDir, clear=True)

        if locales == "*":
            for lname, fullfn in source.get_all_locale_files().items():
                shutil.copy(fullfn, os.path.join(dstDir, "%s.mo" % (lname)))
        else:
            for lname in locales:
                shutil.copy(source.get_locale_file(lname), "%s.mo" % (lname))

    @staticmethod
    def checkLocaleFilesAndRedundants(source, grub_dir):
        assert source.supports(source.CAP_NLS)

        dstDir = os.path.join(os.path.join(grub_dir, "locales")
        if not os.path.exists(dstDir):
            raise CheckError("%s does not exist" % (dstDir))

        ret = []
        for fn2 in os.listdir(dstDir):
            fullfn2 = os.path.join(dstDir, fn2)
            if fn2.endswith(".mo"):
                lname = fn2.replace(".mo", "")
                fullfn = source.try_get_locale_file(lname)
                if fullfn is not None:
                    if not compare_files(fullfn, fullfn2):
                        raise CheckError("%s and %s are different" % (fullfn, fullfn2))
                    continue
            ret.append(fullfn2)
        return ret

    @staticmethod
    def copyFontFiles(source, grub_dir, fonts):
        assert source.supports(source.CAP_FONTS)

        dstDir = os.path.join(grub_dir, "fonts")
        force_mkdir(dstDir, clear=True)

        if fonts == "*":
            for fname, fullfn in source.get_all_font_files().items():
                shutil.copy(fullfn, dstDir)
        else:
            for fname in fonts:
                shutil.copy(source.get_font_file(fname), dstDir)

    @staticmethod
    def checkFontFilesAndRedundants(source, grub_dir):
        assert source.supports(source.CAP_FONTS)

        dstDir = os.path.join(os.path.join(grub_dir, "fonts")
        if not os.path.exists(dstDir):
            raise CheckError("%s does not exist" % (dstDir))

        ret = []
        for fullfn2 in glob.glob(dstDir, "*.pf2"):
            fname = os.path.basename(fullfn2).replace(".pf2", "")
            fullfn = source.try_get_font_file(fname)
            if fullfn is not None:
                if not compare_files(fullfn, fullfn2):
                    raise CheckError("%s and %s are different" % (fullfn, fullfn2))
                continue
            ret.append(fullfn2)
        return ret

    @staticmethod
    def copyThemeFiles(source, grub_dir, themes):
        assert source.supports(source.CAP_THEMES)

        dstDir = os.path.join(grub_dir, "themes")
        force_mkdir(dstDir, clear=True)

        if themes == "*":
            for tname, fullfn in source.get_all_theme_directories():
                shutil.copytree(fullfn, dstDir)
        else:
            for tname in themes:
                shutil.copytree(source.get_theme_directory(tname), dstDir)

    @staticmethod
    def checkThemeFilesAndRedundants(source, grub_dir):
        assert source.supports(source.CAP_THEMES)

        dstDir = os.path.join(os.path.join(grub_dir, "themes")
        if not os.path.exists(dstDir):
            raise CheckError("%s does not exist" % (dstDir))

        ret = []
        for tname in os.listdir(dstDir):
            fullfn2 = os.path.join(dstDir, tname)
            if os.path.isdir(fullfn2):
                fullfn = source.try_get_theme_directory(lname)
                if fullfn is not None:
                    if not compare_directories(fullfn, fullfn2):
                        raise CheckError("%s and %s are different" % (fullfn, fullfn2))
                    continue
            ret.append(fullfn2)
        return ret

    @staticmethod
    def makeCoreImage(source, platform_type, load_cfg_file_content, mkimage_target, module_list, out_path, tmp_dir=None):
        with tempfile.TemporaryDirectory(dir=tmp_dir) as tmpdir:
            loadCfgFile = os.path.join(tmpdir, "load.cfg")
            with open(loadCfgFile, "w") as f:
                f.write(load_cfg_file_content)
            subprocess.check_call(["grub-mkimage", "-c", loadCfgFile, "-O", mkimage_target, "-d", source.get_platform_directory(platform_type), "-o", out_path] + module_list)

    @staticmethod
    def probeMnt(dir):
        assert os.path.isabs(dir) and not dir.endswith("/")
        dir = dir + "/"

        tlist = []
        for p in psutil.disk_partitions():
            if dir.startswith(p.mountpoint):
                tlist.append(p)
        tlist.sort(key=lambda x: len(x.mountpoint))
        ret = tlist[-1]

        try:
            fs = subprocess.check_output(["grub-probe", "-t", "fs", "-d", ret.device], universal_newlines=True).rstrip("\n")
        except subprocess.CalledProcessError:
            fs = None

        try:
            fs_uuid = subprocess.check_output(["grub-probe", "-t", "fs", "-d", ret.device], universal_newlines=True).rstrip("\n")
        except subprocess.CalledProcessError:
            fs_uuid = None

        try:
            bios_hints = subprocess.check_output(["grub-probe", "-t", "bios_hints", "-d", ret.device], universal_newlines=True).rstrip("\n")
        except subprocess.CalledProcessError:
            bios_hints = ""

        try:
            efi_hints = subprocess.check_output(["grub-probe", "-t", "efi_hints", "-d", ret.device], universal_newlines=True).rstrip("\n")
        except subprocess.CalledProcessError:
            efi_hints = ""

        class Mnt:
            def __init__(self, dev, fs, fs_uuid, mnt_dir, mnt_opts, bios_hints, efi_hints):
                self.dev = dev
                self.fs = fs
                self.fs_uuid = fs_uuid
                self.mnt_dir = mnt_dir
                self.mnt_opts = mnt_opts
                self.bios_hints = bios_hints
                self.efi_hints = efi_hints

        return Mnt(ret.device, fs, fs_uuid, ret.mountpoint, ret.opts, bios_hints, efi_hints)

    @staticmethod
    def escape(in_str):
        return in_str.replace('\'', "'\\''")
