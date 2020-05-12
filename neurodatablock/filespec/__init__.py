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
from ..core import SelectionStatus as _SelectionStatus

def parse_repeated(item, parsefun, separators=(",", "/", "+", "-")):
    """tests if the string `item` consists of a repetition of
    representations."""
    item = item.strip()
    if " " in item:
        return parsefun(item.split())
    for sep in separators:
        if sep in item:
            return parsefun(item.split(sep))
    # otherwise
    return None

def validate_index(index, label="index"):
    if index is None:
        return None
    elif isinstance(index, int):
        return index
    elif isinstance(index, str):
        is_repeat = parse_repeated(index, validate_index)
        if is_repeat is not None:
            return is_repeat
        # otherwise: assumed to be a single index repr
        idx = None
        try:
            idx = int(index)
        except ValueError:
            pass
        if idx is None:
            raise ValueError(f"error parsing '{index}' into an index")
        if idx < 0:
            raise ValueError(f"{label} cannot be negative (got {idx})")
        return idx
    elif hasattr(index, "__iter__"):
        parsed = [validate_index(i, label) for i in index]
        return tuple(item for item in parsed if item is not None)
    elif callable(index):
        return index
    else:
        raise ValueError(f"unexpected {label} type: '{index}'")

def validate_suffix(suffix):
    if suffix is None:
        return None
    elif isinstance(suffix, str):
        is_repeat = parse_repeated(suffix, validate_suffix)
        if is_repeat is not None:
            return is_repeat
        # otherwise: assumed to be a single suffix repr
        suffix = suffix.strip()
        if len(suffix) == 0:
            return None
        elif not suffix.startswith("."):
            return "." + suffix
        else:
            return suffix
    elif hasattr(suffix, "__iter__"):
        parsed = [validate_suffix(s) for s in suffix]
        return tuple(item for item in parsed if item is not None)
    elif callable(suffix):
        return suffix
    else:
        raise ValueError(f"unexpected suffix: '{suffix}'")

def validate_channels(channels):
    if channels is None:
        return None
    elif isinstance(channels, str):
        is_repeat = parse_repeated(channels, validate_channels)
        if is_repeat is not None:
            return is_repeat
        # otherwise: assume to be a single channel repr
        return channels
    elif hasattr(channels, "__iter__"):
        parsed = [validate_channels(chan) for chan in channels]
        return tuple(item for item in parsed if item is not None)
    elif callable(channels):
        return channels

class FileSpec(_collections.namedtuple("_FileSpec",
                ("suffix", "trial", "run", "channel")), _SelectionStatus):
    DIGITS = 5

    def __new__(cls, suffix=None, trial=None, run=None, channel=None):
        return super(cls, FileSpec).__new__(cls,
                        suffix=validate_suffix(suffix),
                        trial=validate_index(trial, "trial index"),
                        run=validate_index(run, "run index"),
                        channel=validate_channels(channel))

    @property
    def status(self):
        return self.compute_status(None)

    def compute_status(self, context=None):
        # TODO
        if context is None:
            unspecified = (((self.trial is None) and (self.run is None)),
                           self.channel is None,
                           self.suffix is None)
            if all(unspecified):
                return self.UNSPECIFIED
            elif any(callable(fld) for fld in self):
                return self.DYNAMIC
            elif any(unspecified):
                return self.MULTIPLE
            elif any(((not isinstance(fld, str)) and hasattr(fld, "__iter__")) for fld in self):
                return self.MULTIPLE
            else:
                return self.SINGLE
        else:
            raise NotImplementedError("FileSpec.compute_status()")

    def compute_path(self, context):
        """context: Predicate"""
        return context.compute_domain_path() / self.format_name(context)

    def format_name(self, context, digits=None):
        """context: Predicate"""
        runtxt = self.format_run(digits=digits)
        chtxt  = self.format_channel(context)
        sxtxt  = self.format_suffix()
        return f"{context.subject}_{context.session.name}_{context.domain}{runtxt}{chtxt}{sxtxt}"

    def format_run(self, digits=None):
        if digits is None:
            digits = self.DIGITS
        if self.trial is None:
            if self.run is None:
                return ""
            elif not isinstance(self.run, int):
                raise ValueError(f"cannot compute a run representation from run index: {self.run}")
            else:
                return "_run" + str(self.run).zfill(digits)
        elif not isinstance(self.trial, int):
            raise ValueError(f"cannot compute a trial representation from trial index: {self.trial}")
        else:
            return "_trial" + str(self.trial).zfill(digits)

    def format_channel(self, context):
        if self.channel is None:
            return ""
        elif isinstance(self.channel, str):
            return f"_{self.channel}"
        elif iterable(self.channel):
            return "_" + "-".join(self.channel)
        else:
            raise ValueError(f"cannot compute channel representation from: {self.channel}")

    def format_suffix(self):
        if self.suffix is None:
            return ""
        elif not isinstance(self.suffix, str):
            raise ValueError(f"cannot compute a suffix from specification: {self.suffix}")
        else:
            return self.suffix

    def with_values(self, **kwargs):
        spec = dict(**kwargs)
        for fld in self._fields:
            if fld not in spec.keys():
                spec[fld] = getattr(self, fld)
        return self.__class__(**spec)
