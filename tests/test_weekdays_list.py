
def check_days(weekdays, *valid_days, is_valid=True):
    from dataclass_property.weekdays_list import Weekdays

    if len(valid_days) == 0:
        valid_days = list(Weekdays.DAYS)
    elif len(valid_days) == 0 and isinstance(valid_days[0], list):
        valid_days = valid_days[0]
    valid_days = [Weekdays.as_attr(d) for d in valid_days]
    
    for day in Weekdays.DAYS:
        should_be_valid = (day in valid_days and is_valid) or (day not in valid_days and not is_valid)
        assert (day in weekdays) == should_be_valid, \
            'day={} valid_days={} is_valid={}'.format(day, valid_days, is_valid)
        # assert ((day in valid_days and day in weekdays and is_valid) or
        #         (day in valid_days and day not in weekdays and not is_valid) or
        #         (day not in valid_days and day not in weekdays and is_valid) or
        #         (day not in valid_days and day in weekdays and not is_valid)
        #         )


def test_weekdays_init():
    from dataclass_property.weekdays_list import Weekdays

    # No given inputs should be all True
    w = Weekdays()
    check_days(w, *list(Weekdays.DAYS))

    def check_day_init(day):
        w = Weekdays(day)
        w2 = Weekdays(**{day: True})
        check_days(w, day)
        check_days(w2, day)

    # Single day as string should be true while all other false
    for day in Weekdays.DAYS:
        check_day_init(day)

    # ===== Case insensitive =====
    for day in Weekdays.DAYS:
        day = day.upper()
        check_day_init(day)

    # ===== Abbreviations =====
    for day in Weekdays.DAYS:
        day = day[:3]
        check_day_init(day)

    # ===== Abbreviations case insensitive =====
    for day in Weekdays.DAYS:
        day = day[:3].upper()
        check_day_init(day)


def test_weekday_property():
    from dataclass_property.weekdays_list import Weekdays

    w = Weekdays()
    check_days(w)

    w.sunday = False
    check_days(w, 'sunday', is_valid=False)
    w.sunday = True
    check_days(w)

    checked = []
    for day in Weekdays.DAYS:
        setattr(w, day, False)
        checked.append(day)
        check_days(w, *checked, is_valid=False)

    checked = []
    for day in Weekdays.DAYS:
        setattr(w, day, True)
        checked.append(day)
        check_days(w, *checked, is_valid=True)


def test_weekdays_append_add_remove():
    from dataclass_property.weekdays_list import Weekdays

    w = Weekdays()
    check_days(w)

    w.remove('SUnday')
    check_days(w, 'sunday', is_valid=False)

    # Check append and order
    w.append('sunday')
    assert all(d1 == d2 for d1, d2 in zip(w, Weekdays.DAYS))

    w.mon = False
    check_days(w, 'monday', is_valid=False)
    w += ['Mon']  # Extend is used in the background so if this works extend works as well
    assert all(d1 == d2 for d1, d2 in zip(w, Weekdays.DAYS))

    w.pop(2)  # Tuesday
    check_days(w, 'tuesday', is_valid=False)
    w2 = w + ['TUESDAY']
    print(w2, type(w2))
    assert len(w2) != len(w)
    assert all(d1 == d2 for d1, d2 in zip(w2, Weekdays.DAYS))
    w3 = ['Tuesday'] + w
    assert len(w3) != len(w)
    assert all(d1 == d2 for d1, d2 in zip(w3, Weekdays.DAYS))


def test_weekday_pydantic():
    from pydantic import BaseModel
    from dataclass_property.weekdays_list import Weekdays

    # Check pydantic default None
    class MyModel(BaseModel):
        weekdays: Weekdays = None

        class Config:
            validate_assignment = True

    m = MyModel()
    assert m.weekdays is None

    # Check pydantic default Weekdays
    class MyModel(BaseModel):
        weekdays: Weekdays = Weekdays()  # Empty fills will all days

        class Config:
            validate_assignment = True

    m = MyModel()
    assert isinstance(m.weekdays, Weekdays)
    check_days(m.weekdays)  # All days should validate

    m.weekdays.remove('sunday')
    assert isinstance(m.weekdays, Weekdays)
    check_days(m.weekdays, 'sunday', is_valid=False)  # Make sure sunday is not in the list

    # Check mutable default for changed option
    m2 = MyModel()
    assert isinstance(m2.weekdays, Weekdays)
    check_days(m2.weekdays)  # All days should validate


if __name__ == '__main__':
    test_weekdays_init()
    test_weekday_property()
    test_weekdays_append_add_remove()
    test_weekday_pydantic()

    print('All tests finished successfully!')
