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

SESSION_NAME_PATTERN = _re.compile(r"([a-zA-Z0-9-]*[a-zA-Z])(\d{4})-(\d{2})-(\d{2})-(\d+)")
SESSION_TYPE_PATTERN = _re.compile(r"[a-zA-Z0-9-]*[a-zA-Z]$")
SESSION_DATE_FORMAT  = "%Y-%m-%d"

def parse_session_name(namefmt):
    if not isinstance(namefmt, str):
        raise ValueError(f"session name expected to be a string, but got {namefmt.__class__}")
    matched = SESSION_NAME_PATTERN.match(namefmt)
    if not matched:
        raise ValueError(f"does not match to session-name pattern: {namefmt}")
    return dict(type=matched.group(1),
                date=_datetime.datetime.strptime(f"{matched.group(2)}-{matched.group(3)}-{matched.group(4)}",
                                                 SESSION_DATE_FORMAT),
                index=int(matched.group(5)))

def parse_session_type(typefmt):
    if typefmt is None:
        return None
    elif not isinstance(typefmt, str):
        raise ValueError(f"session type must be str or None, got {typefmt.__class__}")
    if not SESSION_TYPE_PATTERN.match(typefmt):
        raise ValueError(f"does not match to session-type pattern: '{typefmt}'")
    return typefmt

def parse_session_date(datefmt):
    if datefmt is None:
        return None
    elif isinstance(datefmt, _datetime.datetime):
        return datefmt
    try:
        return _datetime.datetime.strptime(datefmt, SESSION_DATE_FORMAT)
    except ValueError as e:
        raise ValueError(f"failed to parse session date: '{datefmt}' ({e})")

def parse_session_index(indexfmt):
    if indexfmt is None:
        return None
    try:
        index = int(indexfmt)
    except ValueError as e:
        raise ValueError(f"failed to parse session index: '{indexfmt}' ({e})")
    if index < 0:
        raise ValueError(f"session index cannot be negative, but got '{index}'")
    return index
