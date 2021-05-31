from typing import Optional
from logging import Logger

from org.codeforrussia.selector.standardizer.common import Standardizer
from org.codeforrussia.selector.standardizer.schemas.schema_registry_factory import \
    StandardProtocolSchemaRegistryFactory


class ShpilkinDumpStandardizer(Standardizer):
    logger = Logger("ShpilkinDumpStandardizer")

    def __init__(self, schema_registry_factory: StandardProtocolSchemaRegistryFactory):
        super().__init__(schema_registry_factory)

    def convert(self, protocol_data: dict) -> Optional[dict]:
        """
        Accepts single-protocol data in Shpilkin's format.
        First, it recognizes the election attributes by election name.
        :param protocol_data: data
        :return: standardized data
        """
        if protocol_data["loc"]:
            election_name = protocol_data["loc"][0]
            election_level, election_type, election_location_type = self.detect_election_attributes_by_name(election_name)
            recognized_schema = self.schema_registry.search_schema(election_level, election_type, election_location_type)
            protocol_fields = self.get_protocol_fields(recognized_schema)

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
            for d in protocol_data['data']:
                if "line_num" in d and "line_val" in d:
                    line_number = int(d["line_num"])
                    line_value = int(d["line_val"])
                    if line_number > 0 and line_number < len(protocol_fields) + 1:
                        sdata[protocol_fields[line_number - 1]] = line_value

            return sdata, election_level, election_type, election_location_type
        else:
            self.logger.warning("Protocol data is likely malformed. Empty result will be returned for this protocol data.")
            return None
