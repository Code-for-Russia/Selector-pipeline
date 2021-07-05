from abc import ABC, abstractmethod
from typing import Optional, Tuple, List, Dict

from org.codeforrussia.selector.config.global_config import GlobalConfig
from org.codeforrussia.selector.standardizer.recognizers.election_attribute_recognizer import ElectionAttributeRecognizer
from org.codeforrussia.selector.standardizer.election_layers import ElectionLevel, ElectionLocationType, ElectionType
from org.codeforrussia.selector.standardizer.recognizers.protocol_field_recognizer_registry_factory import \
    ProtocolFieldRecognizerRegistryFactory
from org.codeforrussia.selector.standardizer.schemas.schema_registry_factory import StandardProtocolSchemaRegistryFactory

class Standardizer(ABC):

    def __init__(self,
                 schema_registry_factory: StandardProtocolSchemaRegistryFactory,
                 protocol_recognizer_registry_factory: ProtocolFieldRecognizerRegistryFactory,
                 global_config: GlobalConfig,
                 ):
        self.schema_registry = schema_registry_factory.get_schema_registry()
        self.protocol_recognizer_registry = protocol_recognizer_registry_factory.get_registry(global_config=global_config)
        self.election_attribute_recognizer = ElectionAttributeRecognizer()
        self.commission_levels = [f for f in self.schema_registry.get_common_election_schema()["fields"] if f["name"] == "commission_level"][0]["type"]["symbols"]

    def detect_election_attributes_by_name(self, election_name) -> Tuple[ElectionLevel, ElectionType, ElectionLocationType]:
        return self.election_attribute_recognizer.recognize(election_name)

    def detect_commission_level(self, election_location: [str]) -> str:
        """
        Given election location, recognizes the commission level according to the levels defined in the common schema
        :param election_location: election location
        :return:
        """
        if "УИК " in election_location[-1]:
            return self.commission_levels[-1]
        elif any(x in election_location[-1] for x in ["ТИК", "округ"]):
            return self.commission_levels[-2]
        elif "ОИК" in election_location[-1]:
            return self.commission_levels[-3]
        else: # Fallback is territorial
            return self.commission_levels[-2]

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

