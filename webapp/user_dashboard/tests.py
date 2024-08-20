from datetime import datetime, timedelta
from django.forms import ValidationError
import pytest
from django.test import TestCase
from .models import ReservationUnit, ReservationsCalendar
# Create your tests here.


@pytest.fixture
def start_date():
    return datetime.now()


@pytest.fixture
def valid_stop_date(start_date: datetime):
    return start_date + timedelta(minutes=1)


@pytest.fixture
def invalid_stop_date(start_date: datetime):
    return start_date - timedelta(minutes=1)


class ReservationUnitTest(TestCase):
    def test_valid_dates(
        self,
        start_date: datetime,
        valid_stop_date: datetime
    ):
        "If start date is before stop date, then create reservation."
        o = ReservationUnit.objects.create(
            date_start=start_date,
            date_stop=valid_stop_date
        )
        o.full_clean()
        self.assertTrue(ReservationUnit.objects.get(pk=o.pk))

    def test_invalid_dates(
        self,
        start_date: datetime,
        invalid_stop_date: datetime
    ):
        "If start date is after stop date, then throw exception."
        o = ReservationUnit.objects.create(
            date_start=start_date,
            date_stop=invalid_stop_date
        )
        with self.assertRaises(ValidationError):
            o.full_clean()

class ReservationsCalendarTest(TestCase):
    pass
