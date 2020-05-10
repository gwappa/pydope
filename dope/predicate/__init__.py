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

from . import parse as _parse

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


class Predicate(_collections.namedtuple("_Predicate",
                ("mode",
                 "root",
                 "subject",
                 "session",
                 "domain",
                 "file")),
                _SelectionStatus, _DataLevels):
    """a predicate specification to search the datasets."""

    def __new__(cls,
                mode=None,
                root=None,
                subject=None,
                session=None,
                domain=None,
                file=None,
                **specs):
        return super(cls, Predicate).__new__(cls,
                        _modes.verify(mode),
                        _parse.root(root),
                        _parse.item_default(subject, "subject"),
                        _parse.session(session=session, **specs),
                        _parse.item_default(domain, "domain"),
                        _parse.file(file=file, **specs))

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
        else:
            return self.ROOT

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
                spec[fld] = _parse.session(**newvalues, default=default)
            elif fld == "file":
                spec[fld] = _parse.file(**newvalues, default=default)
            else:
                spec[fld] = newvalues.get(fld, default)
        return self.__class__(**spec)

    def as_subject(self, mode=None):
        return self.__class__(mode=self.mode if mode is None else mode,
                              root=self.root,
                              subject=self.subject)

    def as_session(self, mode=None):
        return self.__class__(mode=self.mode if mode is None else mode,
                              root=self.root,
                              subject=self.subject,
                              session=self.session)

    def as_domain(self, mode=None):
        return self.__class__(mode=self.mode if mode is None else mode,
                              root=self.root,
                              subject=self.subject,
                              session=session,
                              domain=domain)

    def compute_status(self):
        """returns a string representation for the status of specification."""
        if any(callable(item) for item in self):
            return self.DYNAMIC

        lev = self.level

        status = compute_selection_status(self.root)
        if (lev == self.ROOT) or (status != self.SINGLE):
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
        elif level == self.SUBJECT:
            return self.compute_subject_path()
        elif level == self.SESSION:
            return self.session.compute_path(self)
        elif level == self.DOMAIN:
            return self.compute_domain_path()
        else:
            # status == FILE
            return self.file.compute_path(self)

    def compute_subject_path(self):
        return self.root / self.subject

    def compute_domain_path(self):
        return self.session.compute_path(self) / self.domain
