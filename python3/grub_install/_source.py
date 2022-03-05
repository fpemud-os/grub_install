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
import shutil
from ._util import truncate_dir
from ._const import PlatformType
from ._errors import SourceError


class Source:

    CAP_NLS = 1
    CAP_FONTS = 2
    CAP_THEMES = 3

    def __init__(self, base_dir=None):
        if base_dir is None:
            base_dir = "/"

        self._libDir = os.path.join(base_dir, "usr", "lib", "grub")
        self._shareDir = os.path.join(base_dir, "usr", "share", "grub")
        self._localeDir = os.path.join(base_dir, "usr", "share", "locale")
        self._themesDir = os.path.join(base_dir, "usr", "share", "grub", "themes")

        # check
        if not os.path.isdir(self._libDir):
            raise SourceError("directory %s does not exist" % (self._libDir))
        if not os.path.isdir(self._shareDir):
            raise SourceError("directory %s does not exist" % (self._shareDir))
        self.get_all_platform_directories()

    def supports(self, key):
        if key == self.CAP_NLS:
            return os.path.exists(self._localeDir)
        elif key == self.CAP_FONTS:
            return len(glob.glob(os.path.join(self._shareDir, "*.pf2"))) > 0
        elif key == self.CAP_THEMES:
            return os.path.exists(self._themesDir)
        else:
            assert False

    def get_all_platform_directories(self):
        ret = dict()
        for fullfn in glob.glob(os.path.join(self._libDir, "*")):
            n = os.path.basename(fullfn)
            try:
                ret[PlatformType(n)] = fullfn
            except ValueError:
                raise SourceError("invalid platform directory %s" % (fullfn))
        return ret

    def get_platform_directory(self, platform_type):
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
        ret = dict()
        for fullfn in glob.glob(os.path.join(self._shareDir, "*.pf2")):
            n = os.path.basename(fullfn)
            n = n.replace(".pf2", "")
            ret[n] = fullfn
        return ret

    def get_font_file(self, font_name):
        assert self.supports(self.CAP_FONTS)
        ret = os.path.join(self._shareDir, font_name + ".pf2")
        assert os.path.exists(ret)
        return ret

    def get_default_font(self):
        assert self.supports(self.CAP_FONTS)
        return "unicode"

    def get_all_theme_directories(self):
        assert self.supports(self.CAP_THEMES)
        ret = dict()
        for fullfn in glob.glob(os.path.join(self._themesDir, "*")):
            n = os.path.basename(fullfn)
            ret[n] = fullfn
        return ret

    def get_theme_directory(self, theme_name):
        assert self.supports(self.CAP_THEMES)
        ret = os.path.join(self._themesDir, theme_name)
        assert os.path.isdir(ret)
        return ret

    def get_default_theme(self):
        assert self.supports(self.CAP_THEMES)
        return "starfield"

    def copy_to(self, dest_dir):
        assert os.path.isdir(dest_dir)

        os.makedirs(os.path.join(dest_dir, "usr", "lib", "grub"), exist_ok=True)
            



        shutil.copytree()




