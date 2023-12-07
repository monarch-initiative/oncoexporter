import os

from .op_mapper import OpMapper
from .map_entry import MapEntry
from typing import Optional
import pandas as pd
import phenopackets as PPkt

class OpDiagnosisMapper(OpMapper):

    def __init__(self):
        super().__init__()
        data_file_name = "neoplasm_types.tsv"
        parent_dir = os.path.dirname(os.path.abspath(__file__))
        fname = os.path.join(parent_dir, data_file_name)
        if not os.path.isfile(fname):
            raise ValueError(f"Could not find necessary input file {fname}")
        self._map_entries = []
        with open(fname, 'rt') as f:
            header = next(f)
            header_fields = header.strip().split("\t")
            if len(header_fields) != 5:
                raise ValueError(f"Expect 5 header fields but got {len(header_fields)}")
            for line in f:
                fields = line.strip().split("\t")
                if len(fields) != len(header_fields):
                    print(f"malformed line with {len(fields)} fields: {line}")
                    continue
                d = {}
                for i in range(len(header_fields)) :
                    d[header_fields[i]] = fields[i]
                me = MapEntry(dictionary = d)
                self._map_entries.append(me)
        # TODO also import stages
        # Todo consider

    def get_ontology_term(self, row:pd.Series) -> Optional[PPkt.OntologyClass]:
        for me in self._map_entries:
            if me.matches(row):
                id, label = me.get_id_and_label()
                oclass = PPkt.OntologyClass()
                oclass.id = id
                oclass.label = label
                return oclass
        return None


