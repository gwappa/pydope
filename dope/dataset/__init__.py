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
from ..core import Selector as _Selector

def verify_spec(spec, mode=None):
    """spec: pathlike or Predicate"""
    if not isinstance(spec, _Predicate):
        try:
            root = _pathlib.Path(spec)
        except TypeError:
            raise ValueError(f"DataRoot can only be initialized by a path-like object or a Predicate, not {spec.__class__}")
        spec = _Predicate(mode=_modes.verify(mode), root=root)
    return spec

class Dataset(_Container):
    """a container class representing the dataset root directory."""

    @classmethod
    def is_valid_path(cls, path):
        """returns if the specified file path
        represents a valid dataroot."""
        return False

    @classmethod
    def compute_path(cls, parentpath, key):
        raise NotImplementedError(f"cannot use compute_path() for Dataset")

    @classmethod
    def from_parent(cls, parentspec, name):
        raise NotImplementedError(f"cannot use from_parent() for Dataset")

    def __init__(self, spec, mode=_modes.READ):
        """spec: pathlike or Predicate"""
        self._spec = verify_spec(spec, mode=mode)
        if (self._spec.mode == _modes.READ) and (not self._spec.root.exists()):
            raise FileNotFoundError(f"dataset directory does not exist: {self._spec.root}")

    @property
    def path(self):
        return self._spec.root

    @property
    def subjects(self):
        from ..subject import Subject
        return _Selector(self._spec, Subject)

    def __getitem__(self, key):
        return self.subjects[key]
