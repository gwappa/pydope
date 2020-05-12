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

import pathlib as _pathlib
import datetime as _datetime

from .. import modes as _modes

class Container: # TODO: better renamed as `Context`?
    """a reference to data based on a specific Predicate."""
    _spec = None

    @classmethod
    def is_valid_path(cls, path):
        """returns if the specified file path
        represents a valid file for this container type."""
        raise NotImplementedError(f"not implemented: {cls}.is_valid_path()")

    @classmethod
    def compute_path(cls, parentpath, key):
        """computes a path for a container from the parent path and `key`.
        `key` is typically a string, but may be e.g. SessionSpec."""
        raise NotImplementedError(f"not implemented: {cls}.compute_child_path()")

    @classmethod
    def from_parent(cls, parentspec, key):
        """creates a container from the parent spec and `key`.
        `key` is typically a string, but may be e.g. SessionSpec."""
        raise NotImplementedError(f"not implemented: {cls}.from_path()")

    def with_mode(self, mode):
        """changes the I/O mode of this container."""
        return self.__class__(self._spec.with_values(mode=mode))

class Selector:
    """an adaptor class used to select from subdirectories."""
    def __init__(self, spec, delegate):
        self._spec     = spec
        self._path     = spec.path
        self._delegate = delegate

    def __iter__(self):
        if not self._path.exists():
            raise FileNotFoundError(f"path does not exist: {parent}")
        return tuple(sorted(self._delegate.from_parent(self._spec, path.name) \
                            for path in self._path.iterdir() \
                            if self._delegate.is_valid_path(path)))

    def __getitem__(self, key):
        child = self._delegate.compute_path(self._path, key)
        if self._spec.mode == _modes.READ:
            if not self._path.exists():
                raise FileNotFoundError(f"container path does not exist: {parent}")
            if not child.exists():
                raise FileNotFoundError(f"item does not exist: {child}")
        return self._delegate.from_parent(self._spec, key)

    @property
    def path(self):
        return self._path

class SelectionStatus:
    NONE        = "none"
    UNSPECIFIED = "unspecified"
    SINGLE      = "single"
    MULTIPLE    = "multiple"
    DYNAMIC     = "dynamic"

    @staticmethod
    def compute_write_status(spec):
        if isinstance(spec, (int, str, bytes, _pathlib.Path, _datetime.datetime)):
            return SelectionStatus.SINGLE
        elif spec is None:
            return SelectionStatus.UNSPECIFIED
        elif hasattr(spec, "__iter__"):
            size = len(spec)
            if size == 1:
                return SelectionStatus.SINGLE
            elif size == 0:
                return SelectionStatus.NONE
            else:
                return SelectionStatus.MULTIPLE
        elif callable(spec):
            return SelectionStatus.DYNAMIC
        else:
            raise ValueError(f"unexpected specification: {spec}")

    @staticmethod
    def compute_read_status(iterated):
        size = len(iterated)
        if size == 0:
            return _SelectionStatus.NONE
        elif size == 1:
            return _SelectionStatus.SINGLE
        else:
            return _SelectionStatus.MULTIPLE

    @staticmethod
    def combine(*stats):
        if len(stats) == 0:
            return SelectionStatus.UNSPECIFIED
        elif len(stats) == 1:
            return stats[0]
        else:
            for status in (SelectionStatus.UNSPECIFIED,
                           SelectionStatus.NONE,
                           SelectionStatus.DYNAMIC,
                           SelectionStatus.MULTIPLE): # must be in this order
                if status in stats:
                    return status
            invalid = tuple(stat for stat in stats if stat != SelectionStatus.SINGLE)
            if len(invalid) > 0:
                raise ValueError(f"unexpected status string(s): {invalid}")
            return SelectionStatus.SINGLE

class DataLevels:
    ROOT    = "root"
    SUBJECT = "subject"
    SESSION = "session"
    DOMAIN  = "domain"
    FILE    = "file"

class FormattingWarning(UserWarning):
    pass
