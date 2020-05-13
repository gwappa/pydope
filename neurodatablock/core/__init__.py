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
from .. import levels as _levels

class Container: # TODO: better renamed as `Context`?
    """a reference to data based on a specific Predicate."""
    _spec = None

    @staticmethod
    def newinstance(spec):
        lev = spec.level
        if lev == _levels.ROOT:
            from ..dataset import Dataset
            return Dataset(spec)
        elif lev == _levels.SUBJECT:
            from ..subject import Subject
            return Subject(spec)
        elif lev == _levels.SESSION:
            from ..session import Session
            return Session(spec)
        elif lev == _levels.DOMAIN:
            from ..domain import Domain
            return Domain(spec)
        else:
            from ..datafile import Datafile
            return Datafile(spec)

    @property
    def root(self):
        return self._spec.root

    def with_mode(self, mode):
        """changes the I/O mode of this container."""
        return self.__class__(self._spec, mode=mode)

class Selector:
    """an adaptor class used to select from child components."""
    def __init__(self, spec, level, container=None):
        self._spec  = spec
        self._path  = spec.compute_path()
        self._level = _levels.validate(level)
        self._container = container

    def __len__(self):
        return len(self.__iter__())

    def __iter__(self):
        if not self._path.exists():
            raise FileNotFoundError(f"path does not exist: {parent}")
        specs = self._spec.iterate_at_level(self._level)
        if self._container is not None:
            return tuple(self._container(spec) for spec in specs)
        else:
            return tuple(Container.newinstance(spec) for spec in specs)

    def _compose_child(self, name):
        values = {self._level: name}
        return self._spec.with_values(**values)

    def __getitem__(self, key):
        child = self._compose_child(key)
        if self._spec.mode == _modes.READ:
            if not self._path.exists():
                raise FileNotFoundError(f"container path does not exist: {parent}")
            if not child.compute_path().exists():
                raise FileNotFoundError(f"item does not exist: {child}")
        if self._container is not None:
            return self._container(child)
        else:
            return Container.newinstance(child)

class FormattingWarning(UserWarning):
    pass
