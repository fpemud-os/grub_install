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
import shutil
import psutil
import subprocess
from ._util import force_mkdir
from ._const import PlatformType


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
    BOOT_MACHINE_BPB_START	= 0x3

    # The offset of the end of BPB (BIOS Parameter Block).
    BOOT_MACHINE_BPB_END = 0x5a

    # The offset of BOOT_DRIVE_CHECK.
    BOOT_MACHINE_DRIVE_CHECK = 0x66

    # The offset of a magic number used by Windows NT.
    BOOT_MACHINE_WINDOWS_NT_MAGIC = 0x1b8

    # The offset of the start of the partition table.
    BOOT_MACHINE_PART_START = 0x1be

    # The offset of the end of the partition table.
    BOOT_MACHINE_PART_END = 0x1fe

    KERNEL_I386_PC_LINK_ADDR = 0x9000

    # Offset of field holding no reed solomon length.
    KERNEL_I386_PC_NO_REED_SOLOMON_LENGTH = 0x14

    @staticmethod
    def getGrubFsName(fs_name):
        if fs_name == "vfat":
            return "fat"
        return fs_name

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
        GRUB_ENVBLK_MESSAGE	= "# WARNING: Do not edit this file by tools other than grub-editenv!!!\n"

        tmpName = name + ".new"

        with open(tmpName, "w") as f:
            f.write(GRUB_ENVBLK_SIGNATURE)
            f.write(GRUB_ENVBLK_MESSAGE)
            f.write("#" * (DEFAULT_ENVBLK_SIZE - len(GRUB_ENVBLK_SIGNATURE) - len(GRUB_ENVBLK_MESSAGE)))

        os.rename(tmpName, name)

    @staticmethod
    def copyPlatformFiles(platform_type, source, grub_dir):
        # install modules and friends
        platDirSrc = os.path.join(source.get_platform_dir(platform_type))
        platDirDst = os.path.join(grub_dir, platform_type.value)
        force_mkdir(platDirDst, clear=True)
        for fn in os.listdir(platDirSrc):
            if fn.endswith(".mod"):
                shutil.copy(os.path.join(platDirSrc, fn), os.path.join(platDirDst, fn))
        for fn in ["efiemu32.o", "efiemu64.o", "moddep.lst", "command.lst", "fs.lst", "partmap.lst", "parttool.lst", "video.lst", "crypto.lst", "terminal.lst", "modinfo.sh"]:
            shutil.copy(os.path.join(platDirSrc, fn), os.path.join(platDirDst, fn))

    @staticmethod
    def copyLocaleFiles(source, grub_dir, locales):
        assert source.supports(source.CAP_NLS)
        dstDir = os.path.join(grub_dir, "locales")
        force_mkdir(dstDir, clear=True)
        if locales == "*":
            for ln, fullfn in source.get_all_locale_files():
                shutil.copy(fullfn, os.path.join(dstDir, "%s.mo" % (ln)))
        else:
            for x in locales:
                shutil.copy(source.get_locale_file(x), "%s.mo" % (x))

    @staticmethod
    def copyFontFiles(source, grub_dir, fonts):
        assert source.supports(source.CAP_FONTS)
        dstDir = os.path.join(grub_dir, "fonts")
        force_mkdir(dstDir, clear=True)
        if fonts == "*":
            for fn, fullfn in source.get_all_font_files():
                shutil.copy(fullfn, dstDir)
        else:
            for x in fonts:
                shutil.copy(source.get_font_file(x), dstDir)

    @staticmethod
    def copyThemeFiles(source, grub_dir, themes):
        assert source.supports(source.CAP_THEMES)
        dstDir = os.path.join(grub_dir, "themes")
        force_mkdir(dstDir, clear=True)
        if themes == "*":
            for tn, fullfn in source.get_all_theme_directories():
                shutil.copytree(fullfn, dstDir)
        else:
            for x in themes:
                shutil.copytree(source.get_theme_directory(x), dstDir)

    @staticmethod
    def makeCoreImage(source, platform_type, load_cfg_file, mkimage_target, module_list, out_path):
        subprocess.check_call(["grub-mkimage", "-c", load_cfg_file, "-O", mkimage_target, "-d", source.get_platform_dir(platform_type), "-o", out_path] + module_list)

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
            if bios_hints == "":
                bios_hints = None
        except subprocess.CalledProcessError:
            bios_hints = ""

        try:
            efi_hints = subprocess.check_output(["grub-probe", "-t", "efi_hints", "-d", ret.device], universal_newlines=True).rstrip("\n")
        except subprocess.CalledProcessError:
            efi_hints = ""

        class Mnt:
            def __init__(self, dev, fs, fs_uuid, mnt_pt, mnt_opts, bios_hints, efi_hints):
                self.dev = dev
                self.fs = fs
                self.fs_uuid = fs_uuid
                self.mnt_pt = mnt_pt
                self.mnt_opts = mnt_opts
                self.bios_hints = bios_hints
                self.efi_hints = efi_hints

        return Mnt(ret.device, fs, fs_uuid, ret.mountpoint, ret.opts, bios_hints, efi_hints)

