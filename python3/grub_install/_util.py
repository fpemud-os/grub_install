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
import re
import shutil
import psutil
import pathlib
import filecmp
import subprocess


def force_rm(path):
    if os.path.islink(path):
        os.remove(path)
    elif os.path.isfile(path):
        os.remove(path)
    elif os.path.isdir(path):
        shutil.rmtree(path)
    elif os.path.lexists(path):
        os.remove(path)             # other type of file, such as device node
    else:
        pass                        # path does not exist, do nothing


def force_mkdir(path, clear=False):
    if os.path.islink(path):
        os.remove(path)
        os.mkdir(path)
    elif os.path.isfile(path):
        os.remove(path)
        os.mkdir(path)
    elif os.path.isdir(path):
        shutil.rmtree(path)
        os.mkdir(path)
    elif os.path.lexists(path):
        os.remove(path)             # other type of file, such as device node
        os.mkdir(path)
    else:
        os.mkdir(path)              # path does not exist


def rmdir_if_empty(path):
    if len(os.listdir(path)) == 0:
        os.rmdir(path)


def truncate_dir(path):
    for fn in os.listdir(path):
        force_rm(os.path.join(path, fn))


def mnt_probe(dir):
    assert os.path.isabs(dir) and not dir.endswith("/")
    dir = dir + "/"

    tlist = []
    for p in psutil.disk_partitions():
        if dir.startswith(p.mountpoint):
            tlist.append(p)
    tlist.sort(key=lambda x: len(x.mountpoint))
    ret = tlist[-1]

    out = subprocess.check_output(["blkid", tlist.device])
    m = re.search(r'\bUUID="(\S*)"\B', out, re.M)
    if m is not None:
        fsUuid = m.group(1)
    else:
        fsUuid = None

    class Mnt:
        def __init__(self, dev, mnt_pt, fs_name, fs_uuid, mnt_opts):
            self.dev = dev
            self.mnt_pt = mnt_pt
            self.fs_name = fs_name
            self.fs_uuid = fs_uuid
            self.mnt_opts = mnt_opts

    return Mnt(ret.device, ret.mountpoint, ret.fstype, fsUuid, ret.opts)


def compare_files(filepath1, filepath2):
    # don't use filecmp.cmp() directly
    # filecmp.dircmp is too complex, we created function compare_files() and compare_directories()
    return filecmp.cmp(filepath1, filepath2, shallow=False)


def compare_directories(dirpath1, dirpath2):
    ret1 = os.listdir(dirpath1)
    ret2 = os.listdir(dirpath2)
    if ret1 != ret2:
        return False
    for fn in ret1:
        if not filecmp.cmp(os.path.join(dirpath1, fn), os.path.join(dirpath2, fn), shallow=False):
            return False
    return True
