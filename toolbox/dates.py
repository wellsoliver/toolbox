"""
Date iterators and other helpers
"""

from datetime import timedelta, date


def date_iterator(start_date, days):
    """Yields a sequence of dates increasing by one from a start date"""
    for i in range(days):
        yield start_date + timedelta(days=i)


def date_range_iterator(start_date, end_date):
    """Yields a sequence of dates increasing by one from a start date"""
    for i in range(int((end_date - start_date).days)):
        yield start_date + timedelta(days=i)
