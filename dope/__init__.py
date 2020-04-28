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
import datetime

defaults = {
    "session.index.width":  3,
    "session.nospec.type":  "<any>",
    "session.nospec.date":  "<any-date>",
    "session.nospec.index": "<any>",
}

from .sessionspec import SessionSpec


class Predicate(_collections.namedtuple("_Predicate",
                ("mode", "root", "dataset", "subject", "sessionspec",
                 "trial", "domain", "run", "channel", "filetype"))):
    """a predicate specification to search the datasets."""
    @property
    def session(self):
        return self.sessionspec.name

class Container:
    """a reference to data based on a specific Predicate."""
    pass
