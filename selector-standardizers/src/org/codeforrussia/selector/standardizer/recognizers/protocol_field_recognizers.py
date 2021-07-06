from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List, Dict, Union
from sentence_transformers import SentenceTransformer, util
import numpy as np
import logging

from torch import Tensor

from org.codeforrussia.selector.config.global_config import GlobalConfig
from org.codeforrussia.selector.utils.gcs import GCS
from org.codeforrussia.selector.utils.file import unzip

@dataclass
class ProtocolRow:
    """Represents a single row in a protocol"""
    # line number, usually integer between 1 and 12, but there can be alphanumeric value, such as "2b"
    line_number: str
    # Protocol data numbers or candidate names
    line_name: str
    # Protocol vote counts
    line_value: int
    

class ProtocolFieldRecognizer(ABC):
    PROTOCOL_FIELD_PATTERN = "Строка"

    def get_protocol_fields(self, schema) -> [str]:
        """
        Gets protocol fields for a given schema
        :param schema:
        :return:
        """
        return [f['name'] for f in schema['fields'] if 'doc' in f and f['doc'].startswith(self.PROTOCOL_FIELD_PATTERN)]

    @abstractmethod
    def recognize(self, protocol_data: List[ProtocolRow], schema: Dict) -> Dict:
        """
        Recognizes standard protocol fields in protocol rows w.r.t. standard schema
        :param protocol_data: protocol rows
        :param schema: recognized standard schema
        :return:
        """
        pass

class LineNumberBasedProtocolRecognizer(ProtocolFieldRecognizer):
    """
    Simplified recognizer that relies on line numbers. For example, federal-level election protocols are well-defined by the federal laws, no smart recognition is needed
    """
    def recognize(self, protocol_data: List[ProtocolRow], schema: Dict) -> Dict:
        standard_protocol_fields = self.get_protocol_fields(schema)
        standardized_protocol_data = {}
        for row in protocol_data:
            if row.line_name and row.line_value:
                line_number = int(row.line_number) # line number is necessarily integer
                if line_number > 0 and line_number < len(standard_protocol_fields) + 1:
                    standardized_protocol_data[standard_protocol_fields[line_number - 1]] = row.line_value
        return standardized_protocol_data

class SimilarityBasedProtocolRecognizer(ProtocolFieldRecognizer):
    """
    Recognizes protocol fields based on name similarity w.r.t. standard schema fields. There are regional electoral laws, defining the standard of protocol fields. To avoid manual work of collecting all regional  laws, we introduce a universal protocol field schema for all regions and take advantage of ML-based NLP model for recognition.

    The core ML model is loaded lazily.
    """
    def __init__(self, global_config: GlobalConfig, model_name: str):
        self.MODEL_THRESHOLD = 0.83
        self._global_config = global_config
        self._model_name = model_name

    @property
    @lru_cache()
    def model(self):
        model_file_name = f"{self._model_name}.zip"
        with TemporaryDirectory() as output_local_dir:
            output_local_filename = str(Path(output_local_dir) / model_file_name)
            logging.debug(f"Loading model='{model_file_name}' from GCS...")
            GCS().download_file(
                bucket_name=self._global_config.gcs_bucket,
                filename=str(Path(self._global_config.ml_models_gcs_prefix) / model_file_name),
                output_local_filename=output_local_filename,
            )
            logging.debug("Model downloaded")
            logging.debug("Model unzipping...")
            unzip(output_local_filename, output_local_dir)
            return SentenceTransformer(str(Path(output_local_dir) / self._model_name))

    def listToTuple(function):
        def wrapper(*args):
            args = [tuple(x) if type(x) == list else x for x in args]
            result = function(*args)
            result = tuple(result) if type(result) == list else result
            return result
        return wrapper

    @listToTuple
    @lru_cache(maxsize=200)
    def encode_sentences(self, sentences: List[str]) -> Union[List[Tensor], np.ndarray, Tensor]:
        return self.model.encode(sentences, convert_to_tensor=True)
        
    def recognize(self, protocol_data: List[ProtocolRow], schema: Dict) -> Dict:
        standard_protocol_fields = [f for f in schema['fields'] if 'doc' in f and f['doc'].startswith(self.PROTOCOL_FIELD_PATTERN)]
        standard_protocol_aliases = {a: f for f in standard_protocol_fields for a in f['aliases']}
        for f in standard_protocol_fields:
            standard_protocol_aliases[f['doc'].split(':')[1].strip()] = f

        standardized_field_names = [*standard_protocol_aliases]

        standardized_field_embeddings = self.encode_sentences(standardized_field_names)

        protocol_fields = [f.line_name for f in protocol_data]
        protocol_field_embeddings = self.encode_sentences(protocol_fields)
        cosine_scores = util.pytorch_cos_sim(protocol_field_embeddings, standardized_field_embeddings)

        standardized_protocol_data = {}
        max_score_indices = set()
        for i in range(len(protocol_fields)):
            max_score_index = np.argmax(cosine_scores[i]).item()

            max_similarity_score = cosine_scores[i][max_score_index]
            if max_similarity_score > self.MODEL_THRESHOLD:
                standard_field_id = standard_protocol_aliases[standardized_field_names[max_score_index]]['name']
                assert max_score_index not in max_score_indices, f"Model gives an invalid repetitive prediction: '{standard_field_id}' duplicate on {protocol_fields[i]} with score={max_similarity_score}"
                max_score_indices.add(max_score_index)
            
                if max_similarity_score < 1: # log the stats of non-exact matches
                    logging.debug("{}\t{} ({})\t{:.4f}".format(
                        protocol_fields[i],
                        standardized_field_names[max_score_index],
                        standard_field_id,
                        max_similarity_score))
                    
                standardized_protocol_data[standard_field_id] = protocol_data[i].line_value
            else:
                logging.debug(f"Could not recognize this protocol field: {protocol_fields[i]}. Score {max_similarity_score} below threshold = {self.MODEL_THRESHOLD}")

        return standardized_protocol_data