import abc
import platform
import os

import pandas as pd


class CdaFactory(metaclass=abc.ABCMeta):
    """Superclass for the CDA Factory Classes

    Each subclass must implement the to_ga4gh method, which transforms a row of a table from CDA to a GA4GH Message.
    """

    @abc.abstractmethod
    def to_ga4gh(self, row:pd.Series):
        """Return a message from the GA4GH Phenopacket Schema that corresponds to this row.

        :param row: A row from the CDA
        :type row: pd.Series
        :returns: a message from the GA4GH Phenopacket Schema
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
    
    def days_to_iso(days: int):
        """
        Convert the number of days of life into an ISO 8601 period representing the age of an individual
        (e.g., P42Y7M is 42 years and 7 months).

        :param days: number of days of life (str or int)
        """
        if isinstance(days, str):
            days = int(str)
        if not isinstance(days, int):
            raise ValueError(f"days argument must be int or str but was {type(days)}")
        
        # pandas does this conversion automatically: https://pandas.pydata.org/docs/reference/api/pandas.Timedelta.isoformat.html
        td = pd.Timedelta(days=days)
        iso = td.isoformat() # returns ISO 8601 duration string: td = pd.Timedelta(days=10350); td.isoformat(); 'P10350DT0H0M0S'
        return iso

    def get_local_share_directory(self, local_dir=None):
        my_platform = platform.platform()
        my_system = platform.system()
        if local_dir is None:
            local_dir = os.path.join(os.path.expanduser('~'), ".oncoexporter")
        if not os.path.exists(local_dir):
            os.makedirs(local_dir)
            print(f"[INFO] Created new directory for oncoexporter at {local_dir}")
        return local_dir


