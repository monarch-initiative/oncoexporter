import math



class Iso8601Mapper:
    """
    # Mapping various input formats for age to iso8601
    # Although conceptuallz simple, it is messy to go from days to years and months
    # None of the available libraries seem to do a good job.
    # pandas does this conversion automatically: https://pandas.pydata.org/docs/reference/api/pandas.Timedelta.isoformat.html
    td = pd.Timedelta(days=days)
    iso = td.isoformat() # returns ISO 8601 duration string: td = pd.Timedelta(days=10350); td.isoformat(); 'P10350DT0H0M0S'
    return iso
    # does not work (does not create Y and M entries)
    """

    def __init__(self, y:int=None, m:int=None,d:int=None) -> None:
        self._years = y
        self._months = m
        self._days = d

    def to_iso8601(self):
        components = ["P"]
        if self._years > 0:
            components.append(f"{self._years}Y")
        if self._months > 0:
            components.append(f"{self._months}M")
        if self._days > 0:
            components.append(f"{self._days}D")
        return "".join(components)


    @staticmethod
    def from_days(days):
        if isinstance(days, str):
            days = int(str)
        if isinstance(days, float) and not math.isnan(days):
            days = int(days) # this is because some values are like 73.0
        if not isinstance(days, int):
            raise ValueError(f"days argument ({days}) must be int or str but was {type(days)}")
        # calculate number of years
        years = math.floor(days / 365.25)
        if years > 0:
            days = days - int(years * 365.25)
        months = math.floor(days / 30.436875)
        if months > 0:
            days = days - int(months * 30.436875)
        mapper =  Iso8601Mapper(y=years, m=months, d=days)
        return mapper.to_iso8601()
