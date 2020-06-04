
def test_normal_property():
    import dataclasses

    # ========== Normal dataclasses property ==========
    @dataclasses.dataclass()
    class Props:
        @property
        def x(self) -> int:  # Used default_factory `int()` because of return annotation
            return self._x

        @x.setter
        def x(self, value):
            print('In Setter @dataclasses.dataclass', repr(value))  # On init this is the property object
            self._x = value  # Note: matches field_property('_x')

    p = Props()
    assert not hasattr(p, 'x'), 'Normal dataclasses do not annotate (which creates fields) for properties as variables!'

    # ========== Manually Annotate Properties for them to work ==========
    class Props:
        @property
        def x(self) -> int:
            return self._x

        @x.setter
        def x(self, value):
            print('In Setter manual dataclasses.dataclass', repr(value))  # On init this is the property object
            self._x = value

    # Manually create type annotations for the dataclass to find the property
    if not hasattr(Props, '__annotations__'):
        Props.__annotations__ = {}
    Props.__annotations__['x'] = int

    # Create the dataclass
    Props = dataclasses.dataclass(Props)

    p = Props()
    try:
        d = dataclasses.asdict(p)
        raise AssertionError('A type annotated property will have a default value '
                             'of a property object instead of int.')
    except TypeError:
        pass  # Expected because property object is not pickleable

    # This isn't what we want, but property(fget, fset) is seen and set as the default value.
    assert isinstance(p.x, property)

    p.x = 1
    assert p.x == 1, 'Property setter should still work. The default is just messed up.'


def test_dataclass_property_normal_property():
    import dataclass_property

    @dataclass_property.dataclass
    class Props:
        @property
        def x(self) -> int:  # Used default_factory `int()` because of return annotation
            return self._x

        @x.setter
        def x(self, value):
            print('In Setter dataclass_property.dataclass', repr(value))  # Should be default to an int() now
            self._x = value

    p = Props()
    assert p.x == 0

    p.x = 1
    assert p.x == 1


def test_dataclass_property_field_property():
    import dataclass_property

    # ========== Use as normal property ==========
    @dataclass_property.dataclass
    class Props:
        @dataclass_property.field_property
        def x(self) -> int:  # Used default_factory `int()` because of return annotation
            return self._x

        @x.setter
        def x(self, value):
            print('In Setter dataclass_property.field_property', repr(value))  # Should be default to an int() now
            self._x = value

    p = Props()
    assert p.x == 0

    p.x = 1
    assert p.x == 1

    # ========== Check default value ==========
    @dataclass_property.dataclass
    class Props:
        @dataclass_property.field_property(default=1)
        def x(self) -> int:  # Used default_factory `int()` because of return annotation
            return self._x

        @x.setter
        def x(self, value):
            self._x = value

    p = Props()
    assert p.x == 1

    p.x = 2
    assert p.x == 2


    # ========== Check default_factory ==========
    @dataclass_property.dataclass
    class Props:
        @dataclass_property.field_property(default_factory=lambda: 5)
        def x(self) -> int:  # Used default_factory `int()` because of return annotation
            return self._x

        @x.setter
        def x(self, value):
            self._x = value

    p = Props()
    assert p.x == 5

    p.x = 2
    assert p.x == 2


    # ========== Check default decorator ==========
    @dataclass_property.dataclass
    class Props:
        @dataclass_property.field_property
        def x(self) -> int:  # Used default_factory `int()` because of return annotation
            return self._x

        x.default(1)

        @x.setter
        def x(self, value):
            self._x = value

    p = Props()
    assert p.x == 1, p.x

    p.x = 2
    assert p.x == 2


    # ========== Check default_factory decorator ==========
    @dataclass_property.dataclass
    class Props:
        @dataclass_property.field_property
        def x(self) -> int:  # Used default_factory `int()` because of return annotation
            return self._x

        # @x.default_factory
        # @staticmethod
        # def x():
        #     return 5

        @x.default_factory
        @classmethod
        def x(cls):
            return 5

        @x.default_factory
        def x():  # No arguments. IDE won't be happy.
            return 5

        @x.setter
        def x(self, value):
            self._x = value

    p = Props()
    assert p.x == 5

    p.x = 2
    assert p.x == 2


def test_field_property():
    import dataclasses
    from dataclass_property import dataclass, field_property

    class Props:
        @field_property(default=1)
        def x(self) -> int:
            return self._x

        @x.setter
        def x(self, value):
            self._x = value  # Note: matches field_property('_x')

        @property
        def y(self) -> int:
            return getattr(self, '_y', 0)

        @y.setter
        def y(self, value):
            if isinstance(value, float):
                self._x = int(value * 10)
            print(value)
            self._y = int(value)

        @property
        def z(self) -> int:
            return getattr(self, '_z', 0)

        @z.setter
        def z(self, value):
            self._z = value

        @property
        def p(self) -> int:
            return getattr(self, '_p', 0)

        @p.setter
        def p(self, value: int):
            self._p = value


    # Manually create type annotations for the dataclass to find the property
    # Props.__annotations__['x'] = int
    # Props.__annotations__['y'] = int
    # Props.__annotations__['z'] = int
    # Props.__annotations__['p'] = int

    # Props = dataclasses.dataclass(Props)

    p = Props()
    try:
        d = dataclasses.asdict(p)
        print(d)
        # raise AssertionError('A type annotated property will have a default value '
        #                      'of a property object instead of int.')
    except TypeError:
        pass  # Expected because property object is not pickleable

    p = Props(p=0)
    d = dataclasses.asdict(p)
    assert 'x' in d and d['x'] == 1
    assert 'y' in d and d['y'] == 0
    assert 'z' in d and d['z'] == 0
    assert 'p' in d and d['p'] == 0

    p = Props(x=2, y=3, z=4, p=0)
    d = dataclasses.asdict(p)
    assert 'x' in d and d['x'] == 2
    assert 'y' in d and d['y'] == 3
    assert 'z' in d and d['z'] == 4
    assert 'p' in d and d['p'] == 0


if __name__ == '__main__':
    test_normal_property()
    test_dataclass_property_normal_property()
    test_dataclass_property_field_property()
    # test_field_property()

    print('All tests finished successfully!')
