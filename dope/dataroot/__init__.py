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

from .. import modes as _modes
from ..predicate import Predicate as _Predicate
from ..core import Container as _Container

class DataRoot(_Container):
    """a container class representing the data root directory."""

    @classmethod
    def is_valid_path(cls, path):
        """returns if the specified file name
        represents a valid name for this container type."""
        return True

    @classmethod
    def from_path(cls, path, parentspec):
        raise NotImplementedError(f"cannot use from_path() for DataRoot")

    def __init__(self, spec, mode=_modes.READ):
        """spec: pathlike or Predicate"""
        if not isinstance(spec, _Predicate):
            # assumes path-like object
            try:
                root = _pathlib.Path(spec)
            except TypeError:
                raise ValueError(f"DataRoot can only be initialized by a path-like object or a Predicate, not {spec.__class__}")
            spec = _Predicate(mode=mode, root=root)
        # isinstance(spec, Predicate) == True
        self._spec = spec
        if (self._spec.mode == _modes.READ) and (not self._spec.root.exists()):
            raise FileNotFoundError(f"data-root does not exist: {self._spec.root}")

    @property
    def datasets(self):
        return Selector(self._spec, _Container)

    def __getitem__(self, key):
        return self.datasets[key]
