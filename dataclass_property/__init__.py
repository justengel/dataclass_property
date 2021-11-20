from .__meta__ import version as __version__
import sys

from dataclasses import Field, field, MISSING, FrozenInstanceError, InitVar, fields, asdict, astuple, make_dataclass, \
    replace, is_dataclass

from .interface import BaseDataclassInterface
from .field_prop import get_return_type, field_property
try:
    from .internals_old import dataclass, DataclassInterface
except (ImportError, Exception):
    dataclass = None
    DataclassInterface = None

if sys.version_info >= (3, 10) or dataclass is None:
    from .internals_310 import dataclass, DataclassInterface


__all__ = ['dataclass', 'DataclassInterface', 'BaseDataclassInterface', 'get_return_type', 'field_property',
           'field',
           'Field',
           'FrozenInstanceError',
           'InitVar',
           'MISSING',

           # Helper functions.
           'fields',
           'asdict',
           'astuple',
           'make_dataclass',
           'replace',
           'is_dataclass',
           ]
