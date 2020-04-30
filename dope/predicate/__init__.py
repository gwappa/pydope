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

import collections as _collections
import pathlib as _pathlib

from .. import modes as _modes
from ..core import SelectionStatus as _SelectionStatus
from ..core import DataLevels as _DataLevels
from ..sessionspec import SessionSpec as _SessionSpec
from ..filespec import FileSpec as _FileSpec

def compute_selection_status(spec):
    """returns the status of root/dataset/subject/domain selection."""
    if isinstance(spec, (str, bytes, _pathlib.Path)):
        return _SelectionStatus.SINGLE
    elif spec is None:
        return _SelectionStatus.UNSPECIFIED
    elif callable(spec):
        return _SelectionStatus.DYNAMIC
    elif iterable(spec):
        size = len(spec)
        if size == 1:
            return _SelectionStatus.SINGLE
        elif size == 0:
            return _SelectionStatus.NONE
        else:
            return _SelectionStatus.MULTIPLE
    else:
        raise ValueError(f"unexpected specification: {spec}")

def compute_sessionspec(specs, default=None):
    if "sessionspec" in specs.keys():
        return _SessionSpec(*specs["sessionspec"])
    elif "session" in specs.keys():
        return _SessionSpec(specs["session"])
    else:
        if default is None:
            default = _SessionSpec()
        sspec = dict((k.replace("session",""), v) for k, v in specs.items() \
                     if k.startswith("session"))
        return default.with_values(**sspec)

def compute_filespec(specs, default=None):
    if "filespec" in specs.keys():
        return _FileSpec(*specs["filespec"])
    else:
        if default is None:
            default = _FileSpec()
        return default

class Predicate(_collections.namedtuple("_Predicate",
                ("mode", "root", "dataset", "subject", "sessionspec",
                 "domain", "filespec")),
                _SelectionStatus, _DataLevels):
    """a predicate specification to search the datasets."""
    DEFAULT_MODE = _modes.READ

    def __new__(cls, *args, **specs):
        values = dict()
        offset = 0
        for fld in cls._fields:
            if fld == "sessionspec":
                values[fld] = compute_sessionspec(specs)
            elif fld in specs.keys():
                values[fld] = specs[fld]
            elif len(args) > offset:
                values[fld] = args[offset]
                offset += 1
            else:
                values[fld] = None
        if values["mode"] is None:
            values["mode"] = cls.DEFAULT_MODE
        if values["filespec"] is None:
            values["filespec"] = _FileSpec.empty()
        if values["root"] is not None:
            values["root"] = _pathlib.Path(values["root"])
        return super(cls, Predicate).__new__(cls, **values)

    @property
    def level(self):
        """returns a string representation for the 'level' of specification."""
        if self.filespec.status != _FileSpec.UNSPECIFIED:
            return self.FILE
        elif self.domain is not None:
            return self.DOMAIN
        elif self.sessionspec.status != _SessionSpec.UNSPECIFIED:
            return self.SESSION
        elif self.subject is not None:
            return self.SUBJECT
        elif self.dataset is not None:
            return self.DATASET
        elif self.root is not None:
            return self.ROOT
        else:
            return self.NA

    @property
    def status(self):
        """returns a string representation for the status of specification."""
        if any(callable(item) for item in self):
            return self.DYNAMIC

        lev = self.level
        if lev == self.NA:
            return self.UNSPECIFIED

        for spec, lv in ((self.root, self.ROOT),
                         (self.dataset, self.DATASET),
                         (self.subject, self.SUBJECT)):
            status = compute_selection_status(spec)
            if (lev == lv) or (status != self.SINGLE):
                return status

        status = self.sessionspec.status
        if (lev == self.SESSION) or (status != self.SINGLE):
            return status

        status = compute_selection_status(self.domain)
        if (lev == self.DOMAIN) or (status != self.SINGLE):
            return status

        return self.filespec.status

    @property
    def session(self):
        return self.sessionspec.name

    @property
    def session_name(self):
        return self.sessionspec.name

    @property
    def session_index(self):
        return self.sessionspec.index

    @property
    def session_type(self):
        return self.sessionspec.type

    @property
    def session_date(self):
        return self.sessionspec.date

    @property
    def path(self):
        """returns a simulated path object if and only if this Predicate
        can represent a single file.

        it does not necessarily mean that the returned value points to an
        existing file.

        raises ValueError in case a path cannot be computed.
        """
        level  = self.level
        status = self.status
        if status != self.SINGLE:
            raise ValueError(f"cannot compute a path: not specifying a single condition (status: '{status}')")

        if level == self.ROOT:
            return self.root
        elif level == self.DATASET:
            return self.root / self.dataset
        elif level == self.SUBJECT:
            return self.root / self.dataset / self.subject
        elif level == self.SESSION:
            return self.root / self.dataset / self.subject / self.sessionspec.name
        elif level == self.DOMAIN:
            return self.root / self.dataset / self.subject / self.sessionspec.name / self.domain
        else:
            # status == FILE
            return self.filespec.get_path(self)

    def with_values(self, clear=False, **newvalues):
        """specifying 'clear=True' will fill all values
        (but `mode` and `root`) with None unless
        explicitly specified."""
        spec = dict()
        for fld in self._fields:
            if (clear == False) or (fld in ("mode", "root")):
                default = getattr(self, fld)
            else:
                default = None
            if fld == "sessionspec":
                spec[fld] = compute_sessionspec(newvalues, default)
            elif fld == "filespec":
                spec[fld] = compute_filespec(newvalues, default)
            else:
                spec[fld] = newvalues.get(fld, default)
        return self.__class__(**spec)

    def cleared(self):
        """returns another Predicate where everything (except for
        `mode` and `root`) is cleared."""
        return self.with_values(clear=True)
