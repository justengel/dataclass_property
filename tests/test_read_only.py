
def test_read_only():
    from dataclass_property import asdict, dataclass, field_property

    @dataclass
    class Hello:
        @field_property(init=False)
        def what(self) -> int:
            return 5

        @property
        def what_is(self) -> bool:
            return False

        # @what.setter
        # def what(self, val):
        #     print('here', val)

    try:
        h = Hello()
        assert h.what == 5
        assert h.what_is is False
    except AttributeError:
        raise AssertionError('init argument failed!')

    try:
        h.what = 7
        raise AssertionError('Invalid test! "what" field_property has a setter!')
    except AttributeError:
        pass  # Should hit here

    try:
        h.what_is = True
        raise AssertionError('Invalid test! "what_is" property has a setter!')
    except AttributeError:
        pass  # Should hit here


if __name__ == '__main__':
    test_read_only()

    print('All tests passed successfully!')
