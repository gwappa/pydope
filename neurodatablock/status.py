#
# MIT License
#
# Copyright (c) 2020 Keisuke Sehara
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

"""keywords used to represent selection status of a predicate."""

import pathlib as _pathlib
import datetime as _datetime

NONE        = "none"
UNSPECIFIED = "unspecified"
SINGLE      = "single"
MULTIPLE    = "multiple"
DYNAMIC     = "dynamic"

def compute_write_status(spec):
    if isinstance(spec, (int, str, bytes, _pathlib.Path, _datetime.datetime)):
        return SINGLE
    elif spec is None:
        return UNSPECIFIED
    elif hasattr(spec, "__iter__"):
        size = len(spec)
        if size == 1:
            return SINGLE
        elif size == 0:
            return NONE
        else:
            return MULTIPLE
    elif callable(spec):
        return DYNAMIC
    else:
        raise ValueError(f"unexpected specification: {spec}")

def compute_read_status(iterated):
    size = len(iterated)
    if size == 0:
        return NONE
    elif size == 1:
        return SINGLE
    else:
        return MULTIPLE

def combine(*stats):
    if len(stats) == 0:
        return UNSPECIFIED
    elif len(stats) == 1:
        return stats[0]
    else:
        for status in (UNSPECIFIED,
                       NONE,
                       DYNAMIC,
                       MULTIPLE): # must be in this order
            if status in stats:
                return status
        invalid = tuple(stat for stat in stats if stat != SINGLE)
        if len(invalid) > 0:
            raise ValueError(f"unexpected status string(s): {invalid}")
        return SINGLE
