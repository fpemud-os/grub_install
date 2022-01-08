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


class GrubInstaller:

    def __init__(self, base_dir=None, source_dir=None, locale_dir=None):
        self._baseDir = base_dir if base_dir is not None else "/"
        self._sourceDir = source_dir if source_dir is not None else os.path.join(base_dir, "usr", "lib", "grub")
        self._localeDir = locale_dir if locale_dir is not None else os.path.join(base_dir, "usr", "share", "locale")

    def install(self):
        pass

    def check(self):
        pass




# arm-coreboot
# arm-coreboot-vexpress
# arm-coreboot-veyron
# arm-efi
# arm-uboot

# arm64-efi

# i386-coreboot
# i386-efi
# i386-ieee1275,
# i386-multiboot
# i386-pc
# i386-pc-eltorito
# i386-pc-pxe
# i386-qemu
# i386-xen
# i386-xen_pvh

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

# x86_64-efi
# x86_64-xen

