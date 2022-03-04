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
from ._const import PlatformType, TargetType


class Target(abc.ABC):

    def __init__(self, target_type, target_access_mode, **kwargs):
        assert isinstance(target_type, TargetType)
        assert isinstance(target_access_mode, TargetAccessMode)

        self._targetType = target_type
        self._mode = target_access_mode

        if self._targetType == TargetType.MOUNTED_FDD_DEV:
            assert False
        elif self._targetType == TargetType.MOUNTED_HDD_DEV:
            assert False
        elif self._targetType == TargetType.PYCDLIB_OBJ:
            assert self._mode in [TargetAccessMode.R, TargetAccessMode.W]
            assert False
        elif self._targetType == TargetType.ISO_DIR:
            assert False
        else:
            assert False

    @property
    def target_type(self):
        return self._targetType

    @property
    def target_access_mode(self):
        return self._mode

    @property
    @abc.abstractmethod
    def platforms(self):
        pass

    @abc.abstractmethod
    def get_platform_status(self, platform_type):
        pass

    @abc.abstractmethod
    def install_platform(platform_type, source):
        pass

    @abc.abstractmethod
    def remove_platform(platform_type, source):
        pass

    @abc.abstractmethod
    def check(auto_fix=False):
        pass

    @abc.abstractmethod
    def check_with_source(source, auto_fix=False):
        pass



class TargetCommon(Target):

    # self.allow_floppy = XXX   # --allow-floppy
    # self.themes = XXX         # --themes=THEMES
    # self.locales = XXX        # --locales=LOCALES
    # self.pubkey = XXX         # --pubkey=FILE
    # self.modules = XXX        # --install-modules=MODULES
    # self.fonts = XXX          # --fonts=FONTS
    # self.compress = XXX       # --compress=no|xz|gz|lzo

    # we won't support:
    # 1. 


    def __init__(self, boot_dir_path, hdd_dev=None):
        assert boot_dir_path is not None
        assert hdd_dev is not None

        self._path = boot_dir_path
        self._grubPath = os.path.join(self._path, "grub")
        self._hdd = hdd_dev

    @property
    def boot_dir_path(self):
        return self._path

    @property
    def supported_platforms(self):
        ret = []
        if os.path.isdir(self._grubPath):
            for fn in os.listdir(self._grubPath):
                for pt in PlatformType:
                    if fn == pt.value:
                        ret.append(pt)
        return ret
















class BootDir:

    def __init__(self, path, base_dir=None, grub_lib_dir=None, locale_dir=None):
        assert path is not None
        if base_dir is None:
            base_dir = "/"
        if grub_lib_dir is None:
            grub_lib_dir = os.path.join(base_dir, "usr", "lib", "grub")
        if locale_dir is None:
            locale_dir = os.path.join(base_dir, "usr", "share", "locale")

        self._path = os.path.realpath(path)
        self._grubPath = os.path.join(self._path, "grub")
        self._libDir = os.path.realpath(grub_lib_dir)
        self._localeDir = os.path.realpath(locale_dir)

    @property
    def path(self):
        return self._path

    @property
    def targets(self):
        ret = []

        if not os.path.isdir(self._grubPath):
            return ret

        for fn in os.listdir(self._grubPath):
            if fn in ["locale", "fonts", "themes"]:
                continue
            if not os.path.isdir(os.path.join(self._grubPath, fn)):
                continue
            ret.append(fn)

        return ret

    def install(self, target, target_info):
        pass

    def check(self, auto_fix=False):
        pass












class Target_i386_pc(TargetCommon):

    """This target needs to install boot code into harddisk boot sector"""

    def write_boot_code(self, hdd_dev):
        pass






-        assert name in ["arm-coreboot", "arm-coreboot-vexpress", "arm-coreboot-veyron", "arm-uboot"] or \
-               name in ["arm64-efi"] or \
-               name in ["i386-coreboot", "i386-efi", "i386-ieee1275", "i386-multiboot", "i386-pc", "i386-pc-eltorito", "i386-pc-pxe", "i386-qemu", "i386-xen", "i386-xen_pvh"] or \
-               name in ["x86_64-efi", "x86_64_xen"]


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


