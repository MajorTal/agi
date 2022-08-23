from itertools import islice

import spacy # used for now only for the sentence splitting
from datasets import load_dataset_builder, load_dataset
from evaluate import load as evaluate_load

import is_it_relevant

NLP = spacy.load('en_core_web_trf') # The larger model

SKIP_THESE_BECAUSE_OVERUSED = 30


def sentence_splitter(text):
    doc = NLP(text)
    return [sent for sent in doc.sents]



def process_datum(idx, question, passage, label):
        # print(passage)
        passage_split = passage.split(" -- ")
        topic = passage_split[0]
        passage = " -- ".join(passage_split[1:])
        print(f"\n{question = }")
        sentences = sentence_splitter(passage)
        for sentence in sentences:
            print(f"{sentence = }")
            print(is_it_relevant.predict(question, topic, sentence.text))
        prediction = 1
        return prediction, label


def main():
    super_glue_metric_boolq = evaluate_load('super_glue', 'boolq') 
    dataset_train = load_dataset("super_glue", "boolq", split="train")
    # dataset_validation = load_dataset("super_glue", "boolq", split="validation")
    # dataset_test = load_dataset("super_glue", "boolq", split="test")
    predictions = []
    references = []

    for datum in islice(dataset_train, SKIP_THESE_BECAUSE_OVERUSED, SKIP_THESE_BECAUSE_OVERUSED+10):
        prediction, reference = process_datum(**datum)
        predictions.append(prediction)
        references.append(reference)

    results = super_glue_metric_boolq.compute(predictions=predictions, references=references)

    print(results)


if __name__ == "__main__":
    main()


