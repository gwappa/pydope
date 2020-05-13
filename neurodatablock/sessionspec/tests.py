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

"""usage: python -m dope.sessionspec.tests"""

import unittest
from . import *
from .. import status as _status

class SessionSpecTests(unittest.TestCase):

    def test_initialize(self):
        obj = SessionSpec(type="session", date="2015-12-31", index="003")
        self.assertEqual(obj.name, "session2015-12-31-003")
        self.assertEqual(obj.type, "session")
        self.assertEqual(obj.date.year, 2015)
        self.assertEqual(obj.date.month, 12)
        self.assertEqual(obj.date.day, 31)
        self.assertEqual(obj.index, 3)
        self.assertEqual(str(SessionSpec("2p-imaging2015-12-31-003")),
            "2p-imaging2015-12-31-003")
        SessionSpec(type=None, date=None, index=None)

    def test_status(self):
        obj = SessionSpec(type="session", date="2015-12-31", index=1)
        self.assertEqual(obj.compute_write_status(), _status.SINGLE)
        obj = obj.with_values(index=(1,3))
        self.assertEqual(obj.compute_write_status(), _status.MULTIPLE)
        obj = obj.with_values(index=None)
        self.assertEqual(obj.compute_write_status(), _status.UNSPECIFIED)
        obj = SessionSpec()
        self.assertEqual(obj.compute_write_status(), _status.UNSPECIFIED)

if __name__ == "__main__":
    unittest.main()
