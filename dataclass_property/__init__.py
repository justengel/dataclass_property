from .__meta__ import version as __version__
import sys

from dataclasses import Field, field, MISSING, FrozenInstanceError, InitVar, fields, asdict, astuple, make_dataclass, \
    replace, is_dataclass

from .internals_old import dataclass, get_return_type, field_property, DataclassInterface
if sys.version_info >= (3, 10):
    from .internals_310 import dataclass, DataclassInterface


__all__ = ['dataclass', 'get_return_type', 'field_property',
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
