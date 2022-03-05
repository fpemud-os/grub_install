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

from enum import Enum, auto


class CheckCode(Enum):
    TRIVIAL = auto()
    ESP_SIZE_INVALID = auto()
    SWAP_NOT_ENABLED = auto()
    SWAP_SIZE_TOO_SMALL = auto()


def checkErrorCallback(error_callback, check_code, *kargs):
    if error_callback is None:
        return

    errDict = {
        CheckCode.TRIVIAL: (1, "{0}"),
        CheckCode.ESP_SIZE_INVALID: (1, "Invalid size for ESP partition \"{0}\"."),
        CheckCode.SWAP_NOT_ENABLED: (0, "Swap is not enabled."),
        CheckCode.SWAP_SIZE_TOO_SMALL: (1, "Swap {0} size is too small."),
    }

    argNum, fstr = errDict[check_code]
    assert len(kargs) == argNum
    error_callback(check_code, fstr % kargs)


class ParseError(Exception):
    pass


class InstallError(Exception):
    pass


class CheckError(Exception):
    pass
