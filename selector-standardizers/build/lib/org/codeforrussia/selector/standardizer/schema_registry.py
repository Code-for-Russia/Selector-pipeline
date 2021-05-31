import os
from pathlib import Path
import json
from typing import Tuple, Dict, List

from fastavro import parse_schema
from collections import OrderedDict
from org.codeforrussia.selector.standardizer.election_layers import ElectionLevel, ElectionType, ElectionLocationType


class StandardProtocolSchemaRegistry:
    """
    Registry of supported standard schemas of election protocols. They cover different levels, election types (personal vs representatives) and regions.
    Specifically,
    - on FEDERAL level there are two elections: Presidential and State Duma elections;
    - on REGIONAL level there are two: elections of Governors and elections of deputies to regional parliaments
    - on MUNICIPAL level there are four:
        - personal: heads of municipal district and heads of city / rural locations
        - representative: representatives at municipal district level and city / rural location level.

    Additionally, we have a common election schema for common attributes.
    """
    def __init__(self):
        named_schemas = {}

        self._registered_schemas: Dict[Tuple[ElectionLevel, ElectionType, ElectionLocationType], Dict]  = OrderedDict() # dict where key is tuple(level, type, location) and value is schema

        schemas_dir = Path(os.path.dirname(__file__)) / "schemas"

        with open( str(schemas_dir / "common" / "election_1_0.avsc"), "rb") as election_schema_file:
            self._election_schema = parse_schema(json.load(election_schema_file), named_schemas)

        with open(str(schemas_dir / "federal" / "state_duma_1_0.avsc"), "rb") as state_duma_schema_file:
            self._registered_schemas[(ElectionLevel.FEDERAL, ElectionType.REPRESENTATIVE, None)] = parse_schema(json.load(state_duma_schema_file), named_schemas)

    def get_common_election_schema(self):
        """
        Returns election schema with common attributes for protocols of different kinds
        :return:
        """
        return self._election_schema

    def get_all_registered_schema_keys(self) -> List[Tuple[ElectionLevel, ElectionType, ElectionLocationType]]:
        return list(self._registered_schemas.keys())

    def search_schema(self, level: ElectionLevel, type: ElectionType, location: ElectionLocationType = None):
        """
        Searches the standardized schema by criteria
        :param level:
        :param type:
        :param location:
        :return:
        """
        try:
            return self._registered_schemas[(level, type, location)]
        except KeyError:
            raise NotImplementedError(f"This combination of election level = '{level}', type = '{type}', location = '{location}' is not supported yet")