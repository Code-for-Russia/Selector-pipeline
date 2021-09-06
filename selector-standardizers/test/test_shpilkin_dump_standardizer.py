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
    municipal_deputy_city_data = []

    @classmethod
    def setUpClass(cls):
        cls.state_duma_data = read_protocol_data_from_file("state_duma_1_0_example.jsonl")
        cls.regional_head_data = list(read_protocol_data_from_file("regional_head_1_0_example.jsonl"))
        cls.municipal_deputy_city_data = read_protocol_data_from_file("municipal_deputy_city_1_0_example.jsonl")
        cls.regional_deputy_data = read_protocol_data_from_file("regional_deputy_1_0_example.jsonl")
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
        row_number = 100
        actual = TestShpilkinDumpStandardizer.standardizer.convert_batch(list(TestShpilkinDumpStandardizer.regional_head_data)[:row_number])

        self.assertEqual(row_number, len(actual), "Expected length does not match")
        self.assertEqual("AREA", actual[0]["sdata"]["election"]["commission_level"])
        self.assertEqual(0, actual[0]["sdata"]["unaccounted"])
        self.assertEqual(10, actual[0]["sdata"]["issued_to_mobile"])
        self.assertEqual(79, actual[0]["sdata"]["issued_ahead"])

    def test_on_smolensk_regional_heads(self):
        actual = TestShpilkinDumpStandardizer.standardizer.convert_batch([d for d in TestShpilkinDumpStandardizer.regional_head_data if d["loc"][0] == "Выборы Губернатора Смоленской области"][:10])
        self.assertEqual(10, len(actual), "Expected length does not match")
        self.assertEqual(216, actual[0]["sdata"]["voters"], "Number of voters must be equal to expected")
        for a in actual:
            self.assertGreater(a["sdata"]["voters"], 0, "Number of voters must be greater than 0")

    def test_on_kamchatka_regional_heads(self):
        actual = TestShpilkinDumpStandardizer.standardizer.convert_batch([d for d in TestShpilkinDumpStandardizer.regional_head_data if d["loc"][0] == "Досрочные выборы Губернатора Камчатского края"][:10])
        self.assertEqual(10, len(actual), "Expected length does not match")
        print(actual[0])
        self.assertEqual(192, actual[0]["sdata"]["issued_to_commission"], "Number of voters must be equal to expected")
        for a in actual:
            self.assertGreater(a["sdata"]["issued_to_commission"], 0, "Number of voters must be greater than 0")

    def test_on_municipal_deputy_city(self):
        row_number = 100
        actual = TestShpilkinDumpStandardizer.standardizer.convert_batch(list(TestShpilkinDumpStandardizer.municipal_deputy_city_data)[:row_number])
        
        self.assertEqual(row_number, len(actual), "Expected length does not match")
        self.assertEqual("TERRITORY", actual[0]["sdata"]["election"]["commission_level"])
        self.assertEqual(0, actual[0]["sdata"]["issued_absentee_certificates_to_territorial"])
        self.assertEqual(1473, actual[0]["sdata"]["issued_to_commission"])
        self.assertEqual(1713, actual[0]["sdata"]["issued_ahead"])

    def test_on_regional_deputy(self):
        actual = TestShpilkinDumpStandardizer.standardizer.convert_batch(list(TestShpilkinDumpStandardizer.regional_deputy_data))

        self.assertEqual(20, len(actual), "Expected length does not match")
        self.assertEqual("AREA", actual[0]["sdata"]["election"]["commission_level"])
        self.assertEqual(256, actual[0]["sdata"]["issued_to_commission"])
        self.assertEqual(4, actual[0]["sdata"]["issued_to_mobile"])
        self.assertEqual(281, actual[0]["sdata"]["in_mobile"])

        self.assertEqual("AREA", actual[19]["sdata"]["election"]["commission_level"])
        self.assertEqual(565, actual[19]["sdata"]["voters"])
        self.assertEqual(7, actual[19]["sdata"]["invalid"])
        self.assertEqual(550, actual[19]["sdata"]["received_by_commission"])
