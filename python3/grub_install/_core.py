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


class Source:

    def __init__(self, base_dir=None, grub_lib_dir=None, locale_dir=None):
        if base_dir is None:
            base_dir = "/"
        if grub_lib_dir is None:
            grub_lib_dir = os.path.join(base_dir, "usr", "lib", "grub")
        if locale_dir is None:
            locale_dir = os.path.join(base_dir, "usr", "share", "locale")

        self._libDir = os.path.realpath(grub_lib_dir)
        self._localeDir = os.path.realpath(locale_dir)


class Target:

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
    def platforms(self):
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


def install(source, target, platforms):
    pass

def check(source, target, auto_fix=False):
    pass







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
