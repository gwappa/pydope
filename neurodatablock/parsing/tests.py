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

"""usage: python -m dope.parsing.tests"""

import unittest
from . import *

class ParsingTests(unittest.TestCase):
    def assert_function_with_values(self, fun,
                            passes=[],
                            fails=[],
                            errortype=ValueError):
        for passobj in passes:
            fun(passobj)
        for failobj in fails:
            with self.assertRaises(errortype):
                fun(failobj)

    def test_parse_type(self):
        self.assert_function_with_values(session.type,
            passes=("session", "2p", "no-task", None),
            fails=("task2",))

    def test_parse_date(self):
        import datetime
        self.assert_function_with_values(session.date,
            passes=("2019-02-26", datetime.datetime.now(), None),
            fails=("2019.02.26", "26-02-2019", "2019-26-02"))

    def test_parse_index(self):
        self.assert_function_with_values(session.index,
            passes=(1, "1", "001", None),
            fails=("all", -1))

    def test_parse_name(self):
        self.assert_function_with_values(session.name,
            passes=("session2016-01-25-001", "no-task2015-12-31-003",),
            fails=(None, "session2016-01-25", "session-2016-01-25-001"))

    def test_parser(self):
        sub  = "K1"
        styp = "ane"
        sidx = 1
        sdat = "2019-11-12"
        sess = f"{styp}{sdat}-{sidx:03d}"
        dom  = "img"
        run  = 1
        suf  = ".tif"
        chans= ("Green", "Red")
        spec = f"run{run:03d}_{'-'.join(chans)}{suf}"
        name = f"{sub}_{sess}_{dom}_{spec}"
        ps = Parse(name)
        self.assertEqual(len(ps.result), 0)
        self.assertEqual(ps.remaining, name)
        ps = ps.subject
        self.assertEqual(ps.result["subject"], sub)
        self.assertEqual(len(ps.remaining), len(name) - len(sub) - 1)
        ps = ps.session
        self.assertEqual(ps.result["session"]["type"], styp)
        self.assertEqual(ps.result["session"]["date"].strftime(session.DATE_FORMAT), sdat)
        self.assertEqual(ps.result["session"]["index"], sidx)
        ps = ps.domain
        self.assertEqual(ps.result["domain"], dom)
        self.assertEqual(ps.remaining, spec)
        ps = ps.filespec
        self.assertEqual(ps.result["filespec"]["suffix"], ".tif")
        self.assertEqual(ps.result["filespec"]["type"],  "run")
        self.assertEqual(ps.result["filespec"]["index"],    run)
        self.assertEqual(set(ps.result["filespec"]["channel"]), set(chans))

if __name__ == "__main__":
    unittest.main()
