import datetime
from typing import Union, List
from dataclass_property import field_property, MISSING


__all__ = ['TIME_FORMATS', 'DATE_FORMATS', 'DATETIME_FORMATS',
           'datetime_property', 'time_property', 'date_property', 'timedelta_helper_property', 'seconds_property',
           'DateTime', 'make_time', 'make_date', 'make_datetime', 'str_date', 'str_time', 'str_datetime']


TIME_FORMATS = [
    '%I:%M:%S %p',     # '02:24:55 PM'
    '%I:%M:%S.%f %p',  # '02:24:55.000200 PM'
    '%I:%M %p',        # '02:24 PM'
    '%H:%M:%S',        # '14:24:55'
    '%H:%M:%S.%f',     # '14:24:55.000200'
    '%H:%M',           # '14:24'
    ]

DATE_FORMATS = [
    '%Y-%m-%d', '%m/%d/%Y',   # '2019-04-17', '04/17/2019'
    '%b %d %Y', '%b %d, %Y',  # 'Apr 17 2019', 'Apr 17, 2019'
    '%d %b %Y', '%d %b, %Y',  # '17 Apr 2019', '17 Apr, 2019'
    '%B %d %Y', '%B %d, %Y',  # 'April 17 2019', 'April 17, 2019'
    '%d %B %Y', '%d %B, %Y',  # '17 April 2019', '17 April, 2019'
    ]

DATETIME_FORMATS = [d + ' ' + t for t in TIME_FORMATS for d in DATE_FORMATS] + DATE_FORMATS + TIME_FORMATS


def datetime_property(attr, allow_none=True, default=MISSING, default_factory=MISSING, formats: List[str] = None):
    """Create a datetime dataclass property where the underlying datetime is saved to "_attr".

    Args:
        attr (str): Attribute name (example: "created_on"
        allow_none (bool)[True]: Allows the property to be set to None. This is needed if the default is None.
        default (object)[MISSING]: Default value for the dataclass
        default_factory (function)[MISSING]: Function that returns the default value.
        formats (list)[None]: List of string formats to accept.

    Returns:
        property (field_property): Dataclass field property for a datetime.
    """
    attr = '_' + attr
    typeref = Union[datetime.datetime, str]
    if allow_none:
        typeref = Union[datetime.datetime, str, None]

    if default == MISSING and default_factory == MISSING and allow_none:
        default = None

    def fget(self):
        return getattr(self, attr)

    def fset(self, value: typeref):
        if value is None and not allow_none:
            raise TypeError('Invalid datetime value given!')
        elif value is not None:
            value = make_datetime(value, formats=formats)
        setattr(self, attr, value)

    return field_property(fget, fset, doc='datetime property {}'.format(attr),
                          default=default, default_factory=default_factory)


def time_property(attr, allow_none=True, default=MISSING, default_factory=MISSING, formats: List[str] = None):
    """Create a time dataclass property where the underlying datetime is saved to "_attr".

    Args:
        attr (str): Attribute name (example: "created_on"
        allow_none (bool)[True]: Allows the property to be set to None. This is needed if the default is None.
        default (object)[MISSING]: Default value for the dataclass
        default_factory (function)[MISSING]: Function that returns the default value.
        formats (list)[None]: List of string formats to accept.

    Returns:
        property (field_property): Dataclass field property for a time.
    """
    attr = '_' + attr
    typeref = Union[datetime.time, str]
    if allow_none:
        typeref = Union[datetime.time, str, None]

    if default == MISSING and default_factory == MISSING and allow_none:
        default = None

    def fget(self):
        return getattr(self, attr)

    def fset(self, value: typeref):
        if value is None and not allow_none:
            raise TypeError('Invalid time value given!')
        elif value is not None:
            value = make_time(value, formats=formats)
        setattr(self, attr, value)

    return field_property(fget, fset, doc='time property {}'.format(attr),
                          default=default, default_factory=default_factory)


def date_property(attr, allow_none=True, default=MISSING, default_factory=MISSING, formats: List[str] = None):
    """Create a date dataclass property where the underlying datetime is saved to "_attr".

    Args:
        attr (str): Attribute name (example: "created_on"
        allow_none (bool)[True]: Allows the property to be set to None. This is needed if the default is None.
        default (object)[MISSING]: Default value for the dataclass
        default_factory (function)[MISSING]: Function that returns the default value.
        formats (list)[None]: List of string formats to accept.

    Returns:
        property (field_property): Dataclass field property for a date.
    """
    attr = '_' + attr
    typeref = Union[datetime.time, str]
    if allow_none:
        typeref = Union[datetime.time, str, None]

    if default == MISSING and default_factory == MISSING and allow_none:
        default = None

    def fget(self):
        return getattr(self, attr)

    def fset(self, value: typeref):
        if value is None and not allow_none:
            raise TypeError('Invalid date value given!')
        elif value is not None:
            value = make_date(value, formats=formats)
        setattr(self, attr, value)

    return field_property(fget, fset, doc='date property {}'.format(attr),
                          default=default, default_factory=default_factory)


