import csv
import pathlib

from tqdm import tqdm


def main():
    merge()


def merge():
    csv_files_dir = pathlib.Path(__file__).parent.absolute() / "output"

    dealer_files = []
    regular_files = []
    for file_obj in csv_files_dir.glob("*.csv"):
        if file_obj.name.startswith("01"):
            continue

        if file_obj.name.startswith("dealer"):
            dealer_files.append(file_obj)
        else:
            regular_files.append(file_obj)

    merge_files_into_one(dealer_files, csv_files_dir / "01_dealer_total.csv")
    merge_files_into_one(regular_files, csv_files_dir / "01_total.csv")


def merge_files_into_one(files, file_path):
    data = []
    for file_obj in tqdm(files, desc=file_path.name):
        with file_obj.open(mode="r") as f:
            reader = csv.DictReader(f)
            results = list(reader)
            for row in results:
                data.append(row)

    with open(file_path, "w") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=data[0].keys())
        for data in data:
            writer.writerow(data)


if __name__ == "__main__":
    main()
