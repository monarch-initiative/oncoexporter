import abc
import os
import platform
import re
import typing

import pandas as pd


int_pattern = re.compile(r'^-?\d+$')


class CdaFactory(metaclass=abc.ABCMeta):
    """Superclass for the CDA Factory Classes

    Each subclass must implement the to_ga4gh method, which transforms a row of a table from CDA to a GA4GH Message.
    """

    @abc.abstractmethod
    def to_ga4gh(self, row: pd.Series):
        """Return a message from the GA4GH Phenopacket Schema that corresponds to this row.

        :param row: A row from the CDA
        :type row: pd.Series
        :returns: a message from the GA4GH Phenopacket Schema
        :raises ValueError: if unable to parse
        """
        pass

    def get_item(self, row, column_name):
        if column_name not in row:
            raise ValueError(f"Expecting to find {column_name} in row but did not. These are the columns: {row.columns}")
        return row[column_name]

    def get_items_from_row(self, row, column_names):
        if not isinstance(column_names, list):
            raise ValueError(f"column_names argument must be a list but was {type(column_names)}")
        results = []
        for name in column_names:
            results.append(self.get_item(row, name))
        return results

    @staticmethod
    def days_to_iso(days: typing.Union[int, str]) -> typing.Optional[str]:
        """
        Convert the number of days of life into an ISO 8601 period representing the age of an individual.

        Note, we only use the `D` designator as transformation to years or months would be lossy.

        The `days` can be negative, leading to the duration of the same length.

        `None` is returned if the input `str` cannot be parsed into an integer.

        :param days: a `str` or `int` with a number of days of life.
        :raises ValueError: if `days` is not an `int` or a `str`.
        """
        if type(days) is int:
            # In Python, `isinstance(True, int) == True`.
            # However, we don't want that here.
            pass
        elif isinstance(days, str):
            if int_pattern.match(days):
                days = int(days)
            else:
                return None
        else:
            raise ValueError(f"days argument must be an int or a str but was {type(days)}")

        return f'P{abs(days)}D'

    def get_local_share_directory(self, local_dir=None):
        my_platform = platform.platform()
        my_system = platform.system()
        if local_dir is None:
            local_dir = os.path.join(os.path.expanduser('~'), ".oncoexporter")
        if not os.path.exists(local_dir):
            os.makedirs(local_dir)
            print(f"[INFO] Created new directory for oncoexporter at {local_dir}")
        return local_dir
