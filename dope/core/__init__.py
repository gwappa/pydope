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

from .. import modes as _modes

class Container:
    """a reference to data based on a specific Predicate."""
    _spec = None

    @classmethod
    def is_valid_path(cls, path):
        """returns if the specified file name
        represents a valid name for this container type."""
        return False

    @classmethod
    def from_path(cls, path, parentspec):
        raise NotImplementedError(f"not implemented: {cls}.from_path()")

    def with_mode(self, mode):
        """changes the I/O mode of this container."""
        return self.__class__(self._spec.with_values(mode=mode))

class Selector:
    """an adaptor class used to select from subdirectories."""
    def __init__(self, spec, baseclass):
        self._spec = spec
        self._cls  = baseclass

    def __iter__(self):
        parent = self._spec.path
        if not parent.exists():
            raise FileNotFoundError(f"path does not exist: {parent}")
        return tuple(self._cls.from_path(path, self._spec) for path in parent.iterdir() \
                    if self._cls.is_valid_path(path))

    def __getitem__(self, key):
        parent = self._spec.path
        child = parent / key
        if self._spec.mode == _modes.READ:
            if not parent.exists():
                raise FileNotFoundError(f"container path does not exist: {parent}")
            if not child.exists():
                raise FileNotFoundError(f"item does not exist: {child}")
        return self._cls.from_path(child, self._spec)

class Specification:
    UNSPECIFIED = "unspecified"
    SINGLE      = "single"
    MULTIPLE    = "multiple"
    DYNAMIC     = "dynamic"
