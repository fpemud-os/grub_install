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
import psutil
import pathlib
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
    def getModuleListAndHnits(platform_type, mnt):
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

        return (moduleList, hints)

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

    @staticmethod
    def makeCoreImage(source, platform_type, load_cfg_file_content, mkimage_target, module_list, tmp_dir=None):
        with tempfile.TemporaryDirectory(dir=tmp_dir) as tmpdir:
            loadCfgFile = os.path.join(tmpdir, "load.cfg")
            coreImgFile = os.pat.join(tmpdir, "core.img")
            with open(loadCfgFile, "w") as f:
                f.write(load_cfg_file_content)
            subprocess.check_call(["grub-mkimage", "-c", loadCfgFile, "-O", mkimage_target, "-d", source.get_platform_directory(platform_type), "-o", coreImgFile] + module_list)
            return pathlib.Path(coreImgFile).read_bytes()

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
