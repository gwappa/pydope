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

from .. import defaults as _defaults
from .. import status as _status
from .. import parsing as _parsing

def validate_type(type):
    if type is None:
        return None
    elif isinstance(type, str):
        return _parsing.session.type(type)
    elif hasattr(type, "__iter__"):
        return tuple(validate_type(t) for t in type)
    elif callable(type):
        return type
    else:
        raise ValueError(f"unexpected type for session-type specification: {type.__class__}")

def validate_date(date):
    if date is None:
        return None
    elif isinstance(date, _datetime.datetime):
        return date
    elif isinstance(date, str):
        return _parsing.session.date(date)
    elif hasattr(date, "__iter__"):
        return tuple(validate_date(d) for d in date)
    elif all(hasattr(date, attr) for attr in ("keys", "values", "items")):
        if all((key in date.keys()) for key in ("year", "month", "day")):
            return _datetime.datetime(year=date["year"],
                                      month=date["month"],
                                      day=date["day"])
    else:
        raise ValueError(f"unexpected type for session-date specification: {date.__class__}")

def validate_index(index):
    if index is None:
        return None
    elif isinstance(index, int):
        return index
    elif isinstance(index, (str, bytes)):
        return _parsing.session.index(index)
    elif hasattr(index, "__iter__"):
        return tuple(validate_index(i) for i in index)
    elif callable(index):
        return index
    else:
        raise ValueError(f"unexpected type for session-index specification: {index.__class__}")

class SessionSpec(_collections.namedtuple("_SessionSpec",
                  ("type", "date", "index"))):

    def __new__(cls, type=None, date=None, index=None):
        if (date is None) and (index is None):
            if type is None:
                return super(cls, SessionSpec).__new__(cls, type=None, date=None, index=None)
            else:
                # attempt name-based initialization
                try:
                    return cls(**_parsing.session.name(type))
                except ValueError:
                    pass # fallthrough
        return super(cls, SessionSpec).__new__(cls, type=validate_type(type),
                                  date=validate_date(date),
                                  index=validate_index(index))

    @classmethod
    def empty(cls):
        return cls(type=None, date=None, index=None)

    @classmethod
    def from_name(cls, name):
        """initializes the specification from a property formatted session name."""
        return cls(**_parsing.session.name(name))

    def __str__(self):
        return self.name

    def test(self, spec):
        """returns if another SessionSpec object
        matches the specification of this object."""
        raise NotImplementedError("SessionSpec.test()")

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

    def compute_write_status(self):
        return _status.combine(*[_status.compute_write_status(fld) \
                    for fld in self])

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
               default = _defaults["session.nospec.type"]
           return str(default)
       else:
           return self.type

    def _format_date(self, default=None):
       if self.date is None:
           if default is None:
               default = _defaults["session.nospec.date"]
           return str(default)
       else:
           return self.date.strftime(_parsing.session.DATE_FORMAT)

    def _format_index(self, digits=None, default=None):
       if digits is None:
           digits = _defaults["session.index.width"]
       if not isinstance(digits, int):
           raise ValueError(f"'digits' expected to be int, got {digits.__class__}")

       if self.index is None:
           if default is None:
               default = _defaults["session.nospec.index"]
           return str(default)
       else: # assumes int
           base = str(self.index)
           if len(base) > digits:
               raise ValueError(f"cannot represent session index '{self.index}' in a {digits}-digit number")
           return base.zfill(digits)
