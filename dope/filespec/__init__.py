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
from ..core import SelectionStatus as _SelectionStatus

class FileSpec(_collections.namedtuple("_FileSpec",
                ("suffix", "trial", "run", "channel")), _SelectionStatus):
    DIGITS = 5

    def __new__(cls, suffix=None, trial=None, run=None, channel=None):
        return super(cls, FileSpec).__new__(cls, suffix=suffix, trial=trial, run=run, channel=channel)

    @classmethod
    def empty(cls):
        return FileSpec(suffix=None, trial=None, run=None, channel=None)

    @property
    def status(self):
        return self.compute_status(None)

    def compute_status(self, context=None):
        # TODO
        if context is None:
            unspecified = (((self.trial is None) and (self.run is None)),
                           self.channel is None,
                           self.suffix is None)
            if all(unspecified):
                return self.UNSPECIFIED
            elif any(callable(fld) for fld in self):
                return self.DYNAMIC
            elif any(unspecified):
                return self.MULTIPLE
            else:
                return self.SINGLE
        else:
            raise NotImplementedError("FileSpec.compute_status()")

    def compute_path(self, context):
        """context: Predicate"""
        return context.compute_domain_path() / self.format_name(context)

    def format_name(self, context, digits=None):
        """context: Predicate"""
        runtxt = self.format_run(digits=digits)
        chtxt  = self.format_channel(context)
        sxtxt  = self.format_suffix()
        return f"{context.subject}_{context.session.name}_{context.domain}{runtxt}{chtxt}{sxtxt}"

    def format_run(self, digits=None):
        if digits is None:
            digits = self.DIGITS
        if self.trial is None:
            if self.run is None:
                return ""
            else:
                return "_" + str(self.run).zfill(digits)
        else:
            return "_" + str(self.trial).zfill(digits)

    def format_channel(self, context):
        if self.channel is None:
            return ""
        elif isinstance(self.channel, str):
            return f"_{self.channel}"
        elif iterable(self.channel):
            return "_" + "-".join(self.channel)
        else:
            raise ValueError(f"cannot compute channel from: {self.channel}")

    def format_suffix(self):
        return self.suffix if self.suffix is not None else ""

    def with_values(self, **kwargs):
        spec = dict(**kwargs)
        for fld in self._fields:
            if fld not in spec.keys():
                spec[fld] = getattr(self, fld)
        return self.__class__(**spec)

    def cleared(self):
        return self.__class__()
