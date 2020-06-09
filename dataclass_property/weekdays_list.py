try:
    from dataclass_property import field_property
except (ImportError, Exception):
    class field_property(property):
        def __init__(self, fget=None, fset=None, fdel=None, doc=None, default=None, default_factory=None):
            super().__init__(fget, fset, fdel, doc)


__all__ = ['Weekdays', 'weekdays_property']


def is_iterable(obj):
    """Return if iterable and is not a string."""
    if isinstance(obj, str):
        return False

    try:
        iter(obj)
        return True
    except (TypeError, ValueError, Exception):
        return False


def weekdays_property(attr):
    """Return a property to access Weekdays.sunday as a property.

    Example:
        .. code-block:: python

            class MyClass:
                weekdays: Weekdays = Weekdays()
                sunday: bool = weekdays_property('sunday')
                monday: bool = weekdays_property('monday')
                tuesday: bool = weekdays_property('tuesday')
                wednesday: bool = weekdays_property('wednesday')
                thursday: bool = weekdays_property('thursday')
                friday: bool = weekdays_property('friday')
                saturday: bool = weekdays_property('saturday')
    """
    def fget(self):
        return getattr(self.weekdays, attr, 0)

    def fset(self, value):
        if value is None:
            return  # Ignore initial value of None
        setattr(self.weekdays, attr, value)

    def fdel(self):
        delattr(self.weekdays, attr)

    return field_property(fget, fset, fdel, doc='Alias for weekdays {}'.format(attr), default=None)


def _weekday_prop(name):
    def fget(self):
        return name in self

    def fset(self, value):
        if value:
            self.append(name)
        elif name in self:
            self.remove(name)

    return property(fget, fset)


