from org.codeforrussia.selector.config.global_config import GlobalConfig
from org.codeforrussia.selector.standardizer.election_layers import ElectionLevel
from org.codeforrussia.selector.standardizer.recognizers.protocol_field_recognizers import LineNumberBasedProtocolRecognizer, \
    SimilarityBasedProtocolRecognizer, ProtocolFieldRecognizer


class ProtocolFieldRecognizerRegistryFactory(object):

    def get_registry(global_config: GlobalConfig):
        class ProtocolFieldRecognizerRegistry:
            """
            Registry of supported election levels and their recognizers
            """
            def __init__(self, global_config: GlobalConfig):
                # share the same similarity model
                similarity_based_protocol_recognizer = SimilarityBasedProtocolRecognizer(
                                                            global_config=global_config,                                                                             model_name="similarity-protocol-recognizer_1_3_0",
                )
                self.recognizers = {
                    ElectionLevel.FEDERAL: LineNumberBasedProtocolRecognizer(),
                    ElectionLevel.REGIONAL: similarity_based_protocol_recognizer,
                    ElectionLevel.MUNICIPAL: similarity_based_protocol_recognizer,
                }

            def get_recognizer(self, election_level: ElectionLevel) -> ProtocolFieldRecognizer:
                try:
                    return self.recognizers[election_level]
                except KeyError:
                    raise NotImplementedError(f"This election level is not supported yet: {election_level}")
        return ProtocolFieldRecognizerRegistry(global_config=global_config)

    get_registry = staticmethod(get_registry)