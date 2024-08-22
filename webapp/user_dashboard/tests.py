from datetime import datetime, time, timedelta
from django.forms import ValidationError
from more_itertools import first
import pytest
from django.test import TestCase
from webapp.user_dashboard.tests import example_calendar, start_date
from .models import ReservationUnit, ReservationsCalendar
# Create your tests here.


@pytest.fixture
def valid_week_dates():
    n = datetime.now()
    return [
        datetime.date(n),
        datetime.date(n) + timedelta(days=7),
        datetime.date(n) + timedelta(days=14),
        datetime.date(n) + timedelta(days=30)
    ]


@pytest.fixture
def invalid_week_dates():
    n = datetime.now()
    return [
        datetime.date(n),
        datetime.date(n) + timedelta(days=2),
        datetime.date(n) + timedelta(days=5),
        datetime.date(n) + timedelta(days=30)
    ]


@pytest.fixture
def example_valid_week_date(valid_week_dates):
    return first(valid_week_dates)


@pytest.fixture
def valid_unit_duration_values():
    return [
        time(minute=15),
        time(minute=30),
        time(hour=1),
        time(hour=3, minute=59),
        time(hour=4)
    ]


@pytest.fixture
def invalid_unit_duration_values():
    return [
        time(minute=2),
        time(minute=14),
        time(hour=4, minute=1),
        time(hour=8)
    ]


@pytest.fixture
def example_valid_unit_duration(valid_unit_duration_values):
    return first(valid_unit_duration_values)


class ReservationsCalendarTest(TestCase):
    def test_valid_unit_duration(
        self,
        example_valid_week_date: datetime,
        valid_unit_duration_values: list[time],
    ):
        "Unit duration must pass for values between 15 minutes up to 4 hours."
        for duration in valid_unit_duration_values:
            o = ReservationsCalendar.objects.create(
                week_date=example_valid_week_date,
                unit_duration=duration
            )
            o.full_clean()
            self.assertTrue(ReservationsCalendar.objects.get(pk=o.pk))

    def test_invalid_unit_duration(
        self,
        example_valid_week_date: datetime,
        invalid_unit_duration_values: list[time]
    ):
        "Unit duration can't pass for values lower than 15 minutes or above 4 hours."
        for duration in invalid_unit_duration_values:
            with self.assertRaises(ValidationError):
                o = ReservationsCalendar.objects.create(
                    week_date=example_valid_week_date,
                    unit_duration=duration
                )
                o.full_clean()

    def test_calendar_doesnt_interleaves_with_others(
        self,
        valid_week_dates: list[datetime],
        example_valid_unit_duration: time
    ):
        "Multiple calendars have different valid times ranges (valid)."
        for date in valid_week_dates:
            o = ReservationsCalendar.objects.create(
                week_date=date,
                unit_duration=example_valid_unit_duration
            )
            o.full_clean()
            self.assertTrue(ReservationsCalendar.objects.get(pk=o.pk))

    def test_calendar_interleave_with_others(
        self,
        invalid_week_dates: list[datetime],
        example_valid_unit_duration: time
    ):
        "Multiple calendars interleaves in dates with each other (invalid)."
        # insert first
        o = ReservationsCalendar.objects.create(
            week_date=first(invalid_week_dates),
            unit_duration=example_valid_unit_duration
        )
        o.full_clean()
        # check the rest
        for date in invalid_week_dates[1:]:
            with self.assertRaises(ValidationError):
                o = ReservationsCalendar.objects.create(
                    week_date=date,
                    unit_duration=example_valid_unit_duration
                )
                o.full_clean()


@pytest.fixture
def start_date():
    return datetime.now()


@pytest.fixture
def valid_stop_dates(start_date: datetime):
    return [
        start_date + timedelta(minutes=1),
        start_date + timedelta(minutes=30),
        start_date + timedelta(hours=1),
        start_date + timedelta(days=1)
    ]


@pytest.fixture
def invalid_stop_dates(start_date: datetime):
    return [
        start_date - timedelta(minutes=1),
        start_date - timedelta(minutes=30),
        start_date - timedelta(hours=1),
        start_date - timedelta(days=1)
    ]


@pytest.fixture
def example_valid_stop_date(valid_stop_dates: list[datetime]):
    return first(valid_stop_dates)


@pytest.fixture
def example_invalid_stop_date(invalid_stop_dates: list[datetime]):
    return first(invalid_stop_dates)


@pytest.fixture
def example_calendar(
    example_valid_week_date: datetime,
    valid_unit_duration_values: list[time]
):
    example_unit_duration = first(valid_unit_duration_values)
    return ReservationsCalendar.objects.create(
        week_date=example_valid_week_date,
        unit_duration=example_unit_duration
    )


@pytest.fixture
def valid_reservation_dates(start_date: datetime):
    diff = timedelta(hours=1)
    return [
        (start_date, start_date + diff),
        (start_date + diff, start_date + 2*diff),
        (start_date + 10*diff, start_date + 11*diff)
    ]


@pytest.fixture
def invalid_reservation_dates(start_date: datetime):
    diff = timedelta(hours=1)
    return [
        (start_date, start_date + diff),
        (start_date + 0.5*diff, start_date + 2*diff),
        (start_date + 1.5*diff, start_date + 5*diff)
    ]


class ReservationUnitTest(TestCase):
    def test_valid_dates(
        self,
        start_date: datetime,
        example_valid_stop_date: datetime,
        example_calendar: ReservationsCalendar
    ):
        "If start date is before stop date, then create reservation."
        o = ReservationUnit.objects.create(
            date_start=start_date,
            date_stop=example_valid_stop_date,
            calendar=example_calendar
        )
        o.full_clean()
        self.assertTrue(ReservationUnit.objects.get(pk=o.pk))

    def test_invalid_dates(
        self,
        start_date: datetime,
        example_invalid_stop_date: datetime,
        example_calendar: ReservationsCalendar
    ):
        "If start date is after stop date, then throw exception."
        o = ReservationUnit.objects.create(
            date_start=start_date,
            date_stop=example_invalid_stop_date,
            calendar=example_calendar
        )
        with self.assertRaises(ValidationError):
            o.full_clean()

    def test_valid_unique_reservations(
        self,
        example_calendar: ReservationsCalendar,
        valid_reservation_dates: list[tuple]
    ):
        '''
        If reservations are assigned to the same calendar and not interleaves
        with each other, then pass.
        '''
        pass

    def test_invalid_unique_reservations(
        self,
        example_calendar: ReservationsCalendar,
        invalid_reservation_dates: list[tuple]
    ):
        '''
        If reservations are assigned to the same calendar and interleaves
        with each other, then fail.
        '''
        pass

    def test_valid_dates_with_calendar_dates(
        self,
        example_calendar: ReservationsCalendar
    ):
        '''
        If reservations dates are in calendar week date, then pass. 
        '''
        pass

    def test_invalid_dates_with_calendar_dates(
        self,
        example_calendar: ReservationsCalendar
    ):
        '''
        If reservations dates are not in calendar week date, then fail.
        '''
        pass

    def test_valid_reservation_duration(
        self,
        example_calendar: ReservationsCalendar
    ):
        '''
        If reservation duration is different than calendar reservation duration, then fail.
        '''
        pass

    def test_invalid_reservation_duration(
        self,
        example_calendar: ReservationsCalendar
    ):
        '''
        If reservation duration is different than calendar reservation duration, then fail.
        '''
        pass
