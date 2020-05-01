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

def compute_session(specs, default=None):
    if "session" in specs.keys():
        if isinstance(specs["session"], str):
            return _SessionSpec(specs["session"])
        else:
            return _SessionSpec(*specs["session"])
    else:
        if default is None:
            default = _SessionSpec()
        sspec = dict((k.replace("session_",""), v) for k, v in specs.items() \
                     if k.startswith("session_"))
        return default.with_values(**sspec)

def compute_file(specs, default=None):
    if "file" in specs.keys():
        if isinstance(specs["file"], str):
            return _FileSpec(specs["file"])
        else:
            return _FileSpec(*specs["file"])
    else:
        if default is None:
            default = _FileSpec()
        fspec = dict((k,v) for k, v in specs.items() \
                     if k in _FileSpec._fields)
        return default.with_values(**fspec)

class Predicate(_collections.namedtuple("_Predicate",
                ("mode", "root", "dataset", "subject", "session",
                 "domain", "file")),
                _SelectionStatus, _DataLevels):
    """a predicate specification to search the datasets."""

    def __new__(cls, *args, **specs):
        values = dict()
        offset = 0
        for fld in cls._fields:
            if fld == "session":
                values[fld] = compute_session(specs)
            elif fld == "file":
                values[fld] = compute_file(specs)
            elif fld in specs.keys():
                values[fld] = specs[fld]
            elif len(args) > offset:
                values[fld] = args[offset]
                offset += 1
            else:
                values[fld] = None
        values["mode"] = _modes.verify(values["mode"])
        if values["root"] is not None:
            values["root"] = _pathlib.Path(values["root"])
        return super(cls, Predicate).__new__(cls, **values)

    @property
    def level(self):
        """returns a string representation for the 'level' of specification."""
        if self.file.status != _FileSpec.UNSPECIFIED:
            return self.FILE
        elif self.domain is not None:
            return self.DOMAIN
        elif self.session.status != _SessionSpec.UNSPECIFIED:
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
        return self.compute_status()

    @property
    def session_name(self):
        return self.session.name

    @property
    def session_index(self):
        return self.session.index

    @property
    def session_type(self):
        return self.session.type

    @property
    def session_date(self):
        return self.session.date

    @property
    def trial(self):
        return self.file.trial

    @property
    def run(self):
        return self.file.run

    @property
    def channel(self):
        return self.file.channel

    @property
    def suffix(self):
        return self.file.suffix

    @property
    def path(self):
        return self.compute_path()

    @property
    def dataset_path(self):
        return self.compute_dataset_path()

    @property
    def subject_path(self):
        return self.compute_subject_path()

    @property
    def session_path(self):
        return self.session.compute_path(self)

    @property
    def domain_path(self):
        return self.compute_domain_path()

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

            if fld == "session":
                spec[fld] = compute_session(newvalues, default)
            elif fld == "file":
                spec[fld] = compute_file(newvalues, default)
            else:
                spec[fld] = newvalues.get(fld, default)
        return self.__class__(**spec)

    def cleared(self):
        """returns another Predicate where everything (except for
        `mode` and `root`) is cleared."""
        return self.__class__()

    def as_dataset(self, mode=None):
        return self.__class__(mode=self.mode if mode is None else mode,
                              root=self.root,
                              dataset=self.dataset)

    def as_subject(self, mode=None):
        return self.__class__(mode=self.mode if mode is None else mode,
                              root=self.root,
                              dataset=self.dataset,
                              subject=self.subject)

    def as_session(self, mode=None):
        return self.__class__(mode=self.mode if mode is None else mode,
                              root=self.root,
                              dataset=self.dataset,
                              subject=self.subject,
                              session=self.session)

    def as_domain(self, mode=None):
        return self.__class__(mode=self.mode if mode is None else mode,
                              root=self.root,
                              dataset=self.dataset,
                              subject=self.subject,
                              session=session,
                              domain=domain)

    def compute_status(self):
        """returns a string representation for the status of specification."""
        if any(callable(item) for item in self):
            return self.DYNAMIC

        lev = self.level
        if lev == self.NA:
            return self.UNSPECIFIED

        status = compute_selection_status(self.root)
        if (lev == self.ROOT) or (status != self.SINGLE):
            return status

        status = self.compute_dataset_status()
        if (lev == self.DATASET) or (status != self.SINGLE):
            return status

        status = self.compute_subject_status()
        if (lev == self.SUBJECT) or (status != self.SINGLE):
            return status

        status = self.session.compute_status(self)
        if (lev == self.SESSION) or (status != self.SINGLE):
            return status

        status = self.compute_domain_status()
        if (lev == self.DOMAIN) or (status != self.SINGLE):
            return status

        return self.file.compute_status(self)

    def compute_dataset_status(self):
        # TODO
        return compute_selection_status(self.dataset)

    def compute_subject_status(self):
        # TODO
        return compute_selection_status(self.subject)

    def compute_domain_status(self):
        # TODO
        return compute_selection_status(self.domain)

    def compute_path(self):
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
            return self.compute_dataset_path()
        elif level == self.SUBJECT:
            return self.compute_subject_path()
        elif level == self.SESSION:
            return self.session.compute_path(self)
        elif level == self.DOMAIN:
            return self.compute_domain_path()
        else:
            # status == FILE
            return self.file.compute_path(self)

    def compute_dataset_path(self):
        return self.root / self.dataset

    def compute_subject_path(self):
        return self.compute_dataset_path() / self.subject

    def compute_domain_path(self):
        return self.session.compute_path(self) / self.domain
