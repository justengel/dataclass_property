import types
import inspect
import dataclasses

from .field_prop import get_return_type, field_property


__all__ = ['BaseDataclassInterface']


MISSING = dataclasses.MISSING


class BaseDataclassInterface:
    """Basically, I need to override certain methods to support dataclass properties."""
    # ===== Done below in for loop =====
    # field = dataclasses.field
    # Field = dataclasses.Field
    # _FIELD = dataclasses._FIELD
    # _is_classvar = dataclasses._is_classvar
    # _FIELD_CLASSVAR = dataclasses._FIELD_CLASSVAR
    # _is_type = dataclasses._is_type
    # _is_initvar = dataclasses._is_initvar
    # _FIELD_INITVAR = dataclasses._FIELD_INITVAR
    # _PARAMS = dataclasses._PARAMS
    # _DataclassParams = dataclasses._DataclassParams
    # _FIELDS = dataclasses._FIELDS
    # _POST_INIT_NAME = dataclasses._POST_INIT_NAME
    # _set_new_attribute = dataclasses._set_new_attribute
    # _repr_fn = dataclasses._repr_fn
    # _tuple_str = dataclasses._tuple_str
    # _cmp_fn = dataclasses._cmp_fn
    # _frozen_get_del_attr = dataclasses._frozen_get_del_attr
    # _hash_action = dataclasses._hash_action
    # _init_fn = dataclasses._init_fn

    @classmethod
    def annotate_properties(mcs, cls):
        # Annotate all properties
        if not hasattr(cls, '__annotations__'):
            cls.__annotations__ = {}
        for name, attr in cls.__dict__.items():
            if isinstance(attr, property) and name not in cls.__annotations__:
                return_type = get_return_type(default_factory=attr.fget)
                if return_type != MISSING:
                    cls.__annotations__[name] = return_type

    @classmethod
    def make_field(mcs, cls, a_name):
        # If the default value isn't derived from Field, then it's only a
        # normal default value.  Convert it to a Field().
        default = getattr(cls, a_name, MISSING)
        if isinstance(default, mcs.Field):
            f = default
        else:
            if isinstance(default, types.MemberDescriptorType):
                # This is a field in __slots__, so it has no default value.
                default = MISSING
            if isinstance(default, property):
                default_factory_attr = getattr(default, 'default_factory_attr', MISSING)
                default_attr = getattr(default, 'default_attr', MISSING)

                field_kwargs = field_property.get_field_params(default)

                # If fset is None the property is read-only. Do not initialize.
                if default.fset is None and field_kwargs.get('init', False):
                    field_kwargs['init'] = False

                if default_factory_attr != MISSING:
                    if isinstance(default_factory_attr, (staticmethod, classmethod)):
                        default_factory_attr = default_factory_attr.__get__(cls, cls)
                    f = mcs.field(default_factory=default_factory_attr, **field_kwargs)
                elif default_attr != MISSING:
                    f = mcs.field(default=default_attr, **field_kwargs)
                else:
                    return_type = inspect.signature(default.fget).return_annotation
                    if return_type != inspect.Signature.empty and field_kwargs['init']:
                        default = return_type
                        f = mcs.field(default_factory=default, **field_kwargs)
                    else:
                        default = MISSING
                        f = mcs.field(default=default, **field_kwargs)
            else:
                f = mcs.field(default=default)

        return f

# Set all dataclasses variables in DataclassInterface so the functions can be overridden
for attr in dir(dataclasses):
    setattr(BaseDataclassInterface, attr, getattr(dataclasses, attr))
