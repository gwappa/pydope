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
from .. import levels as _levels
from ..predicate import Predicate as _Predicate
from ..core import Container as _Container
from ..core import Selector as _Selector

def validate(spec, mode=None):
    """spec: pathlike or Predicate"""
    if not isinstance(spec, _Predicate):
        if spec is None:
            root = _pathlib.Path()
        else:
            try:
                root = _pathlib.Path(spec)
            except TypeError:
                raise ValueError(f"Dataset can only be initialized by a path-like object or a Predicate, not {spec.__class__}")
        spec = _Predicate(root=root)
    if mode is not None:
        spec = spec.with_values(mode=_modes.validate(mode))
    return spec

class Dataset(_Container):
    """a container class representing the dataset root directory."""

    def __init__(self, spec, mode=None):
        """spec: pathlike or Predicate"""
        self._spec = validate(spec, mode=mode)
        if (self._spec.mode == _modes.READ) and (not self._spec.root.exists()):
            raise FileNotFoundError(f"dataset directory does not exist: {self._spec.root}")

    def __getattr__(self, name):
        if name == "_path":
            return self._spec.root

    @property
    def subjects(self):
        from ..subject import Subject
        return _Selector(self._spec, _levels.SUBJECT, container=Subject)

    @property
    def sessions(self):
        from ..session import Session
        return self.in_tuple(Session(spec) for spec in self._spec.sessions)

    @property
    def domains(self):
        from ..domain import Domain
        return self.in_tuple(Domain(spec) for spec in self._spec.domains)

    @property
    def files(self):
        from ..datafile import DataFile
        return self.in_tuple(DataFile(spec) for spec in self._spec.files)

    def __getitem__(self, key):
        return self.subjects[key]
