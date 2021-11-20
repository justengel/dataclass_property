"""
Edited spots are marked with <<<EDITED>>>

Changes:
  * Custom field_property
  * Custom dataclass function to automatically annotate properties.
  * Modified _get_field to get default value for property.
  * No Changes to _process_class, included to use _get_field and _init_fn
"""

import sys
import types
import inspect
import dataclasses

from .interface import BaseDataclassInterface


__all__ = ['dataclass', 'DataclassInterface']


MISSING = dataclasses.MISSING


class DataclassInterface(BaseDataclassInterface):
    """Basically, I need to override certain methods to support dataclass properties."""

    @classmethod
    def dataclass(mcs, cls=None, *, init=True, repr=True, eq=True, order=False,
                  unsafe_hash=False, frozen=False):
        """Returns the same class as was passed in, with dunder methods
        added based on the fields defined in the class.

        Examines PEP 526 __annotations__ to determine fields.

        If init is true, an __init__() method is added to the class. If
        repr is true, a __repr__() method is added. If order is true, rich
        comparison dunder methods are added. If unsafe_hash is true, a
        __hash__() method function is added. If frozen is true, fields may
        not be assigned to after instance creation.
        """
        def wrap(cls):
            # Annotate all properties
            mcs.annotate_properties(cls)  # <<<EDITED>>>
            return mcs._process_class(cls, init, repr, eq, order, unsafe_hash, frozen)

        # See if we're being called as @dataclass or @dataclass().
        if cls is None:
            # We're called with parens.
            return wrap

        # We're called as @dataclass without parens.
        return wrap(cls)

    @classmethod
    def _get_field(mcs, cls, a_name, a_type):
        # Return a Field object for this field name and type.  ClassVars
        # and InitVars are also returned, but marked as such (see
        # f._field_type).

        # If the default value isn't derived from Field, then it's only a
        # normal default value.  Convert it to a Field().
        f = mcs.make_field(cls, a_name)  # <<<EDITED>>>

        # Only at this point do we know the name and the type.  Set them.
        f.name = a_name
        f.type = a_type

        # Assume it's a normal field until proven otherwise.  We're next
        # going to decide if it's a ClassVar or InitVar, everything else
        # is just a normal field.
        f._field_type = mcs._FIELD

        # In addition to checking for actual types here, also check for
        # string annotations.  get_type_hints() won't always work for us
        # (see https://github.com/python/typing/issues/508 for example),
        # plus it's expensive and would require an eval for every stirng
        # annotation.  So, make a best effort to see if this is a ClassVar
        # or InitVar using regex's and checking that the thing referenced
        # is actually of the correct type.

        # For the complete discussion, see https://bugs.python.org/issue33453

        # If typing has not been imported, then it's impossible for any
        # annotation to be a ClassVar.  So, only look for ClassVar if
        # typing has been imported by any module (not necessarily cls's
        # module).
        typing = sys.modules.get('typing')
        if typing:
            if (mcs._is_classvar(a_type, typing)
                    or (isinstance(f.type, str)
                        and mcs._is_type(f.type, cls, typing, typing.ClassVar,
                                     mcs._is_classvar))):
                f._field_type = mcs._FIELD_CLASSVAR

        # If the type is InitVar, or if it's a matching string annotation,
        # then it's an InitVar.
        if f._field_type is mcs._FIELD:
            # The module we're checking against is the module we're
            # currently in (dataclasses.py).
            # dataclasses = sys.modules[__name__]  # WTAF!?
            if (mcs._is_initvar(a_type, dataclasses)
                    or (isinstance(f.type, str)
                        and mcs._is_type(f.type, cls, dataclasses, dataclasses.InitVar,
                                     mcs._is_initvar))):
                f._field_type = mcs._FIELD_INITVAR

        # Validations for individual fields.  This is delayed until now,
        # instead of in the Field() constructor, since only here do we
        # know the field name, which allows for better error reporting.

        # Special restrictions for ClassVar and InitVar.
        if f._field_type in (mcs._FIELD_CLASSVAR, mcs._FIELD_INITVAR):
            if f.default_factory is not MISSING:
                raise TypeError(f'field {f.name} cannot have a '
                                'default factory')
            # Should I check for other field settings? default_factory
            # seems the most serious to check for.  Maybe add others.  For
            # example, how about init=False (or really,
            # init=<not-the-default-init-value>)?  It makes no sense for
            # ClassVar and InitVar to specify init=<anything>.

        # For real fields, disallow mutable defaults for known types.
        if f._field_type is mcs._FIELD and isinstance(f.default, (list, dict, set)):
            raise ValueError(f'mutable default {type(f.default)} for field '
                             f'{f.name} is not allowed: use default_factory')

        return f

    @classmethod
    def _process_class(mcs, cls, init, repr, eq, order, unsafe_hash, frozen):
        # Now that dicts retain insertion order, there's no reason to use
        # an ordered dict.  I am leveraging that ordering here, because
        # derived class fields overwrite base class fields, but the order
        # is defined by the base class, which is found first.
        fields = {}

        if cls.__module__ in sys.modules:
            globals = sys.modules[cls.__module__].__dict__
        else:
            # Theoretically this can happen if someone writes
            # a custom string to cls.__module__.  In which case
            # such dataclass won't be fully introspectable
            # (w.r.t. typing.get_type_hints) but will still function
            # correctly.
            globals = {}

        setattr(cls, mcs._PARAMS, mcs._DataclassParams(init, repr, eq, order,
                                               unsafe_hash, frozen))

        # Find our base classes in reverse MRO order, and exclude
        # ourselves.  In reversed order so that more derived classes
        # override earlier field definitions in base classes.  As long as
        # we're iterating over them, see if any are frozen.
        any_frozen_base = False
        has_dataclass_bases = False
        for b in cls.__mro__[-1:0:-1]:
            # Only process classes that have been processed by our
            # decorator.  That is, they have a _FIELDS attribute.
            base_fields = getattr(b, mcs._FIELDS, None)
            if base_fields:
                has_dataclass_bases = True
                for f in base_fields.values():
                    fields[f.name] = f
                if getattr(b, mcs._PARAMS).frozen:
                    any_frozen_base = True

        # Annotations that are defined in this class (not in base
        # classes).  If __annotations__ isn't present, then this class
        # adds no new annotations.  We use this to compute fields that are
        # added by this class.
        #
        # Fields are found from cls_annotations, which is guaranteed to be
        # ordered.  Default values are from class attributes, if a field
        # has a default.  If the default value is a Field(), then it
        # contains additional info beyond (and possibly including) the
        # actual default value.  Pseudo-fields ClassVars and InitVars are
        # included, despite the fact that they're not real fields.  That's
        # dealt with later.
        cls_annotations = cls.__dict__.get('__annotations__', {})

        # Now find fields in our class.  While doing so, validate some
        # things, and set the default values (as class attributes) where
        # we can.
        cls_fields = [mcs._get_field(cls, name, type)    # <<<EDITED>>>
                      for name, type in cls_annotations.items()]
        for f in cls_fields:
            fields[f.name] = f

            # If the class attribute (which is the default value for this
            # field) exists and is of type 'Field', replace it with the
            # real default.  This is so that normal class introspection
            # sees a real default value, not a Field.
            if isinstance(getattr(cls, f.name, None), mcs.Field):
                if f.default is MISSING:
                    # If there's no default, delete the class attribute.
                    # This happens if we specify field(repr=False), for
                    # example (that is, we specified a field object, but
                    # no default value).  Also if we're using a default
                    # factory.  The class attribute should not be set at
                    # all in the post-processed class.
                    delattr(cls, f.name)
                else:
                    setattr(cls, f.name, f.default)

        # Do we have any Field members that don't also have annotations?
        for name, value in cls.__dict__.items():
            if isinstance(value, mcs.Field) and not name in cls_annotations:
                raise TypeError(f'{name!r} is a field but has no type annotation')

        # Check rules that apply if we are derived from any dataclasses.
        if has_dataclass_bases:
            # Raise an exception if any of our bases are frozen, but we're not.
            if any_frozen_base and not frozen:
                raise TypeError('cannot inherit non-frozen dataclass from a '
                                'frozen one')

            # Raise an exception if we're frozen, but none of our bases are.
            if not any_frozen_base and frozen:
                raise TypeError('cannot inherit frozen dataclass from a '
                                'non-frozen one')

        # Remember all of the fields on our class (including bases).  This
        # also marks this class as being a dataclass.
        setattr(cls, mcs._FIELDS, fields)

        # Was this class defined with an explicit __hash__?  Note that if
        # __eq__ is defined in this class, then python will automatically
        # set __hash__ to None.  This is a heuristic, as it's possible
        # that such a __hash__ == None was not auto-generated, but it
        # close enough.
        class_hash = cls.__dict__.get('__hash__', MISSING)
        has_explicit_hash = not (class_hash is MISSING or
                                 (class_hash is None and '__eq__' in cls.__dict__))

        # If we're generating ordering methods, we must be generating the
        # eq methods.
        if order and not eq:
            raise ValueError('eq must be true if order is true')

        if init:
            # Does this class have a post-init function?
            has_post_init = hasattr(cls, mcs._POST_INIT_NAME)

            # Include InitVars and regular fields (so, not ClassVars).
            flds = [f for f in fields.values()
                    if f._field_type in (mcs._FIELD, mcs._FIELD_INITVAR)]
            mcs._set_new_attribute(cls, '__init__',
                               mcs._init_fn(flds,
                                        frozen,
                                        has_post_init,
                                        # The name to use for the "self"
                                        # param in __init__.  Use "self"
                                        # if possible.
                                        '__dataclass_self__' if 'self' in fields
                                        else 'self',
                                        globals,
                                        ))

        # Get the fields as a list, and include only real fields.  This is
        # used in all of the following methods.
        field_list = [f for f in fields.values() if f._field_type is mcs._FIELD]

        if repr:
            flds = [f for f in field_list if f.repr]
            mcs._set_new_attribute(cls, '__repr__', mcs._repr_fn(flds, globals))

        if eq:
            # Create _eq__ method.  There's no need for a __ne__ method,
            # since python will call __eq__ and negate it.
            flds = [f for f in field_list if f.compare]
            self_tuple = mcs._tuple_str('self', flds)
            other_tuple = mcs._tuple_str('other', flds)
            mcs._set_new_attribute(cls, '__eq__',
                               mcs._cmp_fn('__eq__', '==',
                                       self_tuple, other_tuple,
                                       globals=globals))

        if order:
            # Create and set the ordering methods.
            flds = [f for f in field_list if f.compare]
            self_tuple = mcs._tuple_str('self', flds)
            other_tuple = mcs._tuple_str('other', flds)
            for name, op in [('__lt__', '<'),
                             ('__le__', '<='),
                             ('__gt__', '>'),
                             ('__ge__', '>='),
                             ]:
                if mcs._set_new_attribute(cls, name,
                                      mcs._cmp_fn(name, op, self_tuple, other_tuple,
                                              globals=globals)):
                    raise TypeError(f'Cannot overwrite attribute {name} '
                                    f'in class {cls.__name__}. Consider using '
                                    'functools.total_ordering')

        if frozen:
            for fn in mcs._frozen_get_del_attr(cls, field_list, globals):
                if mcs._set_new_attribute(cls, fn.__name__, fn):
                    raise TypeError(f'Cannot overwrite attribute {fn.__name__} '
                                    f'in class {cls.__name__}')

        # Decide if/how we're going to create a hash function.
        hash_action = mcs._hash_action[bool(unsafe_hash),
                                   bool(eq),
                                   bool(frozen),
                                   has_explicit_hash]
        if hash_action:
            # No need to call _set_new_attribute here, since by the time
            # we're here the overwriting is unconditional.
            cls.__hash__ = hash_action(cls, field_list, globals)

        if not getattr(cls, '__doc__'):
            # Create a class doc-string.
            cls.__doc__ = (cls.__name__ +
                           str(inspect.signature(cls)).replace(' -> None', ''))

        return cls


dataclass = DataclassInterface.dataclass
