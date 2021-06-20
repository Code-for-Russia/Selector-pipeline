import unittest

from org.codeforrussia.selector.config.global_config import GlobalConfig
from org.codeforrussia.selector.standardizer.custom.shpilkin_format import ShpilkinDumpStandardizer
from org.codeforrussia.selector.standardizer.recognizers.protocol_field_recognizer_registry_factory import \
    ProtocolFieldRecognizerRegistryFactory
from org.codeforrussia.selector.standardizer.schemas.schema_registry_factory import StandardProtocolSchemaRegistryFactory
import jsonlines
from pathlib import Path

def read_protocol_data_from_file(filename: str):
    with jsonlines.open(Path(__file__).parent / "resources" / "shpilkin" / filename) as reader:
        for protocol in reader:
            yield protocol

class TestShpilkinDumpStandardizer(unittest.TestCase):
    state_duma_data = []
    regional_head_data  = []

    @classmethod
    def setUpClass(cls):
        cls.state_duma_data = read_protocol_data_from_file("state_duma_1_0_example.jsonl")
        cls.regional_head_data = read_protocol_data_from_file("regional_head_1_0_example.jsonl")
        global_config = GlobalConfig(
            gcs_bucket="codeforrussia-selector",
            ml_models_gcs_prefix="ml-models",
        )
        cls.standardizer = ShpilkinDumpStandardizer(
            schema_registry_factory=StandardProtocolSchemaRegistryFactory,
            protocol_recognizer_registry_factory=ProtocolFieldRecognizerRegistryFactory,
            global_config=global_config,
        )

    def test_on_state_duma(self):
        actual = TestShpilkinDumpStandardizer.standardizer.convert_batch(list(TestShpilkinDumpStandardizer.state_duma_data))
        self.assertEqual(2, len(actual), "Expected length does not match")
        self.assertEqual("TERRITORY", actual[0]["sdata"]["election"]["commission_level"])
        self.assertEqual(18476, actual[0]["sdata"]["valid"])
        self.assertEqual(1183, actual[1]["sdata"]["canceled"])

    def test_on_regional_heads(self):
        actual = TestShpilkinDumpStandardizer.standardizer.convert_batch(list(TestShpilkinDumpStandardizer.regional_head_data)[:10])

        self.assertEqual(10, len(actual), "Expected length does not match")
        self.assertEqual("AREA", actual[0]["sdata"]["election"]["commission_level"])
        self.assertEqual(0, actual[0]["sdata"]["unaccounted"])
        self.assertEqual(10, actual[0]["sdata"]["issued_to_mobile"])
        self.assertEqual(79, actual[0]["sdata"]["issued_ahead"])
