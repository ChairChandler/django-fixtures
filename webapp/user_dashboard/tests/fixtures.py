from datetime import datetime, time, timedelta
from more_itertools import first
import pytest
from user_dashboard.models import ReservationsCalendar

#
#
# ReservationsCalendar
#
#


@pytest.fixture(scope='session', autouse=True)
def valid_week_dates():
    n = datetime.now()
    return [
        datetime.date(n),
        datetime.date(n) + timedelta(days=7),
        datetime.date(n) + timedelta(days=14),
        datetime.date(n) + timedelta(days=30)
    ]


@pytest.fixture(scope='session', autouse=True)
def invalid_week_dates():
    n = datetime.now()
    return [
        datetime.date(n),
        datetime.date(n) + timedelta(days=2),
        datetime.date(n) + timedelta(days=5),
        datetime.date(n) + timedelta(days=30)
    ]


@pytest.fixture(scope='session', autouse=True)
def example_valid_week_date(valid_week_dates):
    return first(valid_week_dates)


@pytest.fixture(scope='session', autouse=True)
def valid_unit_duration_values():
    return [
        time(minute=15),
        time(minute=30),
        time(hour=1),
        time(hour=3, minute=59),
        time(hour=4)
    ]


@pytest.fixture(scope='session', autouse=True)
def invalid_unit_duration_values():
    return [
        time(minute=2),
        time(minute=14),
        time(hour=4, minute=1),
        time(hour=8)
    ]


@pytest.fixture(scope='session', autouse=True)
def example_valid_unit_duration(valid_unit_duration_values):
    return first(valid_unit_duration_values)

#
#
# ReservationUnit
#
#


@pytest.fixture(scope='session', autouse=True)
def start_date():
    return datetime.now()


@pytest.fixture(scope='session', autouse=True)
def valid_stop_dates(start_date: datetime):
    return [
        start_date + timedelta(minutes=1),
        start_date + timedelta(minutes=30),
        start_date + timedelta(hours=1),
        start_date + timedelta(days=1)
    ]


@pytest.fixture(scope='session', autouse=True)
def invalid_stop_dates(start_date: datetime):
    return [
        start_date - timedelta(minutes=1),
        start_date - timedelta(minutes=30),
        start_date - timedelta(hours=1),
        start_date - timedelta(days=1)
    ]


@pytest.fixture(scope='session', autouse=True)
def example_valid_stop_date(valid_stop_dates: list[datetime]):
    return first(valid_stop_dates)


@pytest.fixture(scope='session', autouse=True)
def example_invalid_stop_date(invalid_stop_dates: list[datetime]):
    return first(invalid_stop_dates)


@pytest.fixture(scope='session', autouse=True)
def example_calendar(
    example_valid_week_date: datetime,
    valid_unit_duration_values: list[time]
):
    example_unit_duration = first(valid_unit_duration_values)
    return ReservationsCalendar.objects.create(
        week_date=example_valid_week_date,
        unit_duration=example_unit_duration
    )


@pytest.fixture(scope='session', autouse=True)
def valid_reservation_dates(start_date: datetime):
    diff = timedelta(hours=1)
    return [
        (start_date, start_date + diff),
        (start_date + diff, start_date + 2*diff),
        (start_date + 10*diff, start_date + 11*diff)
    ]


@pytest.fixture(scope='session', autouse=True)
def invalid_reservation_dates(start_date: datetime):
    "(start, stop)"
    diff = timedelta(hours=1)
    return [
        (start_date, start_date + diff),
        (start_date + 0.5*diff, start_date + 2*diff),
        (start_date + 1.5*diff, start_date + 5*diff)
    ]
