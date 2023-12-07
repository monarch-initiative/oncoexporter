import abc
import pandas as pd


class CdaFactory(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def from_cancer_data_aggregator(self, row):
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


