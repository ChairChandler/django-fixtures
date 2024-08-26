from .fixtures import *


class ReservationsCalendarFixturesManager:
    fixtures = ReservationsCalendarFixtures()

    @property
    def test_valid_unit_duration(self):

        durations = self.fixtures.valid_unit_duration_values

        return durations

    @property
    def test_invalid_unit_duration(self):

        durations = self.fixtures.invalid_unit_duration_values

        return durations

    @property
    def test_calendar_doesnt_interleaves_with_others(self):

        weeks = self.fixtures.valid_week_dates
        duration = first(self.fixtures.valid_unit_duration_values)

        return weeks, duration

    @property
    def test_calendar_interleave_with_others(self):

        first_insert_date = first(self.fixtures.invalid_week_dates)
        unit_duration = first(self.fixtures.valid_unit_duration_values)
        another_insert_dates = self.fixtures.invalid_week_dates[1:]

        return first_insert_date, unit_duration, another_insert_dates


class ReservationUnitFixturesManager:
    units_fixtures = ReservationUnitFixtures()
    calendar_fixtures = ReservationsCalendarFixtures()

    @property
    def test_valid_dates(self):

        date_start = self.units_fixtures.start_date
        date_stop = first(self.units_fixtures.valid_stop_dates)
        calendar = self.units_fixtures.example_calendar

        return date_start, date_stop, calendar

    @property
    def test_invalid_dates(self):

        date_start = self.units_fixtures.start_date
        date_stop = first(self.units_fixtures.invalid_stop_dates)
        calendar = self.units_fixtures.example_calendar

        return date_start, date_stop, calendar

    @property
    def test_valid_unique_reservations(self):

        dates = self.units_fixtures.valid_reservation_dates
        calendar = self.units_fixtures.example_calendar

        return dates, calendar

    @property
    def test_invalid_unique_reservations(self):

        first_date = first(self.units_fixtures.invalid_reservation_dates)
        another_dates = self.units_fixtures.invalid_reservation_dates[1:]
        calendar = self.units_fixtures.example_calendar

        return first_date, another_dates, calendar

    @property
    def test_invalid_dates_with_calendar_dates(self):

        calendar = self.units_fixtures.example_calendar
        invalid_dates = self.units_fixtures.invalid_dates_with_calendar_dates

        return calendar, invalid_dates

    @property
    def test_invalid_reservation_duration(self):

        calendar = self.units_fixtures.example_calendar
        diff = self.units_fixtures.invalid_reservation_duration

        return calendar, diff
