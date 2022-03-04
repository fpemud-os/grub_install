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
from ._const import TargetType, TargetAccessMode, PlatformType, PlatformInstallStatus


class Target(abc.ABC):

    def __init__(self, target_type, target_access_mode, **kwargs):
        assert isinstance(target_type, TargetType)
        assert isinstance(target_access_mode, TargetAccessMode)

        self._targetType = target_type
        self._mode = target_access_mode

        # target specific variables
        if self._targetType == TargetType.MOUNTED_FDD_DEV:
            assert False
        elif self._targetType == TargetType.MOUNTED_HDD_DEV:
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
            if self._targetType == TargetType.MOUNTED_FDD_DEV:
                assert False
            elif self._targetType == TargetType.MOUNTED_HDD_DEV:
                _Common.init_platforms(self)
                for pt in self._platforms:
                    pass
            elif self._targetType == TargetType.PYCDLIB_OBJ:
                assert False                                                    # FIXME
            elif self._targetType == TargetType.ISO_DIR:
                _Common.init_platforms(self)
                for pt in self._platforms:
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

    def get_platform_install_status(self, platform_type):
        assert isinstance(platform_type, PlatformType)
        return self._platforms.get(platform_type, PlatformInstallStatus.NOT_EXIST)

    def install_platform(platform_type, source):
        assert self.get_platform_install_status(platform_type) != PlatformInstallStatus.BOOTABLE
        assert isinstance(source, Source)

        if self._targetType == TargetType.MOUNTED_FDD_DEV:
            assert False
        elif self._targetType == TargetType.MOUNTED_HDD_DEV:
            _Common.install_platform(self, platform_type, source)
        elif self._targetType == TargetType.PYCDLIB_OBJ:
            # FIXME
            assert False
        elif self._targetType == TargetType.ISO_DIR:
            _Common.install_platform(self, platform_type, source)
        else:
            assert False

    def remove_platform(platform_type):
        assert isinstance(platform_type, PlatformType)
        
        if self._targetType == TargetType.MOUNTED_FDD_DEV:
            assert False
        elif self._targetType == TargetType.MOUNTED_HDD_DEV:
            _Common.remove_platform(self, platform_type)
        elif self._targetType == TargetType.PYCDLIB_OBJ:
            # FIXME
            assert False
        elif self._targetType == TargetType.ISO_DIR:
            _Common.remove_platform(self, platform_type)
        else:
            assert False

    def check(auto_fix=False):
        if self._targetType == TargetType.MOUNTED_FDD_DEV:
            assert False
        elif self._targetType == TargetType.MOUNTED_HDD_DEV:
            _Common.check(self, auto_fix)
        elif self._targetType == TargetType.PYCDLIB_OBJ:
            # FIXME
            assert False
        elif self._targetType == TargetType.ISO_DIR:
            _Common.check(self, auto_fix)
        else:
            assert False

    def check_with_source(source, auto_fix=False):
        assert isinstance(source, Source)

        if self._targetType == TargetType.MOUNTED_FDD_DEV:
            assert False
        elif self._targetType == TargetType.MOUNTED_HDD_DEV:
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
                        p._platforms[pt] = None

    def install_platform(p, platform_type, source):
        assert False

    def remove_platform(p, platform_type, source):
        assert False

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


