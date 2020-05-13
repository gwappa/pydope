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
    """`spec` may be a path-like object or a Predicate.
    by default, dope.modes.READ is selected for `mode`."""
    if not isinstance(spec, _Predicate):
        # assumes path-like object
        try:
            path = _pathlib.Path(spec).resolve()
        except TypeError:
            raise ValueError(f"Subject can only be initialized by a path-like object or a Predicate, not {spec.__class__}")
        spec = _Predicate(root=path.parent.parent,
                          dataset=path.parent.name,
                          subject=path.name)
    if mode is not None:
      spec = spec.with_values(mode=_modes.validate(mode))
    return spec

class Subject(_Container):
    """a container class representing a subject directory."""

    def __init__(self, spec, mode=None):
        """`spec` may be a path-like object or a Predicate.
        by default, dope.modes.READ is selected for `mode`."""
        spec = validate(spec, mode=mode)
        level = spec.level
        if level in (_levels.ROOT,):
            raise ValueError(f"cannot specify a subject from the predicate level: '{level}'")
        elif level != _levels.SUBJECT:
            spec = _Predicate(mode=spec.mode,
                              root=spec.root,
                              dataset=spec.dataset,
                              subject=spec.subject)

        self._spec = spec
        self._path = spec.compute_path()
        if (self._spec.mode == _modes.READ) and (not self._path.exists()):
            raise FileNotFoundError(f"subject directory does not exist: {self._path}")

    @property
    def name(self):
        return self._spec.subject

    @property
    def dataset(self):
        from ..dataset import Dataset
        return Dataset(self._spec.as_dataset())

    @property
    def sessions(self):
        from ..session import Session
        return _Selector(self._spec, _levels.SESSION, container=Session)

    @property
    def domains(self):
        from ..domain import Domain
        return self.in_tuple(Domain(spec) for spec in self._spec.domains)

    @property
    def files(self):
        from ..datafile import DataFile
        return self.in_tuple(DataFile(spec) for spec in self._spec.files)

    def __getitem__(self, key):
        return self.sessions[key]
