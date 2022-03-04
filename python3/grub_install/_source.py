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
from platform import platform
from ._const import PlatformType


class Source:

    def __init__(self, base_dir=None, grub_lib_dir=None, locale_dir=None):
        if base_dir is None:
            base_dir = "/"

        if grub_lib_dir is None:
            self._libDir = os.path.join(base_dir, "usr", "lib", "grub")
        else:
            self._libDir = grub_lib_dir
        assert os.path.isdir(self._libDir)

        if locale_dir is None:
            self._localeDir = os.path.join(base_dir, "usr", "share", "locale")
        else:
            self._localeDir = locale_dir
        assert os.path.isdir(self._localeDir)

        self._platforms = []
        for fn in os.listdir(self._libDir):
            for pt in PlatformType:
                if fn == pt.value:
                    self._platforms.append(pt)

    @property
    def platforms(self):
        return self._platforms

    def get_platform_dir(self, platform_type):
        assert platform_type in self._platforms
        return os.path.join(self._libDir, platform_type.value)

    def copy_to(self, platforms, dest_dir):
        # FIXME
        assert False
