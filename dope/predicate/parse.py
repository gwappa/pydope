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
from ..sessionspec import SessionSpec as _SessionSpec
from ..filespec import FileSpec as _FileSpec

def root(root):
    if root is not None:
        return _pathlib.Path(root)
    else:
        return _pathlib.Path()

def item_default(value, label="item"):
    if value is None:
        return None
    elif isinstance(value, str):
        return value
    elif callable(value):
        return value
    else:
        raise ValueError(f"unexpected {label} specification: '{value}'")

def session(session=None,
            session_type=None,
            session_date=None,
            session_index=None,
            default=None,
            **specs):
    if session is not None:
        if isinstance(session, str):
            return _SessionSpec(session)
        elif isinstance(session, _SessionSpec):
            return session
        elif all(hasattr(session, attr) for attr in ("keys", "values", "items")):
            return _SessionSpec(**session)
        elif hasattr(session, "__iter__"):
            return _SessionSpec(*session)
        elif callable(session):
            return session
        else:
            raise ValueError(f"unexpected session specification: '{session}'")
    else:
        if default is None:
            default = _SessionSpec()
        sspec = dict()
        if session_type is not None:
            sspec["type"] = session_type
        if session_date is not None:
            sspec["date"] = session_date
        if session_index is not None:
            sspec["index"] = session_index
        return default.with_values(**sspec)

def file(file=None,
         suffix=None,
         trial=None,
         run=None,
         channel=None,
         default=None,
         **specs):
    if file is not None:
        if isinstance(file, str):
            return _FileSpec(file)
        elif isinstance(file, _FileSpec):
            return file
        elif all(hasattr(file, attr) for attr in ("keys", "values", "items")):
            return _FileSpec(**file)
        elif hasattr(file, "__iter__"):
            return _FileSpec(*file)
        elif callable(file):
            return file
        else:
            raise ValueError(f"unexpected file specification: '{file}'")
    else:
        if default is None:
            default = _FileSpec()
        fspec = dict()
        if suffix is not None:
            fspec["suffix"]  = suffix
        if trial is not None:
            fspec["trial"]   = trial
        if run is not None:
            fspec["run"]     = run
        if channel is not None:
            fspec["channel"] = channel
        return default.with_values(**fspec)
