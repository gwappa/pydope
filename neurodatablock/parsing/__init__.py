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

"""parsing file/directory names."""
import re as _re
import datetime as _datetime
from collections import namedtuple as _namedtuple

SEP          = "_"
ParseResult  = _namedtuple("ParseResult", ("result", "remaining"))

class ParseError(ValueError):
    def __init__(self, msg):
        super().__init__(msg)

class Parse(ParseResult):
    def __new__(cls, line=None, result=None, remaining=None):
        if line is not None:
            return super().__new__(cls, {}, line)
        else:
            return super().__new__(cls, result, remaining)

    def parse_single(self, elem):
        parsed = elem.parse(self.remaining)
        res    = dict(**self.result)
        res[elem.__name__] = parsed.result
        return self.__class__(result=res, remaining=parsed.remaining)

    @property
    def subject(self):
        return self.parse_single(subject)

    @property
    def session(self):
        return self.parse_single(session)

    @property
    def domain(self):
        return self.parse_single(domain)

    @property
    def filespec(self):
        return self.parse_single(filespec)

class element:
    NAME_PATTERN = _re.compile(r"[a-zA-Z0-9-]+")

    @classmethod
    def format_remaining(cls, remaining, sep=SEP):
        if len(remaining) == 0:
            return None
        while remaining.startswith(sep):
            remaining = remaining[1:]
        return remaining

    @classmethod
    def parse(cls, fmt):
        """default parsing behavior"""
        if not isinstance(fmt, str):
            raise ValueError(f"names are expected to be a string, but got {fmt.__class__}")
        matched = cls.NAME_PATTERN.match(fmt)
        if not matched:
            raise ParseError(f"does not match to the name pattern: {fmt}")
        result = matched.group(0)
        return ParseResult(result, cls.format_remaining(fmt[len(result):]))

class dataset(element):
    pass

class subject(element):
    pass

class session(element):
    NAME_PATTERN = _re.compile(r"([a-zA-Z0-9-]*[a-zA-Z])(\d{4})-(\d{2})-(\d{2})-(\d+)")
    TYPE_PATTERN = _re.compile(r"[a-zA-Z0-9-]*[a-zA-Z]$")
    DATE_FORMAT  = "%Y-%m-%d"

    @classmethod
    def parse(cls, fmt):
        if not isinstance(fmt, str):
            raise ValueError(f"session name expected to be a string, but got {fmt.__class__}")
        matched = cls.NAME_PATTERN.match(fmt)
        if not matched:
            raise ParseError(f"does not match to session-name pattern: {fmt}")
        result = dict(type=matched.group(1),
                      date=_datetime.datetime.strptime(f"{matched.group(2)}-{matched.group(3)}-{matched.group(4)}",
                                                       cls.DATE_FORMAT),
                      index=int(matched.group(5)))
        remaining = cls.format_remaining(fmt[len(matched.group(0)):])
        return ParseResult(result, remaining)

    @classmethod
    def name(cls, namefmt):
        return session.parse(namefmt).result

    @classmethod
    def type(cls, typefmt):
        if typefmt is None:
            return None
        elif not isinstance(typefmt, str):
            raise ValueError(f"session type must be str or None, got {typefmt.__class__}")
        if not session.TYPE_PATTERN.match(typefmt):
            raise ParseError(f"does not match to session-type pattern: '{typefmt}'")
        return typefmt

    @classmethod
    def date(cls, datefmt):
        if datefmt is None:
            return None
        elif isinstance(datefmt, _datetime.datetime):
            return datefmt
        try:
            return _datetime.datetime.strptime(datefmt, session.DATE_FORMAT)
        except ValueError as e:
            raise ParseError(f"failed to parse session date: '{datefmt}' ({e})")

    @classmethod
    def index(cls, indexfmt):
        if indexfmt is None:
            return None
        try:
            index = int(indexfmt)
        except ValueError as e:
            raise ParseError(f"failed to parse session index: '{indexfmt}' ({e})")
        if index < 0:
            raise ValueError(f"session index cannot be negative, but got '{index}'")
        return index

class domain(element):
    pass

class filespec(element):
    KEYS          = ("run", "trial")
    INDEX_PATTERN = _re.compile(r"\d+")
    CHAN_PATTERN  = _re.compile(r"[a-zA-Z0-9]+")
    CHAN_SEP      = "-"

    @classmethod
    def keyed_index(cls, fmt, key="run"):
        """reads single keyed index"""
        if not fmt.startswith(key):
            return ParseResult(None, fmt)
        fmt     = fmt[len(key):]
        indexed = cls.INDEX_PATTERN.match(fmt)
        if not indexed:
            raise ParseError(f"file name contains '{key}', but is not indexed: {fmt}")
        res = indexed.group(0)
        # I assume the index cannot happen to be negative
        return ParseResult(int(res), cls.format_remaining(fmt[len(res):]))

    @classmethod
    def channel(cls, fmt):
        """reads single channel"""
        matched = cls.CHAN_PATTERN.match(fmt)
        if not matched:
            if fmt.startswith("."): # suffix seems to start
                return ParseResult(None, fmt)
            elif len(fmt) is None:
                return ParseResult(None, None) # name without a suffix
            else:
                raise ParseError(f"does not match to the channel pattern: {fmt}")
        chan = matched.group(0)
        rem  = fmt[len(chan):]
        if len(rem) == 0:
            rem = None
        else:
            rem = cls.format_remaining(rem, sep=cls.CHAN_SEP)
        return ParseResult(chan, rem)

    @classmethod
    def parse(cls, fmt):
        """default parsing behavior"""
        if not isinstance(fmt, str):
            raise ValueError(f"names are expected to be a string, but got {fmt.__class__}")

        res = dict()
        for key in cls.KEYS:
            res[key], fmt = cls.keyed_index(fmt, key=key)

        channels = []
        chan     = cls.channel(fmt)
        while (chan.result is not None) and (chan.remaining is not None):
            channels.append(chan.result)
            chan = cls.channel(chan.remaining)
        res["channel"] = tuple(channels) if len(channels) > 0 else None
        res["suffix"]  = chan.remaining
        return ParseResult(res, "")
