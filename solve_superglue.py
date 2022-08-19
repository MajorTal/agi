from datasets import load_dataset_builder, load_dataset
from evaluate import load as evaluate_load


def process_datum(idx, question, passage, label):
        print(passage)
        passage_split = passage.split(" -- ")
        title = passage_split[0]
        passage = " -- ".join(passage_split[1:])
        # print(title)
        # print(passage)
        prediction = 1
        return prediction, label



def main():
    super_glue_metric_boolq = evaluate_load('super_glue', 'boolq') 
    train_dataset = load_dataset("super_glue", "boolq", split="train")
    predictions = []
    references = []

    for datum in train_dataset:
        prediction, reference = process_datum(**datum)
        predictions.append(prediction)
        references.append(reference)

    results = super_glue_metric_boolq.compute(predictions=predictions, references=references)

    print(results)


if __name__ == "__main__":
    main()


