
class Year:
    def __init__(self, year: int, months=None):
        self.available = True
        self.months = []
        self.year = year
        pass


class Month:
    def __init__(self, month, days=None, days_count=None):
        self.available = True
        self.days = []
        self.month = month
        self.days_count = days_count
        pass


class Day:
    def __init__(self, day, time=None):
        self.available = True
        self.time = []
        self.day = day
        self.hand_date = False
        pass


class Time:
    def __init__(self, hours, minutes):
        self.available = True
        self.time = (hours, minutes)
        if len(str(hours)) != 2:
            hours = '0' + str(hours)
        if len(str(minutes)) != 2:
            minutes = '0' + str(minutes)
        self.str_time = f"{hours}:{minutes}"
