from django.test import TestCase
from user_dashboard.models import *
from .fixtures import ReservationUnitFixturesManager


class ReservationUnitTest(TestCase):
    manager = ReservationUnitFixturesManager()

    def tearDown(self):
        ReservationUnit.objects.all().delete()

    def test_valid_dates(self):
        "If start date is before stop date, then create reservation."
        (
            date_start,
            date_stop,
            calendar
        ) = self.manager.test_valid_dates

        o = ReservationUnit.objects.create(
            date_start=date_start,
            date_stop=date_stop,
            calendar=calendar
        )
        validate_reservation_dates(o)

    def test_invalid_dates(self):
        "If start date is after stop date, then throw exception."
        (
            date_start,
            date_stop,
            calendar
        ) = self.manager.test_invalid_dates

        with self.assertRaises(ReservationUnit.InvalidDateError):
            o = ReservationUnit.objects.create(
                date_start=date_start,
                date_stop=date_stop,
                calendar=calendar
            )
            validate_reservation_dates(o)

    def test_valid_unique_reservations(self):
        '''
        If reservations are assigned to the same calendar and not interleaves
        with each other, then pass.
        '''
        (
            dates,
            calendar
        ) = self.manager.test_valid_unique_reservations

        for start, stop in dates:
            o = ReservationUnit.objects.create(
                date_start=start,
                date_stop=stop,
                calendar=calendar
            )
            validate_unique_reservation(o)

    def test_invalid_unique_reservations(self):
        '''
        If reservations are assigned to the same calendar and interleaves
        with each other, then fail.
        '''
        (
            (start, stop),
            another_dates,
            calendar
        ) = self.manager.test_invalid_unique_reservations

        # create first object
        ReservationUnit.objects.create(
            date_start=start,
            date_stop=stop,
            calendar=calendar
        )
        for start, stop in another_dates:
            with self.assertRaises(ReservationUnit.CalendarReservationError):
                o = ReservationUnit.objects.create(
                    date_start=start,
                    date_stop=stop,
                    calendar=calendar
                )
                validate_unique_reservation(o)

    def test_invalid_dates_with_calendar_dates(self):
        '''
        If reservations dates are not in calendar week date, then fail.
        '''
        (
            calendar,
            invalid_dates
        ) = self.manager.test_invalid_dates_with_calendar_dates

        for start, stop in invalid_dates:
            with self.assertRaises(ReservationUnit.CalendarDateError):
                o = ReservationUnit.objects.create(
                    date_start=start,
                    date_stop=stop,
                    calendar=calendar
                )
                validate_calendar_reservation(o)

    def test_invalid_reservation_duration(self):
        '''
        If reservation duration is different than calendar reservation duration, then fail.
        '''
        (
            calendar,
            diff
        ) = self.manager.test_invalid_reservation_duration

        with self.assertRaises(ReservationUnit.CalendarDurationError):
            o = ReservationUnit.objects.create(
                date_start=calendar.week_date,
                date_stop=calendar.week_date + diff,
                calendar=calendar
            )
            validate_calendar_reservation(o)