def timedelta_helper_property():
    """Return a timedelta property that uses a classes attributes for
    'weeks', 'days', 'hours', 'minutes', 'seconds', 'milliseconds', and 'microseconds'.

    Example:

        .. code-block:: python

            @dataclass
            class MyClass:
                days: int = 0
                hours: int = 0
                minutes: int = 0
                seconds: int = 0
                milliseconds: int = 0

                interval: datetime.timedelta = timedelta_helper_property()

    Returns:
        property (field_property): Timedelta property that uses a classes underlying attributes.
    """
    def fget(self) -> datetime.timedelta:
        weeks = getattr(self, 'weeks', 0)
        days = getattr(self, 'days', 0)
        hours = getattr(self, 'hours', 0)
        minutes = getattr(self, 'minutes', 0)
        seconds = getattr(self, 'seconds', 0)
        milliseconds = getattr(self, 'milliseconds', 0)
        microseconds = getattr(self, 'microseconds', 0)

        return datetime.timedelta(weeks=weeks, days=days, hours=hours, minutes=minutes, seconds=seconds,
                                  milliseconds=milliseconds, microseconds=microseconds)

    def fset(self, value: datetime.timedelta):
        if value is None:  # Protect the default of None
            return
        elif not isinstance(value, datetime.timedelta):
            raise TypeError('Invalid timedelta given!')

        days = value.days
        seconds = value.seconds
        microseconds = value.microseconds

        weeks = int(days / 7)
        days = int(days - weeks)
        if hasattr(self, 'weeks'):
            self.weeks = weeks
        if hasattr(self, 'days'):
            self.days = days

        hours = int(seconds / 3600)
        minutes = int((seconds - (hours * 3600)) / 60)
        seconds = int(seconds - (minutes * 60))
        if hasattr(self, 'hours'):
            self.hours = hours
        if hasattr(self, 'minutes'):
            self.minutes = minutes
        if hasattr(self, 'seconds'):
            self.seconds = seconds

        milliseconds = int(microseconds / 1000)
        microseconds = int(microseconds - (milliseconds * 1000))
        if hasattr(self, 'milliseconds'):
            self.milliseconds = milliseconds
        if hasattr(self, 'microseconds'):
            self.microseconds = microseconds

    return field_property(fget, fset, doc='Interval from the set time values', default=None)


def seconds_property(attr='seconds'):
    """Property for a seconds attribute to turn floating points into milliseconds.

    Args:
        attr (str)['seconds']: Attribute name

    Returns:
        property (field_property): Property that when given a float will set seconds and milliseconds.
    """
    attr = '_' + attr

    def fget(self) -> int:
        return getattr(self, attr, 0)

    def fset(self, value: Union[int, float]):
        if isinstance(value, float):
            mill = int((value % 1) * 1000)
            if mill:
                self.milliseconds = mill

        setattr(self, attr, int(value))

    return field_property(fget, fset, doc='Seconds in time. If float also set milliseconds', default=0)


class DateTime(datetime.datetime):
    """DateTime class for pydantic which converts custom string formats into datetimes."""
    @classmethod
    def __get_validators__(cls):
        # one or more validators may be yielded which will be called in the
        # order to validate the input, each validator will receive as an input
        # the value returned from the previous validator
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(
                allowed_formats=DATETIME_FORMATS,
                )

    @classmethod
    def validate(cls, v):
        if v is None:
            return None
        return make_datetime(v)

    def __str__(self):
        return str_datetime(self)


def make_time(time_string: Union[datetime.time, str], formats: List[str] = None):
    """Make the time object from the given time string.
    Args:
        time_string (str): Time string '04:00 PM' ...
        formats (list): List of acceptable time string formats.
    Returns:
        t (datetime.time): Time object or None.
    """
    if isinstance(time_string, datetime.time):
        return time_string

    if formats is None:
        formats = DATETIME_FORMATS

    for fmt in formats:
        try:
            dt = datetime.datetime.strptime(time_string, fmt)
            return dt.time()
        except (TypeError, ValueError, Exception):
            pass

    raise ValueError('Invalid time format {}. Allowed formats are {}'.format(repr(time_string), repr(formats)))


def make_date(date_string: Union[datetime.date, str], formats: List[str] = None):
    """Make the date object from the given time string.
    Args:
        date_string (str): Date string 'mm/dd/yyyy' ...
        formats (list): List of acceptable time string formats.
    Returns:
        d (datetime.date): Date object or None.
    """
    if isinstance(date_string, datetime.date):
        return date_string

    if formats is None:
        formats = DATETIME_FORMATS

    for fmt in formats:
        try:
            dt = datetime.datetime.strptime(date_string, fmt)
            return dt.date()
        except (TypeError, ValueError, Exception):
            pass

    raise ValueError('Invalid date format {}. Allowed formats are {}'.format(repr(date_string), repr(formats)))


def make_datetime(date_string: Union[datetime.datetime, str], formats: List[str] = None) -> datetime.datetime:
    """Make the datetime from the given date time string.
    Args:
        date_string (str): Datetime string '04:00 PM' ...
        formats (list): List of acceptable datetime string formats.
    Returns:
        dt (datetime.datetime): Datetime object or None.
    """
    if isinstance(date_string, datetime.datetime):
        return date_string

    if formats is None:
        formats = DATETIME_FORMATS

    for fmt in formats:
        try:
            return DateTime.strptime(date_string, fmt)
        except (TypeError, ValueError, Exception):
            pass

    raise ValueError('Invalid datetime format {}. Allowed formats are {}'.format(repr(date_string), repr(formats)))


def str_date(dt: datetime.date) -> str:
    """Return the date as a string."""
    return dt.strftime(DATE_FORMATS[0])


def str_time(dt: datetime.time) -> str:
    """Return the time as a string"""
    return dt.strftime(TIME_FORMATS[0])


def str_datetime(dt: datetime.datetime) -> str:
    """Return the datetime as a string."""
    return dt.strftime(DATETIME_FORMATS[0])
