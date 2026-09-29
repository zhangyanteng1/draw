import datetime
from dateutil.relativedelta import relativedelta
import calendar
from typing import Union, Tuple, Optional


class DateUtils:
    """
    Python 日期处理工具类
    包含常见的日期操作功能
    """

    @staticmethod
    def get_current_date() -> datetime.date:
        """获取当前日期(年月日)"""
        return datetime.date.today()

    @staticmethod
    def get_current_datetime() -> datetime.datetime:
        """获取当前日期时间(年月日时分秒) """
        return datetime.datetime.now()

    @staticmethod
    def get_current_timestamp() -> float:
        """获取当前时间戳"""
        return datetime.datetime.now().timestamp()

    @staticmethod
    def date_to_str(date: Union[datetime.date, datetime.datetime], fmt: str = "%Y-%m-%d") -> str:
        """日期转字符串

        Args:
            date: 日期对象
            fmt: 格式字符串，默认为'%Y-%m-%d'

        Returns:
            格式化后的日期字符串
        """
        return date.strftime(fmt)

    @staticmethod
    def str_to_date(date_str: str, fmt: str = "%Y-%m-%d") -> datetime.date:
        """字符串转日期

        Args:
            date_str: 日期字符串
            fmt: 格式字符串，默认为'%Y-%m-%d'

        Returns:
            日期对象
        """
        return datetime.datetime.strptime(date_str, fmt).date()

    @staticmethod
    def str_to_datetime(datetime_str: str, fmt: str = "%Y-%m-%d %H:%M:%S") -> datetime.datetime:
        """字符串转日期时间

        Args:
            datetime_str: 日期时间字符串
            fmt: 格式字符串，默认为'%Y-%m-%d %H:%M:%S'

        Returns:
            日期时间对象
        """
        return datetime.datetime.strptime(datetime_str, fmt)

    @staticmethod
    def timestamp_to_datetime(timestamp: float) -> datetime.datetime:
        """时间戳转日期时间

        Args:
            timestamp: 时间戳

        Returns:
            日期时间对象
        """
        return datetime.datetime.fromtimestamp(timestamp)

    @staticmethod
    def datetime_to_timestamp(dt: datetime.datetime) -> float:
        """日期时间转时间戳

        Args:
            dt: 日期时间对象

        Returns:
            时间戳
        """
        return dt.timestamp()

    @staticmethod
    def add_days(date: Union[datetime.date, datetime.datetime], days: int) -> datetime.date:
        """日期加减天数

        Args:
            date: 日期对象
            days: 要加减的天数(正数为加，负数为减)

        Returns:
            计算后的日期对象
        """
        if isinstance(date, datetime.datetime):
            return date + datetime.timedelta(days=days)
        return date + datetime.timedelta(days=days)

    @staticmethod
    def add_months(date: Union[datetime.date, datetime.datetime], months: int) -> datetime.date:
        """日期加减月份

        Args:
            date: 日期对象
            months: 要加减的月数(正数为加，负数为减)

        Returns:
            计算后的日期对象
        """
        return date + relativedelta(months=months)

    @staticmethod
    def get_months(months: int = 0) -> str:
        """日期加减月份,返回年-月格式字符串

        Returns:
            日期字符串
        """
        month = DateUtils.add_months(DateUtils.get_current_date(), months)
        return month.strftime('%Y-%m')

    @staticmethod
    def add_years(date: Union[datetime.date, datetime.datetime], years: int) -> datetime.date:
        """日期加减年数

        Args:
            date: 日期对象
            years: 要加减的年数(正数为加，负数为减)

        Returns:
            计算后的日期对象
        """
        return date + relativedelta(years=years)

    @staticmethod
    def get_weekday(date: Union[datetime.date, datetime.datetime]) -> int:
        """获取星期几(1-7, 1表示周一，7表示周日)

        Args:
            date: 日期对象

        Returns:
            星期几的数字表示
        """
        return date.isoweekday()

    @staticmethod
    def get_weekday_name(date: Union[datetime.date, datetime.datetime], short: bool = False) -> str:
        """获取星期几的名称

        Args:
            date: 日期对象
            short: 是否返回简称(默认False)

        Returns:
            星期几的名称
        """
        weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        short_weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        weekday = date.weekday()  # 0-6, Monday is 0
        return short_weekdays[weekday] if short else weekdays[weekday]

    @staticmethod
    def is_weekend(date: Union[datetime.date, datetime.datetime]) -> bool:
        """判断是否是周末

        Args:
            date: 日期对象

        Returns:
            True如果是周末，否则False
        """
        return date.weekday() >= 5  # 5=Saturday, 6=Sunday

    @staticmethod
    def get_month_days(date: Union[datetime.date, datetime.datetime]) -> int:
        """获取指定日期所在月份的天数

        Args:
            date: 日期对象

        Returns:
            该月的天数
        """
        return calendar.monthrange(date.year, date.month)[1]

    @staticmethod
    def get_first_day_of_month(date: Union[datetime.date, datetime.datetime]) -> datetime.date:
        """获取指定日期所在月份的第一天

        Args:
            date: 日期对象

        Returns:
            该月的第一天
        """
        return date.replace(day=1)

    @staticmethod
    def get_last_day_of_month(date: Union[datetime.date, datetime.datetime]) -> datetime.date:
        """获取指定日期所在月份的最后一天

        Args:
            date: 日期对象

        Returns:
            该月的最后一天
        """
        return date.replace(day=calendar.monthrange(date.year, date.month)[1])

    @staticmethod
    def get_date_range(start_date: Union[datetime.date, datetime.datetime, str],
                       end_date: Union[datetime.date, datetime.datetime, str],
                       date_format: str = "%Y-%m-%d") -> list:
        """获取两个日期之间的所有日期列表

        Args:
            start_date: 开始日期(可以是字符串或日期对象)
            end_date: 结束日期(可以是字符串或日期对象)
            date_format: 如果日期是字符串时的格式

        Returns:
            日期范围内的所有日期列表
        """
        if isinstance(start_date, str):
            start_date = DateUtils.str_to_date(start_date, date_format)
        if isinstance(end_date, str):
            end_date = DateUtils.str_to_date(end_date, date_format)

        date_list = []
        current_date = start_date
        while current_date <= end_date:
            date_list.append(current_date)
            current_date = DateUtils.add_days(current_date, 1)
        return date_list

    @staticmethod
    def get_days_diff(date1: Union[datetime.date, datetime.datetime],
                      date2: Union[datetime.date, datetime.datetime]) -> int:
        """计算两个日期之间的天数差

        Args:
            date1: 第一个日期
            date2: 第二个日期

        Returns:
            两个日期之间的天数差(date1 - date2)
        """
        if isinstance(date1, datetime.datetime):
            date1 = date1.date()
        if isinstance(date2, datetime.datetime):
            date2 = date2.date()
        return (date1 - date2).days

    @staticmethod
    def get_work_days(start_date: Union[datetime.date, datetime.datetime, str],
                      end_date: Union[datetime.date, datetime.datetime, str],
                      date_format: str = "%Y-%m-%d") -> int:
        """计算两个日期之间的工作日天数(不包括周末)

        Args:
            start_date: 开始日期(可以是字符串或日期对象)
            end_date: 结束日期(可以是字符串或日期对象)
            date_format: 如果日期是字符串时的格式

        Returns:
            两个日期之间的工作日天数
            两个日期之间的工作日天数
        """
        if isinstance(start_date, str):
            start_date = DateUtils.str_to_date(start_date, date_format)
        if isinstance(end_date, str):
            end_date = DateUtils.str_to_date(end_date, date_format)

        delta = datetime.timedelta(days=1)
        work_days = 0
        current_date = start_date
        while current_date <= end_date:
            if current_date.weekday() < 5:  # 0-4表示周一到周五
                work_days += 1
            current_date += delta
        return work_days

    @staticmethod
    def is_leap_year(year: int) -> bool:
        """判断是否是闰年

        Args:
            year: 年份

        Returns:
            True如果是闰年，否则False
        """
        return calendar.isleap(year)

    @staticmethod
    def get_age(birth_date: Union[datetime.date, datetime.datetime, str],
                current_date: Optional[Union[datetime.date, datetime.datetime, str]] = None,
                date_format: str = "%Y-%m-%d") -> int:
        """根据出生日期计算年龄

        Args:
            birth_date: 出生日期(可以是字符串或日期对象)
            current_date: 当前日期(可选，默认为今天)
            date_format: 如果日期是字符串时的格式

        Returns:
            年龄
        """
        if isinstance(birth_date, str):
            birth_date = DateUtils.str_to_date(birth_date, date_format)

        if current_date is None:
            current_date = DateUtils.get_current_date()
        elif isinstance(current_date, str):
            current_date = DateUtils.str_to_date(current_date, date_format)

        age = current_date.year - birth_date.year
        if (current_date.month, current_date.day) < (birth_date.month, birth_date.day):
            age -= 1
        return age

    @staticmethod
    def get_quarter(date: Union[datetime.date, datetime.datetime]) -> int:
        """获取日期所在的季度

        Args:
            date: 日期对象

        Returns:
            季度(1-4)
        """
        return (date.month - 1) // 3 + 1

    @staticmethod
    def get_quarter_range(year: int, quarter: int) -> Tuple[datetime.date, datetime.date]:
        """获取指定年份季度的开始和结束日期

        Args:
            year: 年份
            quarter: 季度(1-4)

        Returns:
            (季度开始日期, 季度结束日期)
        """
        if quarter == 1:
            start_date = datetime.date(year, 1, 1)
            end_date = datetime.date(year, 3, 31)
        elif quarter == 2:
            start_date = datetime.date(year, 4, 1)
            end_date = datetime.date(year, 6, 30)
        elif quarter == 3:
            start_date = datetime.date(year, 7, 1)
            end_date = datetime.date(year, 9, 30)
        else:
            start_date = datetime.date(year, 10, 1)
            end_date = datetime.date(year, 12, 31)
        return start_date, end_date

    @staticmethod
    def get_week_dates(weeks_offset=0):
        """
        获取指定周的周一至周日的日期（格式：年-月-日）

        参数:
        weeks_offset (int): 周偏移量。0表示本周，-1表示上周，1表示下周，依此类推。

        返回:
        list: 包含7个日期字符串的列表，从周一到周日
        """
        # 获取当前日期
        today = datetime.date.today()

        # 计算指定周的周一
        # 先找到本周的周一：today - 当前星期几（周一为0，周日为6）
        monday = today - datetime.timedelta(days=today.weekday())

        # 根据周偏移量调整
        target_monday = monday + datetime.timedelta(weeks=weeks_offset)

        # 生成整周的日期（周一到周日）
        week_dates = []
        for i in range(7):
            current_date = target_monday + datetime.timedelta(days=i)
            week_dates.append(current_date.strftime("%Y-%m-%d"))

        return week_dates

    @classmethod
    def get_datetime_range(cls, time: datetime) -> list[datetime]:
        start_time = time.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = time.replace(hour=23, minute=59, second=59, microsecond=0)
        return [start_time, end_time]

# if __name__ == '__main__':
#     now_time = DateUtils.get_current_date()
#     first_time = DateUtils.add_days(now_time, -30)
#     print(now_time)
#     print(first_time)

