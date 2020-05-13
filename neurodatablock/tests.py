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
from . import modes, testing
from .core import Selector
from .dataset import Dataset
from .subject import Subject
from .predicate import PredicateError

class BrowsingTests(unittest.TestCase):
    def setUp(self):
        self._root = testing.test_dataset_path()
        self._animal_names  = ("A1", "A2")
        self._animal_nonexistent = "A3"
        self._session_names = ("session2015-11-12-001",
                               "session2015-11-18-001",
                               "session2015-12-11-001",
                               "session2015-12-11-002")
        self._domain_names  = ("scanimage",
                               "behavior")
        self._runs          = (1, 2, 3)
        self._root.mkdir()
        for ani in self._animal_names:
            subdir = self._root / ani
            subdir.mkdir()
            for sess in self._session_names:
                sessdir = subdir / sess
                sessdir.mkdir()
                for dom in self._domain_names:
                    domdir = sessdir / dom
                    domdir.mkdir()
                    for run in self._runs:
                        path = domdir / f"{ani}_{sess}_{dom}_run{run:05d}.dat"
                        path.touch()

    def test_selector(self):
        data = Dataset(self._root)
        subs = data.subjects
        assert isinstance(subs, Selector)
        for ani in self._animal_names:
            assert isinstance(subs[ani], Subject)
        with self.assertRaises(PredicateError):
            subs[self._animal_nonexistent]
        data = data.with_mode(modes.WRITE)
        self.assertEqual(data._spec.mode, modes.WRITE)
        subs = data.subjects
        self.assertEqual(subs._spec.mode, modes.WRITE)
        data[self._animal_nonexistent] # should success

    def test_browsing_dataset(self):
        data = Dataset(self._root)

        # check browsing of subjects
        subs = data.subjects
        assert isinstance(subs, Selector)
        self.assertEqual(len(subs), len(self._animal_names))
        self.assertEqual(tuple(sorted(set(sub.name for sub in subs))),
                         tuple(sorted(self._animal_names)))

        # check browsing of sessions
        sess = data.sessions
        self.assertEqual(len(sess),
                         len(self._animal_names) * len(self._session_names))
        self.assertEqual(tuple(sorted(set(s.subject.name for s in sess))),
                        tuple(sorted(self._animal_names)))
        self.assertEqual(tuple(sorted(set(s.name for s in sess))),
                        tuple(sorted(self._session_names)))

        # check browsing of domains
        dom = data.domains
        self.assertEqual(len(dom),
                         len(sess) * len(self._domain_names))
        self.assertEqual(tuple(sorted(set(d.name for d in dom))),
                         tuple(sorted(self._domain_names)))

        # check browsing of files
        files = data.files
        self.assertEqual(len(files),
                         len(dom) * len(self._runs))
        self.assertEqual(tuple(sorted(set(r.index for r in files))),
                         tuple(sorted(self._runs)))

    def test_browsing_domain(self):
        data    = Dataset(self._root)
        session = data[self._animal_names[0]][self._session_names[0]]
        domain  = session[self._domain_names[0]]

        files = domain.files
        self.assertEqual(len(files), len(self._runs))
        self.assertEqual(tuple(sorted(set(r.index for r in files))),
                         tuple(sorted(self._runs)))

    def tearDown(self):
        if self._root.exists():
            testing.remove_recursive(self._root)
