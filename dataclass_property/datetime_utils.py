import datetime
from typing import Union, List
from dataclass_property import field_property, MISSING


__all__ = ['Date', 'Time', 'DateTime', 'TimeDelta',
           'datetime_property', 'time_property', 'date_property', 'timedelta_helper_property', 'seconds_property']


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
    typeref = Union[Date, str]
    if allow_none:
        typeref = Union[Date, str, None]

    if default == MISSING and default_factory == MISSING and allow_none:
        default = None

    def fget(self):
        return getattr(self, attr)

    def fset(self, value: typeref):
        if value is None and not allow_none:
            raise TypeError('Invalid date value given!')
        elif value is not None:
            value = Date.make_date(value, formats=formats)
        setattr(self, attr, value)

    return field_property(fget, fset, doc='date property {}'.format(attr),
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
    typeref = Union[Time, str]
    if allow_none:
        typeref = Union[Time, str, None]

    if default == MISSING and default_factory == MISSING and allow_none:
        default = None

    def fget(self):
        return getattr(self, attr)

    def fset(self, value: typeref):
        if value is None and not allow_none:
            raise TypeError('Invalid time value given!')
        elif value is not None:
            value = Time.make_time(value, formats=formats)
        setattr(self, attr, value)

    return field_property(fget, fset, doc='time property {}'.format(attr),
                          default=default, default_factory=default_factory)


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
    typeref = Union[DateTime, str]
    if allow_none:
        typeref = Union[DateTime, str, None]

    if default == MISSING and default_factory == MISSING and allow_none:
        default = None

    def fget(self):
        return getattr(self, attr)

    def fset(self, value: typeref):
        if value is None and not allow_none:
            raise TypeError('Invalid datetime value given!')
        elif value is not None:
            value = DateTime.make_datetime(value, formats=formats)
        setattr(self, attr, value)

    return field_property(fget, fset, doc='datetime property {}'.format(attr),
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


class Date(datetime.date):
    """DateTime class for pydantic which converts custom string formats into datetimes."""

    DATE_FORMATS = [
        '%Y-%m-%d', '%m/%d/%Y',   # '2019-04-17', '04/17/2019'
        '%b %d %Y', '%b %d, %Y',  # 'Apr 17 2019', 'Apr 17, 2019'
        '%d %b %Y', '%d %b, %Y',  # '17 Apr 2019', '17 Apr, 2019'
        '%B %d %Y', '%B %d, %Y',  # 'April 17 2019', 'April 17, 2019'
        '%d %B %Y', '%d %B, %Y',  # '17 April 2019', '17 April, 2019'
        ]

    @classmethod
    def make_date(cls, date_string: Union[datetime.date, str], formats: List[str] = None) -> datetime.date:
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
            formats = [i for i in cls.DATE_FORMATS]

        for fmt in formats:
            try:
                dt = datetime.datetime.strptime(date_string, fmt)
                return dt.date()
            except (TypeError, ValueError, Exception):
                pass

        raise ValueError('Invalid date format {}. Allowed formats are {}'.format(repr(date_string), repr(formats)))

    @classmethod
    def str_date(cls, dt: datetime.date) -> str:
        """Return the date as a string."""
        return dt.strftime(cls.DATE_FORMATS[0])

    def __new__(cls, year, month=0, day=0):
        if isinstance(year, bytes):
            year = year.decode()
        if isinstance(year, (str, datetime.time)):
            dt = cls.make_date(year)
            return dt
            # year = dt.year
            # month = dt.month
            # day = dt.day
        super().__new__(year=year, month=month, day=day)

    @classmethod
    def __get_validators__(cls):
        # one or more validators may be yielded which will be called in the
        # order to validate the input, each validator will receive as an input
        # the value returned from the previous validator
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(
                allowed_formats=cls.DATE_FORMATS,
                )

    @classmethod
    def validate(cls, v):
        if v is None:
            return None
        return Date(v)

    def __str__(self):
        return self.str_date(self)


class Time(datetime.time):
    """DateTime class for pydantic which converts custom string formats into datetimes."""

    TIME_FORMATS = [
        '%I:%M:%S %p',     # '02:24:55 PM'
        '%I:%M:%S.%f %p',  # '02:24:55.000200 PM'
        '%I:%M %p',        # '02:24 PM'
        '%H:%M:%S',        # '14:24:55'
        '%H:%M:%S.%f',     # '14:24:55.000200'
        '%H:%M',           # '14:24'
        ]

    @classmethod
    def make_time(cls, time_string: Union[datetime.time, str], formats: List[str] = None) -> datetime.time:
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
            formats = [i for i in cls.TIME_FORMATS]

        for fmt in formats:
            try:
                dt = datetime.datetime.strptime(time_string, fmt)
                return dt.time()
            except (TypeError, ValueError, Exception):
                pass

        raise ValueError('Invalid time format {}. Allowed formats are {}'.format(repr(time_string), repr(formats)))

    @classmethod
    def str_time(cls, dt: datetime.time) -> str:
        """Return the time as a string"""
        return dt.strftime(cls.TIME_FORMATS[0])

    def __new__(cls, hour=0, minute=0, second=0, microsecond=0, tzinfo=None, *, fold=0):
        if isinstance(hour, bytes):
            hour = hour.decode()
        if isinstance(hour, (str, datetime.time)):
            dt = cls.make_time(hour)
            return dt
            # hour = dt.hour
            # minute = dt.minute
            # second = dt.second
            # microsecond = dt.microsecond
            # tzinfo = dt.tzinfo
            # fold = dt.fold
        super().__new__(cls, hour=hour, minute=minute, second=second, microsecond=microsecond, tzinfo=tzinfo, fold=fold)

    @classmethod
    def __get_validators__(cls):
        # one or more validators may be yielded which will be called in the
        # order to validate the input, each validator will receive as an input
        # the value returned from the previous validator
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(
                allowed_formats=cls.TIME_FORMATS,
                )

    @classmethod
    def validate(cls, v):
        if v is None:
            return None
        return Time(v)

    def __str__(self):
        return self.str_time(self)


class DateTime(datetime.datetime):
    """DateTime class for pydantic which converts custom string formats into datetimes."""

    DATETIME_FORMATS = [d + ' ' + t for t in Time.TIME_FORMATS for d in Date.DATE_FORMATS]
    DATETIME_FORMATS.extend(Date.DATE_FORMATS)
    DATETIME_FORMATS.extend(Time.TIME_FORMATS)

    @classmethod
    def make_datetime(cls, date_string: Union[datetime.datetime, str], formats: List[str] = None) -> datetime.datetime:
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
            formats = [i for i in cls.DATETIME_FORMATS]

        for fmt in formats:
            try:
                return datetime.datetime.strptime(date_string, fmt)
            except (TypeError, ValueError, Exception):
                pass

        try:  # Try ISO format
            return datetime.datetime.fromisoformat(date_string)
        except:
            pass

        raise ValueError('Invalid datetime format {}. Allowed formats are {}'.format(repr(date_string), repr(formats)))

    @classmethod
    def str_datetime(cls, dt: datetime.datetime) -> str:
        """Return the datetime as a string."""
        return dt.strftime(cls.DATETIME_FORMATS[0])

    def __new__(cls, year, month=0, day=0, hour=0, minute=0, second=0, microsecond=0, tzinfo=None, *, fold=0):
        if isinstance(year, (str, datetime.datetime)):
            dt = cls.make_datetime(year)
            return dt
            # year = dt.year
            # month = dt.month
            # day = dt.day
            # hour = dt.hour
            # minute = dt.minute
            # second = dt.second
            # microsecond = dt.microsecond
            # tzinfo = dt.tzinfo
            # fold = dt.fold
        return super().__new__(cls, year, month=month, day=day, hour=hour, minute=minute, second=second,
                               microsecond=microsecond, tzinfo=tzinfo, fold=fold)

    @classmethod
    def __get_validators__(cls):
        # one or more validators may be yielded which will be called in the
        # order to validate the input, each validator will receive as an input
        # the value returned from the previous validator
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(
                allowed_formats=cls.DATETIME_FORMATS,
                )

    @classmethod
    def validate(cls, v):
        if v is None:
            return None
        return DateTime(v)

    def __str__(self):
        return self.str_datetime(self)


class TimeDelta(datetime.timedelta):
    pass
