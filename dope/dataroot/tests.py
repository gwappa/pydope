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
from datetime import datetime
from pathlib import Path
from .. import modes

class DataRootTests(unittest.TestCase):
    def setUp(self):
        suffix = datetime.now().strftime("%y%m%d-%H%M%S-%f")
        self._root = Path(f"test{suffix}")
        if self._root.exists():
            raise FileExistsError("cannot use a test data-root")

    def test_initialize(self):
        for mod in (modes.WRITE, modes.APPEND):
            root = DataRoot(self._root, mode=mod) # should success
        self.assertEqual(root.path, self._root)

        with self.assertRaises(FileNotFoundError):
            DataRoot(self._root, mode=modes.READ)

        self._root.mkdir()
        DataRoot(self._root) # should success
        self._root.rmdir()

        with self.assertRaises(FileNotFoundError):
            DataRoot(self._root)
