==================
dataclass_property
==================

Add the ability to use properties with dataclasses.
This allows for better input validation on dataclasses.

Most of the code base is a direct copy from dataclasses with modifications.
Unfortunately, dataclasses were not written in a way where you can extend the functionality easily.
I changed the code to use a class based system, so the functionality could be extended.
It's still not fun to work with the dataclasses library.


Examples
========

.. code-block:: python

    from typing import Union
    from dataclass_property import dataclass

    @dataclass
    class TimeDelta:
        hours: int = 0
        minutes: int = 0
        milliseconds: int = 0

        @property
        def seconds(self) -> int:  # default_factory is set to `int()` from the annotation
            return self._seconds

        @seconds.setter
        def seconds(self, value: Union[int, float]):
            if isinstance(value, float):
                mill = int((value % 1) * 1000)
                if mill:
                    self.milliseconds = mill
            self._seconds = int(value)

    td = TimeDelta(minutes=1)
    td.seconds = 0.5
    assert td.seconds == 0
    assert td.milliseconds == 500

    td = TimeDelta(seconds=0.1)
    assert td.seconds == 0
    assert td.milliseconds == 100


`field_property` example with custom defaults

.. code-block:: python

    from dataclass_property import dataclass, field_property

    @dataclass
    class Point:
        # X
        @field_property(default=1)
        def x(self) -> int:
            return self._x

        @x.setter
        def x(self, value: int):
            self._x = value

        # Y
        y: int = field_property(default=1)

        @y.getter
        def y(self) -> int:
            return self._y

        @y.setter
        def y(self, value: int):
            self._y = value

        # Z
        @field_property
        def z(self) -> int:
            return self._z

        z.default(5)

        @z.default_factory
        @classmethod
        def z(cls):
            return 5

        @z.setter
        def z(self, value: int):
            self._z = value

    p = Point()
    assert p.x == 1
    assert p.y == 1
    assert p.z == 5

    p = Point(x=2, y=2, z=6)
    assert p.x == 2
    assert p.y == 2
    assert p.z == 6
