from django.test import TestCase
from user_dashboard.models import *
from .fixtures import ReservationsCalendarFixturesManager
# Create your tests here.


class ReservationsCalendarTest(TestCase):
    manager = ReservationsCalendarFixturesManager()

    def tearDown(self):
        ReservationsCalendar.objects.all().delete()

    def test_valid_unit_duration(self):
        "Unit duration must pass for values between 15 minutes up to 4 hours."
        durations = self.manager.test_valid_unit_duration

        # lazy field - ignore
        validator = ReservationsCalendar.unit_duration.field.validators[0]  # type: ignore

        for d in durations:
            validator(d)

    def test_invalid_unit_duration(self):
        "Unit duration can't pass for values lower than 15 minutes or above 4 hours."
        durations = self.manager.test_invalid_unit_duration

        # lazy field - ignore
        validator = ReservationsCalendar.unit_duration.field.validators[0] # type: ignore

        for d in durations:
            with self.assertRaises(ReservationsCalendar.UnitDurationError):
                validator(d)

    def test_calendar_doesnt_interleaves_with_others(self):
        "Multiple calendars have different valid times ranges (valid)."
        (
            weeks,
            duration
        ) = self.manager.test_calendar_doesnt_interleaves_with_others

        for date in weeks:
            o = ReservationsCalendar.objects.create(
                week_date=date,
                unit_duration=duration
            )
            validate_calendar(o)

    def test_calendar_interleave_with_others(self):
        "Multiple calendars interleaves in dates with each other (invalid)."
        (
            first_insert_date,
            unit_duration,
            another_insert_dates
        ) = self.manager.test_calendar_interleave_with_others

        # insert first
        o = ReservationsCalendar.objects.create(
            week_date=first_insert_date,
            unit_duration=unit_duration
        )
        # check the rest
        for date in another_insert_dates:
            with self.assertRaises(ReservationsCalendar.InterleaveError):
                o = ReservationsCalendar.objects.create(
                    week_date=date,
                    unit_duration=unit_duration
                )
                validate_calendar(o)