class Weekdays(list):
    """Sorted list of weekdays.

    Features:
      * If no arguments are given the list will be populated with all weekday names.
      * If `Weekdays(friday=False)` all weekdays will be in the list except for fridays.
      * Weekdays can be added or removed by a property `my_week.monday = False` or `my_week.tuesday = True`.
      * Abbreviations ("Sun", "Mon", "Tue") and weekday indexes (where monday is 0, sunday is 6) are allowed.
        * Abbreviations and indexes work with init, append, insert, extend, remove, __add__, __contains__

    Args:
        *args (tuple/object): Positional arguments of names to be in the list of weekdays.
            ("sunday", "monday", "Tue", "Fri")
        **kwargs (dict/object): Keyword arguments for weekday values.
            {"Sunday": True, "Monday": True, "Tue": True, "Fri": False}
    """
    SUNDAY_VALUE = 'sunday'
    MONDAY_VALUE = 'monday'
    TUESDAY_VALUE = 'tuesday'
    WEDNESDAY_VALUE = 'wednesday'
    THURSDAY_VALUE = 'thursday'
    FRIDAY_VALUE = 'friday'
    SATURDAY_VALUE = 'saturday'

    # Weekday names and order
    DAYS = {SUNDAY_VALUE: 0, MONDAY_VALUE: 1, TUESDAY_VALUE: 2, WEDNESDAY_VALUE: 3,
            THURSDAY_VALUE: 4, FRIDAY_VALUE: 5, SATURDAY_VALUE: 6}

    _all_true = {name: True for name in DAYS}
    _all_false = {name: False for name in DAYS}

    MAPPING = {'sunday': SUNDAY_VALUE, 'sundays': SUNDAY_VALUE, 'sun': SUNDAY_VALUE, 6: SUNDAY_VALUE,
               'monday': MONDAY_VALUE, 'mondays': MONDAY_VALUE, 'mon': MONDAY_VALUE, 0: MONDAY_VALUE,
               'tuesday': TUESDAY_VALUE, 'tuesdays': TUESDAY_VALUE, 'tue': TUESDAY_VALUE, 1: TUESDAY_VALUE,
               'wednesday': WEDNESDAY_VALUE, 'wednesdays': WEDNESDAY_VALUE, 'wed': WEDNESDAY_VALUE, 2: WEDNESDAY_VALUE,
               'thursday': THURSDAY_VALUE, 'thursdays': THURSDAY_VALUE, 'thu': THURSDAY_VALUE, 3: THURSDAY_VALUE,
               'friday': FRIDAY_VALUE, 'fridays': FRIDAY_VALUE, 'fri': FRIDAY_VALUE, 4: FRIDAY_VALUE,
               'saturday': SATURDAY_VALUE, 'saturdays': SATURDAY_VALUE, 'sat': SATURDAY_VALUE, 5: SATURDAY_VALUE,
               }

    sunday = _weekday_prop('sunday')
    monday = _weekday_prop('monday')
    tuesday = _weekday_prop('tuesday')
    wednesday = _weekday_prop('wednesday')
    thursday = _weekday_prop('thursday')
    friday = _weekday_prop('friday')
    saturday = _weekday_prop('saturday')

    sun = _weekday_prop('sunday')
    mon = _weekday_prop('monday')
    tue = _weekday_prop('tuesday')
    wed = _weekday_prop('wednesday')
    thu = _weekday_prop('thursday')
    fri = _weekday_prop('friday')
    sat = _weekday_prop('saturday')

    def __init__(self, *args, **kwargs):
        """Initialize the sorted list of Weekdays

        An empty list means that every day of the week is valid.
        If Weekdays(friday=False) all weekdays will be in the list except for fridays.

        Args:
            *args (tuple/object): Positional arguments of names to be in the list of weekdays.
                ("sunday", "monday", "Tue", "fri")
            **kwargs (dict/object): Keyword arguments for weekday values.
                {"Sunday": True, "Monday": True, "Tue": True, "fri": False}
        """
        if len(args) == 0 and len(kwargs) == 0:
            # If no arguments given assume all True
            values = self._all_true.copy()
        else:
            if len(args) == 1 and is_iterable(args[0]):
                args = args[0]
            values = self._all_false.copy()
            values.update({self.as_attr(arg): True for arg in args if self.is_attr(arg)})
            values.update({self.as_attr(k): v for k, v in kwargs.items() if self.is_attr(k)})

        super().__init__((k for k, v in values.items() if v))

    @classmethod
    def is_attr(cls, value):
        if isinstance(value, str):
            value = value.lower()
        return value in cls.MAPPING

    @classmethod
    def as_attr(cls, value):
        if isinstance(value, str):
            value = value.lower()
        value = cls.MAPPING.get(value, None)
        if value not in cls.DAYS:
            raise ValueError('Invalid weekday given!')

        return value

    def is_valid(self, weekday):
        """Return if the given weekday is in this list of Weekdays."""
        return weekday in self

    def append(self, value):
        value = self.as_attr(value)
        if not list.__contains__(self, value):
            super().append(value)
            self.sort(key=self.DAYS.get)

    def insert(self, index, value):
        value = self.as_attr(value)
        if not list.__contains__(self, value):
            super().insert(index, value)
            self.sort(key=self.DAYS.get)

    def remove(self, value):
        value = self.as_attr(value)
        if list.__contains__(self, value):
            super().remove(value)

    def __contains__(self, value):
        try:
            value = self.as_attr(value)
            return super().__contains__(value)
        except (TypeError, ValueError, Exception):
            return False

    def __setitem__(self, key, value):
        value = self.as_attr(value)
        super().__setitem__(key, value)
        self.sort(key=self.DAYS.get)

    def extend(self, other):
        for n in other:
            if self.is_attr(n):
                n = self.as_attr(n)
                if n not in self:
                    self.append(n)
        self.sort(key=self.DAYS.get)

    def __add__(self, other):
        if isinstance(other, str):
            other = [other]
        new_obj = self.__class__(*self)
        new_obj.extend(other)
        return new_obj

    def __radd__(self, other):
        if isinstance(other, str):
            other = [other]
        new_obj = self.__class__(*self)
        new_obj.extend(other)
        return new_obj

    def __iadd__(self, other):
        if isinstance(other, str):
            other = [other]
        self.extend(other)
        return self

    # ===== Pydantic validation =====
    @classmethod
    def __get_validators__(cls):
        # one or more validators may be yielded which will be called in the
        # order to validate the input, each validator will receive as an input
        # the value returned from the previous validator
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(
                options=[cls.SUNDAY_VALUE, cls.MONDAY_VALUE, cls.TUESDAY_VALUE, cls.WEDNESDAY_VALUE,
                         cls.THURSDAY_VALUE, cls.FRIDAY_VALUE, cls.SATURDAY_VALUE],
                )

    @classmethod
    def validate(cls, v):
        if isinstance(v, cls):
            return v
        elif v is None:
            v = []
        elif not isinstance(v, (list, tuple)):
            v = [v]
        elif isinstance(v, dict):
            return cls(**v)
        return cls(*v)
