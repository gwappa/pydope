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
    """`spec` may be a path-like object or a Predicate.
    by default, dope.modes.READ is selected for `mode`."""
    if not isinstance(spec, _Predicate):
        # assumes path-like object
        try:
            path = _pathlib.Path(spec).resolve()
        except TypeError:
            raise ValueError(f"Subject can only be initialized by a path-like object or a Predicate, not {spec.__class__}")
        sessdir = path.parent
        subdir  = sessdir.parent
        dsdir   = subdir.parent
        rootdir = dsdir.parent
        spec = _Predicate(mode=_modes.verify(mode),
                          root=rootdir,
                          dataset=dsdir.name,
                          subject=subdir.name,
                          sessionspec=_SessionSpec(sessdir.name),
                          domain=path.name)
    return spec.with_values(mode=_modes.verify(mode))

class Domain(_Container):
    """a container class representing a domain directory."""
    @classmethod
    def is_valid_path(cls, path):
        """returns if the specified file path
        represents a valid domain."""
        return (not path.name.startswith(".")) and (path.is_dir())

    @classmethod
    def from_parent(cls, parentspec, key):
        return cls(parentspec.with_values(domain=key))

    def __init__(self, spec, mode=None):
        """`spec` may be a path-like object or a Predicate.
        by default, dope.modes.READ is selected for `mode`."""
        spec = verify_spec(spec, mode=mode)
        level = spec.level
        if level in (spec.ROOT, spec.SUBJECT, spec.SESSION):
            raise ValueError(f"cannot specify a session from the predicate level: '{level}'")
        elif level != spec.DOMAIN:
            spec = _Predicate(mode=spec.mode,
                              root=spec.root,
                              dataset=spec.dataset,
                              subject=spec.subject,
                              session=spec.session,
                              domain=spec.domain)

        self._spec = spec
        self._path = spec.path
        if (self._spec.mode == _modes.READ) and (not self._path.exists()):
            raise FileNotFoundError(f"domain directory does not exist: {self._path}")

    @property
    def path(self):
        return self._path

    @property
    def dataset(self):
        from ..dataset import Dataset
        return Dataset(self._spec.as_dataset())

    @property
    def subject(path):
        from ..subject import Subject
        return Subject(self._spec.as_subject())

    @property
    def session(path):
        from ..session import Session
        return Session(self._spec.as_session())

    @property
    def files(self):
        from ..datafile import DataFile
        return _Selector(self._spec, DataFile)

    def __getitem__(self, key):
        return self.files[key]
