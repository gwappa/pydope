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
import warnings as _warnings

from .. import modes as _modes
from .. import parsing as _parsing
from ..core import SelectionStatus as _SelectionStatus
from ..core import DataLevels as _DataLevels
from ..core import FormattingWarning as _FormattingWarning
from ..sessionspec import SessionSpec as _SessionSpec
from ..filespec import FileSpec as _FileSpec

from . import validate as _validate

class Predicate(_collections.namedtuple("_Predicate",
                ("mode",
                 "root",
                 "subject",
                 "session",
                 "domain",
                 "file")),
                _SelectionStatus, _DataLevels):
    """a predicate to search the datasets.
    the base class is also used to represent the specification
    of concrete subjects, sessions etc."""

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
                        _validate.root(root),
                        _validate.item_default(subject, "subject"),
                        _validate.session(session=session, **specs),
                        _validate.item_default(domain, "domain"),
                        _validate.file(file=file, **specs))

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

    @property
    def subjects(self):
        """scans the dataset for existing subjects as Predicate objects."""
        return self.iterate_at_level(self.SUBJECT)

    @property
    def sessions(self):
        """scans the dataset for existing sessions as Predicate objects."""
        return self.iterate_at_level(self.SESSION)

    @property
    def domains(self):
        """scans the dataset for existing domains as Predicate objects."""
        return self.iterate_at_level(self.DOMAIN)

    @property
    def files(self):
        """scans the dataset for existing data files as Predicate objects."""
        return self.iterate_at_level(self.FILE)

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

    def as_dataset(self, mode=None):
        return self.__class__(mode=self.mode if mode is None else _modes.verify(mode),
                              root=self.root)

    def as_subject(self, mode=None):
        return self.__class__(mode=self.mode if mode is None else _modes.verify(mode),
                              root=self.root,
                              subject=self.subject)

    def as_session(self, mode=None):
        return self.__class__(mode=self.mode if mode is None else _modes.verify(mode),
                              root=self.root,
                              subject=self.subject,
                              session=self.session)

    def as_domain(self, mode=None):
        return self.__class__(mode=self.mode if mode is None else _modes.verify(mode),
                              root=self.root,
                              subject=self.subject,
                              session=session,
                              domain=domain)

    def compute_status(self):
        """returns a string representation for the status of specification."""
        if self.mode == _modes.READ:
            return self._read_status()
        else:
            return self._write_status()

    def _write_status(self):
        if any(callable(item) for item in self):
            return self.DYNAMIC

        lev = self.level
        if lev == self.ROOT:
            return _SelectionStatus.SINGLE

        status = _SelectionStatus.compute_write_status(self.subject)
        if (lev == self.SUBJECT) or (status != _SelectionStatus.SINGLE):
            return status

        status = self.session.compute_write_status()
        if (lev == self.SESSION) or (status != _SelectionStatus.SINGLE):
            return status

        status = _SelectionStatus.compute_write_status(self.domain)
        if (lev == self.DOMAIN) or (status != _SelectionStatus.SINGLE):
            return status

        return self.file.compute_write_status()

    def _read_status(self):
        """uses iterate() functionality to check selection status."""
        lev = self.level
        if lev == self.ROOT:
            return self.SINGLE
        elif lev == self.SUBJECT:
            return _SelectionStatus.compute_read_status(self.subjects)
        elif lev == self.SESSION:
            return _SelectionStatus.compute_read_status(self.sessions)
        elif lev == self.DOMAIN:
            return _SelectionStatus.compute_read_status(self.domains)
        elif lev == self.FILE:
            return _SelectionStatus.compute_read_status(self.files)

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

    def _test_name_default(self, attr, name):
        """returns True if the given name matches with the specification
        of `attr` in this Predicate.

        it is assumed that the `name` is already validated to conform."""
        pred = getattr(self, attr)
        if pred is None:
            return True
        elif isinstance(pred, str):
            return (pred == name)
        elif hasattr(pred, "__contains__"):
            return (name in pred)
        elif callable(pred):
            return pred(name)
        else:
            raise RuntimeError(f"unexpected predicate for '{attr}': {pred}")

    def _test_subject_name(self, subject):
        """returns True if the given subject name matches with the specification
        in this Predicate."""
        return self._test_name_default(self, 'subject', subject)

    def _test_session_spec(self, session):
        """returns True if the given SessionSpec matches with the specification
        in this Predicate."""
        pred = self.session
        if pred is None:
            return True
        elif isinstance(pred, _SessionSpec):
            return pred.test(session)
        elif callable(pred):
            return pred(session)
        else:
            raise RuntimeError(f"unexpected session specification in a predicate: {pred}")

    def _test_domain_name(self, domain):
        """returns True if the given domain name matches with the specification
        in this Predicate."""
        return self._test_name_default(self, 'domain', domain)

    def _test_datafile_spec(self, file):
        """returns True if the given FileSpec matches with the specification
        in this Predicate."""
        pred = self.file
        if pred is None:
            return True
        elif isinstance(pred, _FileSpec):
            return pred.test(file)
        elif callable(pred):
            return pred(file)
        else:
            raise RuntimeError(f"unexpected data-file specification in a predicate: {pred}")

    def iterate_at_level(self, level):
        """scans files using this Predicate context.
        returns a tuple consisting of SINGLE-selected Predicates.
        """
        if level == _DataLevels.ROOT:
            return (self,)
        elif level == _DataLevels.SUBJECT:
            return tuple(self.with_values(subject=path.name) \
                    for path in self._iter_subject_directories())
        elif level == _DataLevels.SESSION:
            return tuple(self.with_values(subject=path.parent.name,
                                          session=_SessionSpec(path.name)) \
                        for path in self._iter_session_directories())
        elif level == _DataLevels.DOMAIN:
            return tuple(self.with_values(subject=path.parent.parent.name,
                                          session=_SessionSpec(path.parent.name),
                                          domain=path.name)) \
                        for path in self._iter_domain_directories())
        elif level == _DataLevels.FILE:
            return tuple(self.with_values(subject=path.parent.parent.parent.name,
                                          session=_SessionSpec(path.parent.parent.name),
                                          domain=path.parent.name,
                                          file=_FileSpec.from_path(path)))
        else:
            raise ValueError(f"unknown data level to iterate: '{level}'")

    def _iter_subject_directories(self):
        """scans subject directories using this Predicate context.
        returns a tuple consisting of single-subject directories."""
        ret = []
        for subdir in sorted(self.root.iterdir()):
            subject = _parsing.subject.match(subdir.name)
            if subject is None:
                continue
            elif self._test_subject_name(subject) == True:
                ret.append(subdir)
        return tuple(ret)

    def _iter_session_directories(self):
        """scans session directories using this Predicate context.
        returns a tuple consisting of single-session directories."""
        ret = []
        for subdir in self._iter_subject_directories():
            for sessdir in sorted(subdir.iterdir()):
                session = _parsing.subject.match(sessdir.name)
                if session is None:
                    continue
                elif self._test_session_spec(_SessionSpec(**session)) == True:
                    ret.append(sessdir)
        return tuple(ret)

    def _iter_domain_directories(self):
        """scans domain directories using this Predicate context.
        returns a tuple consisting of single-domain directories."""
        ret = []
        for sessdir in self._iter_session_directories():
            for domdir in sorted(sessdir.iterdir()):
                domain = _parsing.domain.match(domdir.name)
                if domain is None:
                    continue
                elif self._test_domain_name(domain) == True:
                    ret.append(domdir)
        return tuple(ret)

    def _iter_datafiles(self):
        """scans individual data file using this Predicate context.
        returns a tuple consisting of Path objects."""
        ret = []
        for domdir in self._iter_domain_directories():
            sessdir = domdir.parent
            subdir  = sessdir.parent

            subject = subdir.name
            session = sessdir.name
            domain  = domdir.name
            for path in sorted(domdir.iterdir()):
                spec = _parsing.file.match(path.name)
                if spec is None:
                    continue
                elif (spec["subject"] != subject) \
                    or (_SessionSpec(**spec["session"]).name != session) \
                    or (spec["domain"] != domain):
                    _warnings.warn(f"incoherent file name found in '{subject}/{session}/{domain}': {path.name}",
                                    _FormattingWarning)
                elif self._test_datafile_spec(_FileSpec(**spec["filespec"])) == True:
                    ret.append(path)
        return tuple(ret)
