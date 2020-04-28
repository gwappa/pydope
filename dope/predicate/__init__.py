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
from .. import modes as _modes
from ..sessionspec import SessionSpec as _SessionSpec
from ..filespec import FileSpec as _FileSpec

class Predicate(_collections.namedtuple("_Predicate",
                ("mode", "root", "dataset", "subject", "sessionspec",
                 "domain", "filespec"))):
    """a predicate specification to search the datasets."""
    DEFAULT_MODE = _modes.READ

    # constants for representing specification status
    NONE    = "none"
    PARTIAL = "partial"
    ROOT    = "root"
    DATASET = "dataset"
    SUBJECT = "subject"
    SESSION = "session"
    DOMAIN  = "domain"
    FILE    = "file"

    def __new__(cls, **specs):
        vlaues = dict()
        for fld in cls._fields:
            values[fld] = specs.get(fld, None)
        if values["mode"] is None:
            values["mode"] = cls.DEFAULT_MODE
        if values["sessionspec"] is None:
            values["sessionspec"] = _SessionSpec.empty()
        if values["filespec"] is None:
            values["filespec"] = _FileSpec.empty()
        return super(cls, Predicate).__new__(cls, **values)

    @property
    def status(self):
        """returns a string representation for the status of specification."""
        if self.root is None:
            return self.NONE

        elif any(callable(item) for item in self):
            return self.PARTIAL

        elif self.dataset is None: # possibly representing a data-root
            if self.subject is not None:
                return self.PARTIAL
            elif self.sessionspec.status != _SessionSpec.UNSPECIFIED:
                return self.PARTIAL
            elif self.domain is not None:
                return self.PARTIAL
            elif self.filespec.status != _FileSpec.UNSPECIFIED:
                return self.PARTIAL
            return self.ROOT

        elif self.subject is None: # possibly representing a dataset
            if self.sessionspec.status != _SessionSpec.UNSPECIFIED:
                return self.PARTIAL
            elif self.domain is not None:
                return self.PARTIAL
            elif self.filespec.status != _FileSpec.UNSPECIFIED:
                return self.PARTIAL
            return self.DATASET

        elif self.sessionspec.status == _SessionSpec.UNSPECIFIED: # possibly representing a subject
            if self.domain is not None:
                return self.PARTIAL
            elif self.filespec.status != _FileSpec.UNSPECIFIED:
                return self.PARTIAL
            return self.SUBJECT

        elif self.domain is None: # possibly representing a session
            if self.filespec.status != _FileSpec.UNSPECIFIED:
                return self.PARTIAL
            return self.SESSION

        elif self.filespec.status == _FileSpec.UNSPECIFIED: # represents a domain
            return self.DOMAIN

        elif self.filespec.status == _FileSpec.SINGLE:
            return self.FILE

        else:
            return self.PARTIAL

    @property
    def session(self):
        return self.sessionspec.name

    @property
    def path(self):
        """returns a simulated path object if and only if this Predicate
        can represent a single file.

        it does not necessarily mean that the returned value points to an
        existing file.

        raises ValueError in case a path cannot be computed.
        """
        status = self.status
        msg    = None
        if status is None:
            msg = "data-root remains unspecified"
        elif status == self.PARTIAL:
            msg = "specification is partial"
        if msg is not None:
            raise ValueError(f"cannot compute a path: {msg}")

        if status == self.ROOT:
            return self.root
        elif status == self.DATASET:
            return self.root / self.dataset
        elif status == self.SUBJECT:
            return self.root / self.dataset / self.subject
        elif status == self.SESSION:
            return self.root / self.dataset / self.subject / self.sessionspec.name
        elif status == self.DOMAIN:
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
            spec[fld] = newvalues.get(fld, default)
        return self.__class__(**spec)

    def cleared(self):
        """returns another Predicate where everything (except for
        `mode` and `root`) is cleared."""
        return self.with_values(clear=True)
