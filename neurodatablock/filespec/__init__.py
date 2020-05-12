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
from .. import parsing as _parsing

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
                ("suffix", "type", "index", "channel")), _SelectionStatus):
    DIGITS = 5

    def __new__(cls, suffix=None, trial=None, run=None, channel=None, type=None, index=None):
        if type is not None:
            # use type/index mode
            if trial is not None:
                raise ValueError("cannot specify 'trial' when 'type' is specified")
            elif run is not None:
                raise ValueError("cannot specify 'run' when 'type' is specified")
            if type not in ("trial", "run"):
                raise ValueError(f"string ('trial' or 'run') was expected for 'type', but got '{type}'")
            index = validate_index(index, f"{type} index")
        else:
            # trial/run mode
            if (trial is not None) and (run is not None):
                raise ValueError("trial and run cannot be specified at the same time")
            elif trial is None:
                typ = "run"
                index = validate_index(run, "run index")
            else:
                typ = "trial"
                index = validate_index(trial, "trial index")
        if (type is None) and (index is not None):
            raise ValueError("cannot specify index when 'type' is not specified")
        return super(cls, FileSpec).__new__(cls,
                        suffix=validate_suffix(suffix),
                        type=type,
                        index=index,
                        channel=validate_channels(channel))

    @classmethod
    def from_path(cls, path):
        spec, _ = _parsing.file.parse(path.name)
        return cls(**spec)

    def compute_write_status(self):
        status_set = dict((fld, _SelectionStatus.compute_write_status(getattr(self, fld)) \
                        for fld in ("suffix", "index", "channel"))
        # being NONE or DYNAMIC supercedes everything (in this order)
        for status in (self.NONE, self.DYNAMIC):
            if status in status_set.values():
                return status

        # otherwise: status can be either MULTIPLE, SINGLE or UNSPECIFIED
        # where MULTIPLE is not allowed for suffix or index in a single file
        if self.MULTIPLE in [status_set[key] for key in ("suffix", "index")]:
            return self.MULTIPLE

        # otherwise every combination can be represented as SINGLE
        return self.SINGLE


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
        if self.type is None:
            return ""
        elif isinstance(self.index, int):
            if digits is None:
                digits = self.DIGITS
            return f"_{self.type}{str(self.index).zfill(digits)}"
        else:
            # type is not None, index is None
            return f"_all{self.type}s"

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
        spec = {}
        if "type" in kwargs.keys():
            spec[kwargs["type"]] = kwargs.get("index", self.index)
        else:
            for key in ("run", "trial"):
                if key in kwargs.keys():
                    spec[key] = kwargs[key]
        for fld in ("suffix", "channel"):
            spec[fld] = kwargs.get(fld, getattr(self, fld))
        return self.__class__(**spec)
