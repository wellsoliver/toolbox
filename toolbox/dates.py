from datetime import timedelta, date


def date_iterator(start_date, days, include_start=True):
    """
    Yields a sequence of dates increasing by one from a start date
    """
    for i in range(days):
        y = i if include_start else i+1
        yield start_date + timedelta(days=y)