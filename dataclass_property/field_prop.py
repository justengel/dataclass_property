import inspect
import functools
from typing import Callable, Any

import dataclasses


__all__ = ['get_return_type', 'field_property']


MISSING = dataclasses.MISSING


def get_return_type(default: Any = MISSING, default_factory: Callable[[], Any] = MISSING):
    """Find the return type for the default value or default_factory.

    Args:
        default (object)[MISSING]: is the default value of the field.
        default_factory (callable/function)[MISSING]: is a 0-argument function called to initialize a field's value.

    Returns:
        return_type (type/object)[MISSING]: The type of the default or MISSING if not found.
    """
    # Fields must have an annotation
    return_type = inspect.signature(default_factory).return_annotation
    if return_type == inspect.Signature.empty:
        return_type = MISSING
        if default != MISSING:
            return_type = type(default)
        elif default_factory != MISSING:
            try:
                return_type = type(default_factory())
            except (ValueError, TypeError, Exception):
                pass
    return return_type


class field_property(property):

    get_return_type = staticmethod(get_return_type)

    def __init__(self,
                 fget: Callable[[Any], Any] = None,
                 fset: Callable[[Any, Any], None] = None,
                 fdel: Callable[[Any], None] = None,
                 doc: str = None,
                 default: Any = MISSING,
                 default_factory: Callable[[], Any] = MISSING):

        self.default_attr = default
        self.default_factory_attr = default_factory
        self.name = None
        super().__init__(fget, fset, fdel, doc=doc)

    def __set_name__(self, owner, name):
        try:
            if self.name is None:
                self.name = name
        except (AttributeError, Exception):
            pass

    def getter(self, fget: Callable[[Any], Any]) -> 'field_property':
        return type(self)(fget, self.fset, self.fdel, self.__doc__,
                          default=self.default_attr, default_factory=self.default_factory_attr)

    def setter(self, fset: Callable[[Any, Any], None]) -> 'field_property':
        return type(self)(self.fget, fset, self.fdel, self.__doc__,
                          default=self.default_attr, default_factory=self.default_factory_attr)

    def deleter(self, fdel: Callable[[Any], None]) -> 'field_property':
        return type(self)(self.fget, self.fset, fdel, self.__doc__,
                          default=self.default_attr, default_factory=self.default_factory_attr)

    def default(self, default: Any) -> 'field_property':
        self.default_attr = default
        return self

    def default_factory(self, default_factory: Callable[[Any], None]) -> 'field_property':
        self.default_factory_attr = default_factory
        return self

    __call__ = getter
