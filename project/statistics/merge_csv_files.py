import csv
import pathlib
from random import shuffle

from tqdm import tqdm

TEST_DATA_PERCENTAGE = 5


def main():
    merge()


def merge():
    csv_files_dir = pathlib.Path(__file__).parent.absolute() / "output"

    csv_files = []
    for file_obj in csv_files_dir.glob("*.csv"):
        if file_obj.name.startswith("combined"):
            continue

        csv_files.append(file_obj)

    merge_files_into_one(csv_files, csv_files_dir)


def merge_files_into_one(files, csv_files_dir):
    data = []
    for file_obj in tqdm(files):
        with file_obj.open(mode="r") as f:
            reader = csv.DictReader(f)
            results = list(reader)
            for row in results:
                data.append(row)

    header = data[0].keys()

    # important to randomize data and exclude header from csv
    shuffle(data[1:])

    test_samples_count = int((TEST_DATA_PERCENTAGE * len(data)) / 100)
    test_samples = data[0:test_samples_count]
    train_samples = data[test_samples_count:]

    print(f"Total samples {len(data)}")
    print(f"Train samples {len(train_samples)}")
    print(f"Test samples {len(test_samples)}")

    file_name = csv_files_dir / "combined_train.csv"
    with open(file_name, "w") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=header)
        for data in train_samples:
            writer.writerow(data)

    file_name = csv_files_dir / "combined_test.csv"
    with open(file_name, "w") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=header)
        for data in test_samples:
            writer.writerow(data)


if __name__ == "__main__":
    main()
