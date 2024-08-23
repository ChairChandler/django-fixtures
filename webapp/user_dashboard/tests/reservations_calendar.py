from datetime import datetime, time
from django.forms import ValidationError
from more_itertools import first
from django.test import TestCase
from user_dashboard.models import ReservationsCalendar
# Create your tests here.


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
