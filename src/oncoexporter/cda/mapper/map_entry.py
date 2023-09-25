



class MapEntry:
    """A class to hold information in one line of a mapping file.
    This class is used to help map combinations of strings (in multiple columns of a CDA table) to one ontology term

    :param _id: identifier of the ontology term to which we map
    :type _id: str
    :param _label: label (name) of the ontology term to which we map
    :type _label: str
    :param _d: dictinary that has the column names (key) and row values of the corresponding map entry
    :type _d: dict
    """
    def __init__(self, dictionary):
        """Initialize a mapping entry from the data in one row of the input TSV file, e.g., neoplasm_types.tsv
        :param dictionary: keys -- the table header of the input TSV file. values : corresponding entires of one row
        """
        if not isinstance(dictionary, dict):
            raise ValueError(f"argument dictionary must be dict but was {type(dictionary)}")
        if not 'id' in dictionary:
            raise ValueError("id not in dictionary")
        if not 'label' in dictionary:
            raise ValueError("label not in dictionary")
        self._id = dictionary.get('id')
        self._label = dictionary.get('label')
        del dictionary['id']
        del dictionary['label']
        self._d = dictionary



    def matches(self, row):
        """
        Check if the input row of a table from CDA matches with the current MapEntry object
        :returns: True if the row matches the entry, otherwise false
        """
        for k, v in self._d.items():
            if k not in row or row[k] != v:
                return False
        return True

    def get_id_and_label(self):
        """
        :returns: id and label of the GA4GH Ontology term that corresponds to the entry,
        """
        return self._id, self._label
