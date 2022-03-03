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
