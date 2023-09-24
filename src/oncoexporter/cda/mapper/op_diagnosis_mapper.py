import os

from .op_mapper import OpMapper
from .map_entry import MapEntry
from typing import Optional
import phenopackets as PPkt

class OpDiagnosisMapper(OpMapper):

    def __init__(self):
        super.__init__()
        data_file_name = "neoplasm_types.tsv"
        if not os.path.isfile(data_file_name):
            raise ValueError(f"Could not find necessary input file {data_file_name}")
        self._map_entries = []
        with open(data_file_name, 'rt') as f:
            header = next(f)
            header_fields = header.strip().split("\t")
            if len(header_fields) != 5:
                raise ValueError(f"Expect 5 header fields but got {len(header_fields)}")
            for line in f:
                fields = line.strip().split("\t")
                d = {}
                for i in range(len(header_fields)) :
                    d[header_fields[i]] = fields[i]
                me = MapEntry(dictionary = d)
                self._map_entries.append(me)

    def get_ontology_term(self, row) -> Optional[PPkt.OntologyClass]:
        for me in self._map_entries:
            if me.matches(row):
                id, label = me.get_id_and_value()
                oclass = PPkt.OntologyClass()
                oclass.id = id
                oclass.label = label
                return oclass
        return None


