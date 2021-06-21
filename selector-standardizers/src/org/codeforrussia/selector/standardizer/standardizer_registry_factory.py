from typing import Dict

from org.codeforrussia.selector.config.global_config import GlobalConfig
from org.codeforrussia.selector.standardizer.common import Standardizer
from org.codeforrussia.selector.standardizer.custom.shpilkin_format import ShpilkinDumpStandardizer
from org.codeforrussia.selector.standardizer.recognizers.protocol_field_recognizer_registry_factory import \
    ProtocolFieldRecognizerRegistryFactory
from org.codeforrussia.selector.standardizer.schemas.schema_registry_factory import \
    StandardProtocolSchemaRegistryFactory

from enum import Enum

class SupportedInputFormat(Enum):
    SHPILKIN_DUMP  = "SHPILKIN"
    # TODO: add other custom formats of scraped election data

    def __str__(self):
        return self.value


class StandardizerRegistryFactory(object):

    def get_standardizer_registry(
            schema_registry_factory: StandardProtocolSchemaRegistryFactory,
            protocol_recognizer_registry_factory: ProtocolFieldRecognizerRegistryFactory,
            global_config: GlobalConfig,
    ):

        class StandardizerRegistry:
            """
            Registry of supported input data formats and their respective standardizers.
            """
            def __init__(self,
                         schema_registry_factory: StandardProtocolSchemaRegistryFactory,
                         protocol_recognizer_registry_factory: ProtocolFieldRecognizerRegistryFactory,
                         global_config: GlobalConfig,
                         ):
                self.standardizers: Dict[SupportedInputFormat, Standardizer] = {
                        SupportedInputFormat.SHPILKIN_DUMP : ShpilkinDumpStandardizer(
                            schema_registry_factory=schema_registry_factory,
                            protocol_recognizer_registry_factory=protocol_recognizer_registry_factory,
                            global_config=global_config,
                            )
                }

            def get_standardizer(self, data_format: SupportedInputFormat) -> Standardizer:
                try:
                    return self.standardizers[data_format]
                except KeyError:
                    raise NotImplementedError(f"This input data format is not supported yet: {data_format}")

        return StandardizerRegistry(schema_registry_factory,
                                    protocol_recognizer_registry_factory,
                                    global_config=GlobalConfig( # Copy global config to trigger post_init and setting environment variable
                                        gcs_bucket=global_config.gcs_bucket,
                                        ml_models_gcs_prefix=global_config.ml_models_gcs_prefix,
                                        gcs_credentials=global_config.gcs_credentials))

    get_standardizer_registry = staticmethod(get_standardizer_registry)