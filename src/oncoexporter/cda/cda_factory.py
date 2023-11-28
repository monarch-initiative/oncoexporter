import abc
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

