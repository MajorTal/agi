from datasets import load_dataset_builder, load_dataset


def process_datum(idx, question, passage, label):
        print(passage)
        title, passage = passage.split(" -- ")
        print(title)
        print(passage)
        exit()



def main():
    train_dataset = load_dataset("super_glue", "boolq", split="train")
    for datum in train_dataset:
        process_datum(**datum)


if __name__ == "__main__":
    main()
