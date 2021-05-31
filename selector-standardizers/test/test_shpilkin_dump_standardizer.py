import unittest
from org.codeforrussia.selector.standardizer.custom.shpilkin import ShpilkinDumpStandardizer
from org.codeforrussia.selector.standardizer.schemas.schema_registry_factory import StandardProtocolSchemaRegistryFactory
import jsonlines
from pathlib import Path

class TextShpilkinDumpStandardizer(unittest.TestCase):
    test_protocol_data = []

    @classmethod
    def setUpClass(cls):
        with jsonlines.open(Path(__file__).parent / "resources" / "shpilkin" / "state_duma_1_0_example.jsonl") as reader:
            for protocol in reader:
                cls.test_protocol_data.append(protocol)

    def test_on_dump(self):
        standardizer = ShpilkinDumpStandardizer(schema_registry_factory=StandardProtocolSchemaRegistryFactory)
        actual = standardizer.convert_batch(TextShpilkinDumpStandardizer.test_protocol_data)
        self.assertEqual(2, len(actual), "Expected length does not match")
        self.assertEqual("TERRITORY", actual[0]["sdata"]["election"]["commission_level"])
        self.assertEqual(18476, actual[0]["sdata"]["valid"])
        self.assertEqual(1183, actual[1]["sdata"]["canceled"])