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

"""usage: python -m dope.predicate.tests"""

import unittest
from . import *

class PredicateTests(unittest.TestCase):
    def test_sessionspec(self):
        self.assertEqual(Predicate(sessionindex=1).session_index, 1)
        self.assertEqual(Predicate(session="session2019-03-11-001").session_name,
                        "session2019-03-11-001")
        self.assertEqual(Predicate(sessiondate="2019-03-11").session_date.strftime("%Y-%m-%d"),
                        "2019-03-11")
        self.assertEqual(Predicate(sessiontype="session").session_type, "session")

    def test_level(self):
        pred = Predicate()
        self.assertEqual(pred.level, pred.NA)
        pred = pred.with_values(root="testroot")
        self.assertEqual(pred.level, pred.ROOT)
        pred = pred.with_values(dataset="testds")
        self.assertEqual(pred.level, pred.DATASET)
        pred = pred.with_values(subject="testsub")
        self.assertEqual(pred.level, pred.SUBJECT)
        pred = pred.with_values(session="session2019-03-11-001")
        self.assertEqual(pred.level, pred.SESSION)

    def test_status(self):
        pass #TODO
