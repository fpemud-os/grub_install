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


import abc


class Target(abc.ABC):

    def __init__(self, name):
        assert name in ["arm-coreboot", "arm-coreboot-vexpress", "arm-coreboot-veyron", "arm-uboot"] or \
               name in ["arm64-efi"] or \
               name in ["i386-coreboot", "i386-efi", "i386-ieee1275", "i386-multiboot", "i386-pc", "i386-pc-eltorito", "i386-pc-pxe", "i386-qemu", "i386-xen", "i386-xen_pvh"] or \
               name in ["x86_64-efi", "x86_64_xen"]

        self._name = name
        # self.allow_floppy = XXX   # --allow-floppy
        # self.themes = XXX         # --themes=THEMES
        # self.locales = XXX        # --locales=LOCALES
        # self.pubkey = XXX         # --pubkey=FILE
        # self.modules = XXX        # --install-modules=MODULES
        # self.fonts = XXX          # --fonts=FONTS
        # self.compress = XXX       # --compress=no|xz|gz|lzo

        # we won't support:
        # 1. 

    @property
    def name(self):
        return self._name



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





# static struct
# {
#   const char *cpu;
#   const char *platform;
# } platforms[GRUB_INSTALL_PLATFORM_MAX] =
#   {
#     [GRUB_INSTALL_PLATFORM_I386_PC] =          { "i386",    "pc"        },
#     [GRUB_INSTALL_PLATFORM_I386_EFI] =         { "i386",    "efi"       },
#     [GRUB_INSTALL_PLATFORM_I386_QEMU] =        { "i386",    "qemu"      },
#     [GRUB_INSTALL_PLATFORM_I386_COREBOOT] =    { "i386",    "coreboot"  },
#     [GRUB_INSTALL_PLATFORM_I386_MULTIBOOT] =   { "i386",    "multiboot" },
#     [GRUB_INSTALL_PLATFORM_I386_IEEE1275] =    { "i386",    "ieee1275"  },
#     [GRUB_INSTALL_PLATFORM_X86_64_EFI] =       { "x86_64",  "efi"       },
#     [GRUB_INSTALL_PLATFORM_I386_XEN] =         { "i386",    "xen"       },
#     [GRUB_INSTALL_PLATFORM_X86_64_XEN] =       { "x86_64",  "xen"       },
#     [GRUB_INSTALL_PLATFORM_I386_XEN_PVH] =     { "i386",    "xen_pvh"   },
#     [GRUB_INSTALL_PLATFORM_MIPSEL_LOONGSON] =  { "mipsel",  "loongson"  },
#     [GRUB_INSTALL_PLATFORM_MIPSEL_QEMU_MIPS] = { "mipsel",  "qemu_mips" },
#     [GRUB_INSTALL_PLATFORM_MIPS_QEMU_MIPS] =   { "mips",    "qemu_mips" },
#     [GRUB_INSTALL_PLATFORM_MIPSEL_ARC] =       { "mipsel",  "arc"       },
#     [GRUB_INSTALL_PLATFORM_MIPS_ARC] =         { "mips",    "arc"       },
#     [GRUB_INSTALL_PLATFORM_SPARC64_IEEE1275] = { "sparc64", "ieee1275"  },
#     [GRUB_INSTALL_PLATFORM_POWERPC_IEEE1275] = { "powerpc", "ieee1275"  },
#     [GRUB_INSTALL_PLATFORM_IA64_EFI] =         { "ia64",    "efi"       },
#     [GRUB_INSTALL_PLATFORM_ARM_EFI] =          { "arm",     "efi"       },
#     [GRUB_INSTALL_PLATFORM_ARM64_EFI] =        { "arm64",   "efi"       },
#     [GRUB_INSTALL_PLATFORM_ARM_UBOOT] =        { "arm",     "uboot"     },
#     [GRUB_INSTALL_PLATFORM_ARM_COREBOOT] =     { "arm",     "coreboot"  },
#     [GRUB_INSTALL_PLATFORM_RISCV32_EFI] =      { "riscv32", "efi"       },
#     [GRUB_INSTALL_PLATFORM_RISCV64_EFI] =      { "riscv64", "efi"       },
#   }; 
