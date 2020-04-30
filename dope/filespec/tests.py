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

"""usage: python -m dope.filespec.tests"""

import unittest
from . import *

class FileSpecTests(unittest.TestCase):
    def test_status(self):
        obj = FileSpec(trial=None, run=1, channel="V", filetype=".npy")
        self.assertEqual(obj.status, obj.SINGLE)
        obj = obj.with_values(trial=1, run=None)
        self.assertEqual(obj.status, obj.SINGLE)
        obj = obj.with_values(trial=None)
        self.assertEqual(obj.status, obj.MULTIPLE)
        obj = obj.cleared()
        self.assertEqual(obj.status, obj.UNSPECIFIED)
