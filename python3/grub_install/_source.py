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
import glob
from platform import platform
from ._const import PlatformType


class Source:

    CAP_NLS = 1
    CAP_FONTS = 2
    CAP_THEMES = 3

    def __init__(self, base_dir=None):
        if base_dir is None:
            base_dir = "/"

        self._libDir = os.path.join(base_dir, "usr", "lib", "grub")
        assert os.path.isdir(self._libDir)

        self._shareDir = os.path.join(base_dir, "usr", "share", "grub")
        assert os.path.isdir(self._shareDir)

        self._localeDir = os.path.join(base_dir, "usr", "share", "locale")

        self._themesDir = os.path.join(base_dir, "usr", "share", "grub", "themes")

        self._platforms = []
        for fn in os.listdir(self._libDir):
            for pt in PlatformType:
                if fn == pt.value:
                    self._platforms.append(pt)

    @property
    def platforms(self):
        return self._platforms

    def supports(self, key):
        if key == self.CAP_NLS:
            return os.path.exists(self._localeDir)
        elif key == self.CAP_FONTS:
            return len(glob.glob(os.path.join(self._shareDir, "*.pf2"))) > 0
        elif key == self.CAP_THEMES:
            return os.path.exists(self._themesDir)
        else:
            assert False

    def get_platform_dir(self, platform_type):
        assert platform_type in self._platforms
        return os.path.join(self._libDir, platform_type.value)

    def get_all_locale_files(self):
        assert self.supports(self.CAP_NLS)
        ret = dict()
        for fullfn in glob.glob(os.path.join(self._localeDir, "**/LC_MESSAGES/grub.mo")):
            n = fullfn.replace(self._localeDir, "")
            n = n[1:]
            n = n.split("/")[0]
            ret[n] = fullfn
        return ret

    def get_locale_file(self, locale_name):
        assert self.supports(self.CAP_NLS)
        ret = os.path.join(self._localeDir, locale_name, "LC_MESSAGES", "grub.mo")
        assert os.path.exists(ret)
        return ret

    def get_all_font_files(self):
        assert self.supports(self.CAP_FONTS)
        return glob.glob(os.path.join(self._shareDir, "*.pf2"))

    def get_font_file(self, font_name):
        assert self.supports(self.CAP_FONTS)
        ret = os.path.join(self._shareDir, font_name + ".pf2")
        assert os.path.exists(ret)
        return ret

    def get_default_font(self):
        assert self.supports(self.CAP_FONTS)
        ret = "unicode"
        assert os.path.exists(os.path.join(self._shareDir, ret + ".pf2"))
        return ret

    def get_all_theme_directories(self):
        assert self.supports(self.CAP_THEMES)
        return glob.glob(os.path.join(self._themesDir, "*"))

    def get_theme_directory(self, theme_name):
        assert self.supports(self.CAP_THEMES)
        ret = os.path.join(self._themesDir, theme_name)
        assert os.path.isdir(ret)
        return ret

    def get_default_theme(self):
        assert self.supports(self.CAP_THEMES)
        ret = "starfield"
        assert os.path.exists(os.path.join(self._themesDir, ret))
        return ret

    def copy_to(self, platforms, dest_dir):
        # FIXME
        assert False
