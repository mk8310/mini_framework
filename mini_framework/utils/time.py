from datetime import datetime, timedelta, date

FMT_DATETIME = "%Y-%m-%d %H:%M:%S"
FMT_DATE = "%Y-%m-%d"


class TimeUtils:
    @staticmethod
    def now() -> datetime:
        return datetime.now()

    @staticmethod
    def epoch_milliseconds(dt: datetime) -> float:
        return dt.timestamp()

    @staticmethod
    def from_epoch_milliseconds(milliseconds: float) -> datetime:
        return datetime.fromtimestamp(milliseconds)

    @staticmethod
    def add_seconds(dt: datetime, seconds: int) -> datetime:
        return dt + timedelta(seconds=seconds)

    @staticmethod
    def add_minutes(dt: datetime, minutes: int) -> datetime:
        return dt + timedelta(minutes=minutes)

    @staticmethod
    def add_hours(dt: datetime, hours: int) -> datetime:
        return dt + timedelta(hours=hours)

    @staticmethod
    def add_days(dt: datetime, days: int) -> datetime:
        return dt + timedelta(days=days)

    @staticmethod
    def add_weeks(dt: datetime, weeks: int) -> datetime:
        return dt + timedelta(weeks=weeks)

    @staticmethod
    def add_months(dt: datetime, months: int) -> datetime:
        return dt.replace(month=dt.month + months)

    @staticmethod
    def add_years(dt: datetime, years: int) -> datetime:
        return dt.replace(year=dt.year + years)

    @staticmethod
    def format(dt: datetime, fmt: str = FMT_DATETIME) -> str:
        return dt.strftime(fmt)

    @staticmethod
    def parse(time_str: str, fmt: str = FMT_DATETIME) -> datetime:
        return datetime.strptime(time_str, fmt)

    @staticmethod
    def from_iso_format(time_str: str) -> datetime:
        return datetime.fromisoformat(time_str)


class DateUtil:
    @staticmethod
    def now() -> date:
        return datetime.now().date()

    @staticmethod
    def epoch_milliseconds(dt: date) -> int:
        zero_time = datetime.combine(dt, datetime.min.time())
        return int(zero_time.timestamp() * 1000)

    @staticmethod
    def from_epoch_milliseconds(milliseconds: int) -> date:
        return datetime.fromtimestamp(milliseconds / 1000).date()

    @staticmethod
    def add_days(dt: date, days: int) -> date:
        return dt + timedelta(days=days)

    @staticmethod
    def add_weeks(dt: date, weeks: int) -> date:
        return dt + timedelta(weeks=weeks)

    @staticmethod
    def add_months(dt: date, months: int) -> date:
        return dt.replace(month=dt.month + months)

    @staticmethod
    def add_years(dt: date, years: int) -> date:
        return dt.replace(year=dt.year + years)

    @staticmethod
    def format(dt: date, fmt: str = FMT_DATE) -> str:
        return dt.strftime(fmt)

    @staticmethod
    def parse(time_str: str, fmt: str = FMT_DATE) -> date:
        return datetime.strptime(time_str, fmt).date()
