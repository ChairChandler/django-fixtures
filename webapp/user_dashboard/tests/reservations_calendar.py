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

        validator = validate_time(
            min_time=datetime.time(minute=15),
            max_time=datetime.time(hour=4)
        )

        for d in durations:
            validator(d)

    def test_invalid_unit_duration(self):
        "Unit duration can't pass for values lower than 15 minutes or above 4 hours."
        durations = self.manager.test_invalid_unit_duration

        validator = validate_time(
            min_time=datetime.time(minute=15),
            max_time=datetime.time(hour=4)
        )

        for d in durations:
            with self.assertRaises(ReservationsCalendar.TimeError):
                validator(d)

    def test_valid_lock_time(self):
        "Lock time must pass for values between 30 minutes up to 1 day."
        lock_times = self.manager.test_valid_lock_time

        validator = validate_time(
            min_time=datetime.time(minute=30),
            max_time=datetime.time(hour=23, minute=59, second=59)
        )

        for t in lock_times:
            validator(t)

    def test_invalid_lock_time(self):
        "Lock time cannot pass for values below 30 minutes or above 1 day."
        lock_times = self.manager.test_invalid_lock_time

        validator = validate_time(
            min_time=datetime.time(hour=1),
            max_time=datetime.time(hour=23, minute=59, second=59)
        )

        for t in lock_times:
            with self.assertRaises(ReservationsCalendar.TimeError):
                validator(t)

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
