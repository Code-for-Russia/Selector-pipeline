from typing import Optional, Tuple
from logging import Logger

from org.codeforrussia.selector.config.global_config import GlobalConfig
from org.codeforrussia.selector.standardizer.common import Standardizer
from org.codeforrussia.selector.standardizer.election_layers import ElectionLevel, ElectionType, ElectionLocationType
from org.codeforrussia.selector.standardizer.recognizers.protocol_field_recognizer_registry_factory import \
    ProtocolFieldRecognizerRegistryFactory
from org.codeforrussia.selector.standardizer.recognizers.protocol_field_recognizers import ProtocolRow
from org.codeforrussia.selector.standardizer.schemas.schema_registry_factory import \
    StandardProtocolSchemaRegistryFactory


class ShpilkinDumpStandardizer(Standardizer):
    logger = Logger("ShpilkinDumpStandardizer")

    def __init__(self, schema_registry_factory: StandardProtocolSchemaRegistryFactory,
                 protocol_recognizer_registry_factory: ProtocolFieldRecognizerRegistryFactory,
                 global_config: GlobalConfig,
                 ):
        super().__init__(schema_registry_factory, protocol_recognizer_registry_factory, global_config)

    def convert(self, protocol_data: dict) -> Optional[Tuple[dict, ElectionLevel, ElectionType, ElectionLocationType]]:
        """
        Accepts single-protocol data in Shpilkin's format.
        First, it recognizes the election attributes by election name.
        :param protocol_data: data
        :return: standardized data
        """
        if protocol_data["loc"]:
            election_name = protocol_data["loc"][0]
            election_level, election_type, election_location_type = self.detect_election_attributes_by_name(election_name)

            election_location = protocol_data["loc"][1:]
            election_commission_level = self.detect_commission_level(election_location)
            election_date = "21.09.2020"  # must be included, but no provided in dump; TODO: extract from filename

            sdata = {
                "election": {
                    "name": election_name,
                    "location": election_location,
                    "commission_level": election_commission_level,
                    "date": election_date
                }
            }

            protocol_rows = [ProtocolRow(line_number=d["line_num"],
                             line_name=d["line_name"],
                             line_value=int(d["line_val"])) for d in protocol_data['data']]

            recognized_schema = self.schema_registry.search_schema(election_level, election_type, election_location_type)
            standardized_protocol_rows = self.protocol_recognizer_registry.get_recognizer(election_level).recognize(protocol_rows, recognized_schema)
            sdata = dict(sdata, **standardized_protocol_rows)

            return sdata, election_level, election_type, election_location_type
        else:
            self.logger.warning("Protocol data is likely malformed. Empty result will be returned for this protocol data.")
            return None
