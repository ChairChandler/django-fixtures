from datetime import datetime, time, timedelta, date
from more_itertools import first
from user_dashboard.models import ReservationsCalendar
import pytz
from webapp.settings import TIME_ZONE

#
#
# ReservationsCalendar
#
#

# I can't mix pytest fixtures with Django tests easily, I would like also
# to avoid Django fixtures files, so decided to use manual objects access
# to get fixtures workaround.


tz_info = pytz.timezone(TIME_ZONE)


class ReservationsCalendarFixtures:
    @property
    def valid_week_dates(self) -> list[date]:
        n = datetime.date(datetime.now(tz=tz_info))
        return [
            n,
            n + timedelta(days=7),
            n + timedelta(days=14),
            n + timedelta(days=30),
            n + timedelta(days=60)
        ]

    @property
    def invalid_week_dates(self) -> list[date]:
        n = datetime.date(datetime.now(tz=tz_info))
        return [
            n,
            n + timedelta(days=2),
            n + timedelta(days=5),
            n + timedelta(days=9),
            n + timedelta(days=12)
        ]

    @property
    def valid_unit_duration_values(self) -> list[time]:
        return [
            time(minute=15, tzinfo=tz_info),
            time(minute=30, tzinfo=tz_info),
            time(hour=1, tzinfo=tz_info),
            time(hour=3, minute=59, tzinfo=tz_info),
            time(hour=4, tzinfo=tz_info)
        ]

    @property
    def invalid_unit_duration_values(self) -> list[time]:
        return [
            time(minute=2, tzinfo=tz_info),
            time(minute=14, tzinfo=tz_info),
            time(hour=4, minute=1, tzinfo=tz_info),
            time(hour=8, tzinfo=tz_info),
            time(hour=12, tzinfo=tz_info)
        ]

    @property
    def example_valid_unit_duration(self) -> time:
        return first(self.valid_unit_duration_values)

#
#
# ReservationUnit
#
#


class ReservationUnitFixtures:
    @property
    def start_date(self) -> date:
        return datetime.now(tz=tz_info)

    @property
    def valid_stop_dates(self) -> list[date]:
        return [
            self.start_date + timedelta(minutes=1),
            self.start_date + timedelta(minutes=30),
            self.start_date + timedelta(hours=1),
            self.start_date + timedelta(days=1),
            self.start_date + timedelta(days=2)
        ]

    @property
    def invalid_stop_dates(self) -> list[date]:
        return [
            self.start_date - timedelta(minutes=1),
            self.start_date - timedelta(minutes=30),
            self.start_date - timedelta(hours=1),
            self.start_date - timedelta(days=1),
            self.start_date - timedelta(days=2)
        ]

    @property
    def example_valid_stop_date(self) -> date:
        return first(self.valid_stop_dates)

    @property
    def example_invalid_stop_date(self) -> date:
        return first(self.invalid_stop_dates)

    @property
    def example_calendar(self) -> ReservationsCalendar:
        calendar_fixtures = ReservationsCalendarFixtures()

        example_unit_duration = first(
            calendar_fixtures.valid_unit_duration_values
        )
        return ReservationsCalendar.objects.create(
            week_date=first(calendar_fixtures.valid_week_dates),
            unit_duration=example_unit_duration
        )

    @property
    def valid_reservation_dates(self) -> list[tuple[date, date]]:
        '''
        [r1, r2, r3]

        r = (start_date, stop_date)

        r1 < r2 < r3
        '''
        diff = timedelta(hours=1)
        return [
            (self.start_date, self.start_date + diff),
            (self.start_date + diff, self.start_date + 2*diff),
            (self.start_date + 10*diff, self.start_date + 11*diff)
        ]

    @property
    def invalid_reservation_dates(self) -> list[tuple[date, date]]:
        '''
        [r1, r2, r3]

        r = (start_date, stop_date)

        r[i+1].start_date < r[i].stop_date
        '''
        diff = timedelta(hours=1)
        return [
            (self.start_date, self.start_date + diff),
            (self.start_date + 0.5*diff, self.start_date + 2*diff),
            (self.start_date + 1.5*diff, self.start_date + 5*diff)
        ]
