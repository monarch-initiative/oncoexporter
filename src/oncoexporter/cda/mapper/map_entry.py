



class MapEntry:
    def __init__(self, dictionary):
        if not isinstance(dictionary, dict):
            raise ValueError(f"argument dictionary must be dict but was {type(dictionary)}")
        if not 'id' in dictionary:
            raise ValueError("id not in dictionary")
        if not 'value' in dictionary:
            raise ValueError("value not in dictionary")
        self._id = dictionary.get('id')
        self._value = dictionary.get('value')
        del dictionary['id']
        del dictionary['value']
        self._d = dictionary



    def matches(self, row):
        for k, v in self._d:
            if k not in row or row[k] != v:
                return False
        return True

    def get_id_and_value(self):
        return self._id, self._value
