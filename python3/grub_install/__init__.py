#!/usr/bin/env python3

# grub_install - grub installation
#
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

"""
grub_install

@author: Fpemud
@license: GPLv3 License
@contact: fpemud@sina.com
"""


__author__ = "fpemud@sina.com (Fpemud)"
__version__ = "0.0.1"


from ._core import Source
from ._core import Target
from ._core import Utils

from ._core import get_supported_storage_layouts
from ._core import get_current_storage_layout
from ._core import detect_and_mount_storage_layout
from ._core import create_and_mount_storage_layout

from ._errors import CheckCode

from ._errors import StorageLayoutError
from ._errors import StorageLayoutCreateError
from ._errors import StorageLayoutAddDiskError
from ._errors import StorageLayoutRemoveDiskError
from ._errors import StorageLayoutParseError
