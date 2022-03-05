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


import enum


class TargetType(enum.Enum):
    MOUNTED_HDD_DEV = enum.auto()            # hard-disk device
    PYCDLIB_OBJ = enum.auto()                # pycdlib object
    ISO_DIR = enum.auto()                    # directory containing files for a ISO


class TargetAccessMode(enum.Enum):
    R = enum.auto()
    W = enum.auto()
    RW = enum.auto()


class PlatformType(enum.Enum):
    I386_PC = "i386-pc"
    I386_EFI = "i386-efi"
    I386_QEMU = "i386-qemu"
    I386_COREBOOT = "i386-coreboot"
    I386_MULTIBOOT = "i386-multiboot"
    I386_IEEE1275 = "i386-ieee1275"
    I386_XEN = "i386-xen"
    I386_XEN_PVH = "i386-xen_pvh"
    X86_64_EFI = "x86_64-efi"
    X86_64_XEN = "x86_64_xen"
    ARM_UBOOT = "arm-uboot"
    ARM_COREBOOT = "arm-coreboot"
    ARM_EFI = enum.auto()                                   # FIXME
    ARM64_EFI = "arm64-efi"
    IA64_EFI = enum.auto()                                  # FIXME
    SPARC64_IEEE1275 = enum.auto()                          # FIXME
    POWERPC_IEEE1275 = enum.auto()                          # FIXME
    MIPS_ARC = enum.auto()                                  # FIXME
    MIPS_QEMU_MIPS = enum.auto()                            # FIXME
    MIPSEL_ARC = enum.auto()                                # FIXME
    MIPSEL_LOONGSON = enum.auto()                           # FIXME
    MIPSEL_QEMU_MIPS = enum.auto()                          # FIXME
    RISCV32_EFI = enum.auto()                               # FIXME
    RISCV64_EFI = enum.auto()                               # FIXME


class PlatformInstallInfo:

    class Status(enum.Enum):
        BOOTABLE = enum.auto()
        EXIST = enum.auto()
        NOT_EXIST = enum.auto()

    def __init__(self):
        self.status = None


#    MOUNTED_FDD_DEV = enum.auto()            # floppy device
#    MOUNTED_HDD_DEV_APPLE = enum.auto()      # apple device
#    APPLE_ISO_DIR = enum.auto()              # apple device
