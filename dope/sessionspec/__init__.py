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

import re as _re
import collections as _collections
import datetime as _datetime

from .. import defaults
from ..core import SelectionStatus as _SelectionStatus
from .. import parsing as _parsing

class SessionSpec(_collections.namedtuple("_SessionSpec",
                  ("type", "date", "index")), _SelectionStatus):

    def __new__(cls, type=None, date=None, index=None):
        if (date is None) and (index is None):
            if type is None:
                return super(cls, SessionSpec).__new__(cls, type=None, date=None, index=None)
            else:
                # attempt name-based initialization
                try:
                    return cls(**_parsing.parse_session_name(type))
                except ValueError:
                    pass # fallthrough
        return super(cls, SessionSpec).__new__(cls, type=_parsing.parse_session_type(type),
                                  date=_parsing.parse_session_date(date),
                                  index=_parsing.parse_session_index(index))

    @classmethod
    def empty(cls):
        return cls(type=None, date=None, index=None)

    @classmethod
    def from_name(cls, name):
        """initializes the specification from a property formatted session name."""
        return cls(**_parsing.parse_session_name(name))

    def __str__(self):
        return self.name

    @property
    def status(self):
        return self.compute_status(None)

    @property
    def name(self):
        """returns the session specification as it appears on directory names."""
        return self.format()

    def with_values(self, **kwargs):
        spec = dict(**kwargs)
        for fld in self._fields:
            if fld not in spec.keys():
                spec[fld] = getattr(self, fld)
        return self.__class__(**spec)

    def cleared(self):
        return self.__class__(None,None,None)

    def compute_status(self, context=None):
        # TODO
        if context is None:
            stat = tuple(fld is None for fld in self)
            if all(stat):
                return self.UNSPECIFIED
            elif any(stat):
                return self.MULTIPLE
            else:
                return self.SINGLE
        else:
            raise NotImplementedError("SessionSpec.compute_status()")

    def compute_path(self, context):
        """context: Predicate"""
        return context.compute_subject_path() / self.name

    def format(self,
               digits=None,
               default_type=None,
               default_date=None,
               default_index=None):
        return f"{self._format_type(default=default_type)}" + \
               f"{self._format_date(default=default_date)}" + \
               f"-{self._format_index(default=default_index)}"

    def _format_type(self, default=None):
       if self.type is None:
           if default is None:
               default = defaults["session.nospec.type"]
           return str(default)
       else:
           return self.type

    def _format_date(self, default=None):
       if self.date is None:
           if default is None:
               default = defaults["session.nospec.date"]
           return str(default)
       else:
           return self.date.strftime(_parsing.SESSION_DATE_FORMAT)

    def _format_index(self, digits=None, default=None):
       if digits is None:
           digits = defaults["session.index.width"]
       if not isinstance(digits, int):
           raise ValueError(f"'digits' expected to be int, got {digits.__class__}")

       if self.index is None:
           if default is None:
               default = defaults["session.nospec.index"]
           return str(default)
       else: # assumes int
           base = str(self.index)
           if len(base) > digits:
               raise ValueError(f"cannot represent session index '{self.index}' in a {digits}-digit number")
           return base.zfill(digits)
