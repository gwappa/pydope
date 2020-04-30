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

    def __new__(cls, suffix=None, trial=None, run=None, channel=None):
        return super(cls, FileSpec).__new__(cls, suffix=suffix, trial=trial, run=run, channel=channel)

    @classmethod
    def empty(cls):
        return FileSpec(suffix=None, trial=None, run=None, channel=None)

    @property
    def status(self):
        # FIXME: read dynamically??
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

    def with_values(self, **kwargs):
        spec = dict(**kwargs)
        for fld in self._fields:
            if fld not in spec.keys():
                spec[fld] = getattr(self, fld)
        return self.__class__(**spec)

    def cleared(self):
        return self.__class__()
