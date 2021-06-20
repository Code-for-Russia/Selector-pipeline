import argparse
from typing import Generator, Tuple

from sentence_transformers import SentenceTransformer,  SentencesDataset, LoggingHandler, losses
from sentence_transformers.readers import InputExample
from torch.utils.data import DataLoader
from sentence_transformers.evaluation import BinaryClassificationEvaluator, TripletEvaluator
import logging
from random import choice, shuffle
from sklearn.model_selection import train_test_split

from org.codeforrussia.selector.standardizer.election_layers import ElectionLevel, ElectionType, ElectionLocationType
from org.codeforrussia.selector.standardizer.schemas.schema_registry_factory import \
    StandardProtocolSchemaRegistryFactory

BATCH_SIZE=64
EPOCHS=1
TEST_SIZE=0.25
TRIPLET_MARGIN=0.1


def get_anchor_name(anchor) -> str:
    return anchor["doc"].split(":")[1]


def get_anchor_and_aliases(anchor: dict) -> [str]:
    return [get_anchor_name(anchor)] + anchor["aliases"]

def generate_train_data(anchors) -> Generator[Tuple[str, str, str], None, None]:
    """
    Generates train data as 3-string tuples: (anchor,positive,negative), where anchor - standardized field name, positive - its alias, negative - randomly sample of other standardized name or alias
    :param anchors:
    :return: generator of tuples (anchor,positive,negative)
    """
    for anchor in anchors:
        for alias in anchor["aliases"]:
            random_other_anchor = choice([t for t in anchors if t["doc"] != anchor["doc"]])
            random_negative = choice(get_anchor_and_aliases(random_other_anchor))
            yield (get_anchor_name(anchor), alias, random_negative)

def run():
    parser = argparse.ArgumentParser()

    parser.add_argument('--election-level',
                        dest='election_level',
                        required=True,
                        type=ElectionLevel,
                        help=f'Election level. Supported: {[l.value for l in ElectionLevel]}')

    parser.add_argument('--election-type',
                        dest='election_type',
                        required=True,
                        type=ElectionType,
                        help=f'Election type. Supported: {[l.value for l in ElectionType]}')

    parser.add_argument('--election-location-type',
                        dest='election_location_type',
                        required=False,
                        default=None,
                        type=ElectionLocationType,
                        help=f'Election location type. Supported: {[l.value for l in ElectionLocationType]}')

    parser.add_argument('--output-model-dir',
                        dest='output_model_dir',
                        required=True,
                        type=str,
                        help='Path to save the trained model checkpoints')

    parser.add_argument('--base-model',
                        dest='base_model',
                        required=False,
                        type=str,
                        default="distiluse-base-multilingual-cased-v1",
                        help='Base pre-trained model (by default, Multi-lingual Transformer-based Universal Sentence Encoder), which will be fine-tuned with triplet loss. See https://www.sbert.net/docs/pretrained_models.html')

    args = parser.parse_args()

    schema_registry = StandardProtocolSchemaRegistryFactory.get_schema_registry()
    standard_schema = schema_registry.search_schema(args.election_level, args.election_type, args.election_location_type)
    protocol_fields = [f for f in standard_schema["fields"] if 'doc' in f and f['doc'].startswith("Строка")]
    # Train / val split
    train_anchors, val_anchors = train_test_split(protocol_fields, test_size=TEST_SIZE, random_state=17)
    # Train data
    train_data = list(generate_train_data(train_anchors))
    shuffle(train_data)
    train_examples = [InputExample(texts=list(t)) for t in train_data]
    print(f"Training examples: {len(train_examples)}")
    # Model
    model = SentenceTransformer(args.base_model)
        
    train_dataset = SentencesDataset(train_examples, model)
    train_dataloader = DataLoader(train_dataset, shuffle=True, batch_size=BATCH_SIZE)
    train_loss = losses.TripletLoss(model=model, triplet_margin=TRIPLET_MARGIN)
    # Validation data
    val_data = list(generate_train_data(val_anchors))
    shuffle(val_data)
    positives = [(anchor, positive, 1) for anchor, positive, _ in val_data]
    negatives = [(anchor, negative, 0) for anchor, _, negative in val_data]
    evaluation_set = positives + negatives
    evaluator = BinaryClassificationEvaluator(sentences1=[s1 for s1, _,_ in evaluation_set],
                                              sentences2=[s2 for _, s2,_ in evaluation_set],
                                              labels=[l for _, _, l in evaluation_set],
                                              name="evaluation",
                                              show_progress_bar=True)
    print(f"Validation examples: {len(val_data)}")
    # evaluator = TripletEvaluator(anchors=[a for a, _,_ in val_data],
    #                              positives=[p for _, p,_ in val_data],
    #                              negatives=[n for _, _,n in val_data],
    #                              name="val_triplet_loss",
    #                              show_progress_bar=True)

    model.fit(train_objectives=[(train_dataloader, train_loss)], epochs=EPOCHS, warmup_steps=0, evaluator=evaluator, evaluation_steps=1, show_progress_bar=True, output_path=args.output_model_dir, checkpoint_save_steps=1)




if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()