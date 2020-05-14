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
"""
- from_name()
- for_suffix()
- for_datatype()
- for_data()
"""

import collections as _collections

from .. import core as _core
from .. import modes as _modes

ARRAY  = "array"
TABLE  = "table"
BINARY = "binary"
DICT   = "dict"

class DataIOWarning(UserWarning):
    pass

class DataIOError(IOError):
    pass

Registry = _collections.namedtuple("Registry",
                    ("name", "type", "suffix", "test", "load", "save"))

import pandas as _pd

def pandas_test(data):
    return isinstance(data, _pd.DataFrame)

def pandas_load(spec, path, **kwargs):
    if path.suffix == ".tsv":
        return _pd.read_csv(str(path), sep="\t", **kwargs)
    else:
        return _pd.read_csv(str(path), **kwargs)

def pandas_save(spec, path, data, **kwargs):
    if not isinstance(data, _pd.DataFrame):
        raise ValueError(f"cannot run pandas-save() with {data.__class__}")
    if "index" not in kwargs.keys():
        kwargs["index"] = False
    if path.suffix == ".tsv":
        data.to_csv(str(path), sep="\t", **kwargs)
    else:
        data.to_csv(str(path), **kwargs)

pandas_io = Registry(name="pandas",
                     type=TABLE,
                     suffix=(".csv", ".tsv"),
                     test=pandas_test,
                     load=pandas_load,
                     save=pandas_save)

import numpy as _np
import bzar as _bzar

def bzar_test(data):
    return isinstance(data, _np.ndarray)

def bzar_load(spec, path, **kwargs):
    return _bzar.load(path, **kwargs)

def bzar_save(spec, path, data, **kwargs):
    if not isinstance(data, _np.ndarray):
        raise ValueError(f"cannot run bzar-save() with {data.__class__}")
    return _bzar.save(path, data, **kwargs)

bzar_io = Registry(name="bzar",
                   type=ARRAY,
                   suffix=(".bzar",),
                   test=bzar_test,
                   load=bzar_load,
                   save=bzar_save)

import json as _json

def json_test(data, throw=False):
    if data is None:
        return True
    elif isinstance(data, (str, int, float)):
        return True
    elif isinstance(data, (list, tuple)):
        return all(json_test(item, throw=throw) for item in data)
    elif all(hasattr(data, attr) for attr in ("keys", "values", "items")):
        for key, value in data.items():
            if not isinstance(key, str):
                if throw == True:
                    raise ValueError(f"key must be string, instead of '{key}'")
                else:
                    return False
            elif json_test(data, throw=throw) == False:
                return False
        return True
    else:
        if throw == True:
            raise ValueError(f"cannot format to JSON: {data}")
        else:
            return False

def json_load(spec, path, **kwargs):
    with open(path, "r") as src:
        return _json.load(src, **kwargs)

def json_save(spec, path, data, **kwargs):
    if "indent" not in kwargs:
        kwargs["indent"] = 4
    with open(path, "w") as out:
        _json.dump(data, out, **kwargs)

json_io = Registry(name="json",
                   type=DICT,
                   suffix=(".json",),
                   test=json_test,
                   load=json_load,
                   save=json_save)

BASE = [pandas_io, bzar_io, json_io]
USER = []

def register(name, type, suffix, load=None, save=None):
    if not isinstance(name, str):
        raise ValueError(f"'name' must be string, got {name.__class__}")
    if type not in (ARRAY, TABLE, BINARY, DICT):
        raise ValueError(f"'type' must be one of: '{ARRAY}', '{TABLE}', '{BINARY}', '{DICT}'")
    if isinstance(suffix, str):
        suffix = (suffix,)
    elif hasattr(suffix, "__iter__"):
        suffix = tuple(suffix)
    else:
        raise ValueError(f"unexpected suffix type (must contain at least one suffix): {suffix}")
    reg = Registry(name, type, suffix, load=load, save=save)
    # TODO: check for collision (name, type, suffix)
    USER.append(reg)

def for_suffix(suffix):
    for regs in (USER, BASE):
        for reg in regs:
            if suffix in reg.suffix:
                return reg
    raise DataIOError(f"appropriate I/O driver not found for: '{suffix}'")

def from_name(name):
    for regs in (USER, BASE):
        for reg in regs:
            if name == reg.name:
                return reg
    raise DataIOError(f"I/O driver not found with name: '{name}'")

def for_datatype(type):
    for regs in (USER, BASE):
        for reg in regs:
            if type == reg.type:
                return reg
    raise DataIOError(f"I/O driver not found for type: '{type}'")

def for_data(data):
    for regs in (USER, BASE):
        for reg in regs:
            if reg.test(data) == True:
                return reg
    raise DataIOError(f"appropriate I/O driver not found for: {data}")

def load(spec, loader=None, **kwargs):
    if loader is not None:
        if not isinstance(loader, Registry):
            loader = from_name(loader)
    else:
        loader = for_suffix(spec.file.suffix)
    if loader.load is None:
        raise DataIOError(f"I/O driver '{loader.name}' does not have the load() method")
    data = loader.load(spec, spec.compute_path(), **kwargs)
    return _core.Entry(source=spec, data=data)

def save(spec, data, loader=None, datatype=None, **kwargs):
    path = spec.compute_path()
    if spec.mode == _modes.READ:
        raise DataIOError("the file is referenced in read-only mode")
    elif (spec.mode == _modes.APPEND) and path.exists():
        raise FileExistsError("the file is referenced in append mode, and the file already exists")
    if loader is not None:
        if not isinstance(loader, Registry):
            loader = from_name(loader)
    elif datatype is not None:
        if datatype in (ARRAY, TABLE, BINARY, DICT):
            loader = for_datatype(datatype)
        else:
            raise ValueError(f"unknown datatype: '{datatype}'")
    else:
        loader = for_suffix(spec.file.suffix)
    if loader.save is None:
        raise DataIOError(f"I/O driver '{loader.name}' does not have the save() method")
    return loader.save(spec, path, data, **kwargs)
