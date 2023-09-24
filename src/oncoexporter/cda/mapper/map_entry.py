



class MapEntry:
    def __init__(self, dictionary):
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
        for k, v in self._d:
            if k not in row or row[k] != v:
                return False
        return True

    def get_id_and_label(self):
        return self._id, self._label
