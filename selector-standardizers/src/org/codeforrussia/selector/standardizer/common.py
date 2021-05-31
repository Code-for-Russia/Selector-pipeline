from abc import ABC, abstractmethod
from typing import Optional, Tuple, List, Dict

from org.codeforrussia.selector.standardizer.election_layers import ElectionLevel, ElectionLocationType, ElectionType
from org.codeforrussia.selector.standardizer.schemas.schema_registry_factory import StandardProtocolSchemaRegistryFactory


class Standardizer(ABC):
    PROTOCOL_FIELD_PATTERN = "Строка"

    def __init__(self, schema_registry_factory: StandardProtocolSchemaRegistryFactory):
        self.schema_registry = schema_registry_factory.get_schema_registry()
        self.commission_levels = [f for f in self.schema_registry.get_common_election_schema()["fields"] if f["name"] == "commission_level"][0]["type"]["symbols"]

    def detect_election_attributes_by_name(self, election_name) -> Tuple[ElectionLevel, ElectionType, ElectionLocationType]:
        # TODO: add more accurate recognition; support all combinations
        if "депутатов государственной думы" in election_name.lower():
            return (ElectionLevel.FEDERAL, ElectionType.REPRESENTATIVE, None)
        else:
            raise NotImplementedError(f"Cannot recognize election attributes by this election name: {election_name}")

    def detect_commission_level(self, election_location: [str]) -> str:
        """
        Given election location, recognizes the commission level according to the levels defined in the common schema
        :param election_location: election location
        :return:
        """
        loc_number = len(election_location)
        if loc_number > 0 and loc_number < len(self.commission_levels):
            return self.commission_levels[loc_number]
        else:
            raise ValueError(f"Election location contains wrong number of elements; must be within [1, {len(self.commission_levels) - 1}] got {loc_number}")

    def get_protocol_fields(self, schema) -> [str]:
        """
        Gets protocol fields for a given schema
        :param schema:
        :return:
        """
        return [f['name'] for f in schema['fields'] if 'doc' in f and f['doc'].startswith(self.PROTOCOL_FIELD_PATTERN)]

    def convert_batch(self, batch: List[Dict]) -> List[Optional[Dict]]:
        def tuple_to_dict(output: Optional[Tuple[Dict, ElectionLevel, ElectionType, ElectionLocationType]]) -> Optional[Dict]:
            if output is not None:
                sdata, election_level, election_type, election_location = output
                return {
                    "sdata": sdata,
                    "election_attrs": {"level": election_level, "type": election_type, "location": election_location}
                        }
            else:
                return None

        return [tuple_to_dict(self.convert(protocol_data)) for protocol_data in batch]



    @abstractmethod
    def convert(self, protocol_data: dict) -> Optional[Tuple[dict, ElectionLevel, ElectionType, ElectionLocationType]]:
        pass

