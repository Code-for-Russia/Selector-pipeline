import argparse
from typing import Generator, Tuple

from sentence_transformers import SentenceTransformer,  SentencesDataset, losses, models
from sentence_transformers.readers import InputExample
from torch.utils.data import DataLoader
from sentence_transformers.evaluation import BinaryClassificationEvaluator, TripletEvaluator
import logging
from random import choice, shuffle
import random

from org.codeforrussia.selector.standardizer.election_layers import ElectionLevel, ElectionType, ElectionLocationType
from org.codeforrussia.selector.standardizer.schemas.schema_registry_factory import \
    StandardProtocolSchemaRegistryFactory
import pandas as pd

BATCH_SIZE=128
EPOCHS=3
NEGATIVE_RANDOM_SAMPLES = 5
# One schema is for train, another is for validation
# TODO: add cross-validation
TRAIN_SCHEMA = (ElectionLevel.MUNICIPAL, ElectionType.REPRESENTATIVE, ElectionLocationType.CITY_RURAL)
VAL_SCHEMA = (ElectionLevel.REGIONAL, ElectionType.PERSONAL, None)

random.seed(17)

def get_anchor_name(anchor) -> str:
    return anchor["doc"].split(":")[1].strip()


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
            for _ in range(NEGATIVE_RANDOM_SAMPLES):
                random_other_anchor = choice([t for t in anchors if t["doc"] != anchor["doc"]])
                random_negative = choice(get_anchor_and_aliases(random_other_anchor))
                yield (get_anchor_name(anchor), alias, random_negative)

def run():
    parser = argparse.ArgumentParser()

    parser.add_argument('--output-model-dir',
                        dest='output_model_dir',
                        required=True,
                        type=str,
                        help='Path to save the trained model checkpoints')

    parser.add_argument('--base-model',
                        dest='base_model',
                        required=False,
                        type=str,
                        default="DeepPavlov/rubert-base-cased-sentence",
                        help='Base pre-trained model (by default, sentence encoder based on DeepPavlov RuBERT), which will be fine-tuned with triplet loss. See https://www.sbert.net/docs/pretrained_models.html')

    parser.add_argument('--triple-margin',
                        dest='triple_margin',
                        required=False,
                        default=1,
                        type=float,
                        help='Margin in triplet loss')

    args = parser.parse_args()

    schema_registry = StandardProtocolSchemaRegistryFactory.get_schema_registry()
    train_schema = schema_registry.search_schema(*TRAIN_SCHEMA)
    train_anchors = [f for f in train_schema["fields"] if 'doc' in f and f['doc'].startswith("Строка")]
    # Train data
    train_data = list(generate_train_data(train_anchors))
    pd.DataFrame(train_data).to_csv("/tmp/train.csv")
    shuffle(train_data)
    train_examples = [InputExample(texts=list(t)) for t in train_data]
    print(f"Training examples: {len(train_examples)}")
    # Model
    base_model = models.Transformer(args.base_model)
    pooling_model = models.Pooling(base_model.get_word_embedding_dimension())
    model = SentenceTransformer(modules=[base_model, pooling_model])
    
        
    train_dataset = SentencesDataset(train_examples, model)
    train_dataloader = DataLoader(train_dataset, shuffle=True, batch_size=BATCH_SIZE)
    train_loss = losses.TripletLoss(model=model, triplet_margin=args.triple_margin)
    # Validation data:
    val_schema = schema_registry.search_schema(*VAL_SCHEMA)
    val_anchors = [f for f in val_schema["fields"] if 'doc' in f and f['doc'].startswith("Строка")]
    val_data = list(generate_train_data(val_anchors))
    
    positives = [(anchor, positive, 1) for anchor, positive, _ in val_data]
    negatives = [(anchor, negative, 0) for anchor, _, negative in val_data]
    evaluation_set = positives + negatives
    print(print(f"Validation examples: {len(evaluation_set)}"))
    evaluator = BinaryClassificationEvaluator(sentences1=[s1 for s1, _,_ in evaluation_set],
                                              sentences2=[s2 for _, s2,_ in evaluation_set],
                                              labels=[l for _, _, l in evaluation_set],
                                              name="evaluation",
                                              show_progress_bar=True)

    model.fit(train_objectives=[(train_dataloader, train_loss)], epochs=EPOCHS, warmup_steps=0, evaluator=evaluator, evaluation_steps=1, show_progress_bar=True, output_path=args.output_model_dir, checkpoint_save_steps=1)


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()