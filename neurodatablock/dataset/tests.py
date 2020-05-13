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

import unittest
from . import *
from .. import modes, testing
from ..core import Selector
from ..subject import Subject
from ..predicate import PredicateError

class DatasetTests(unittest.TestCase):
    def setUp(self):
        self._root = testing.test_dataset_path()

    def test_initialize(self):
        for mod in (modes.WRITE, modes.APPEND):
            root = Dataset(self._root, mode=mod) # should success
        self.assertEqual(root._path, self._root)

        with self.assertRaises(FileNotFoundError):
            Dataset(self._root, mode=modes.READ)

        self._root.mkdir()
        Dataset(self._root) # should success
        self._root.rmdir()

        with self.assertRaises(FileNotFoundError):
            Dataset(self._root)

    def test_subjects(self):
        self._root.mkdir()
        data = Dataset(self._root)
        subs = data.subjects
        assert isinstance(subs, Selector)
        self.assertEqual(len(subs), 0)

        for ani in ("A1", "A2"):
            path = self._root / ani
            path.mkdir()
        subs = data.subjects
        self.assertEqual(len(subs), 2)
        assert isinstance(subs["A1"], Subject)
        assert isinstance(subs["A2"], Subject)
        with self.assertRaises(PredicateError):
            subs["A3"]
        data = data.with_mode(modes.WRITE)
        self.assertEqual(data._spec.mode, modes.WRITE)
        subs = data.subjects
        self.assertEqual(subs._spec.mode, modes.WRITE)
        data["A3"] # should success
        testing.remove_recursive(self._root)

    def tearDown(self):
        if self._root.exists():
            testing.remove_recursive(self._root)
