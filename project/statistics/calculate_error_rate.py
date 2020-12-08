import csv
import os
from pathlib import Path

stats_output_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "output")


def main():
    dealer_csv = os.path.join(stats_output_folder, "dealer_2009.db_100000_0.csv")
    regular_csv = os.path.join(stats_output_folder, "2009.db_100000_0.csv")

    calculate_errors(dealer_csv)
    calculate_errors(regular_csv)


def calculate_errors(csv_file):
    print(Path(csv_file).name)
    error_borders = [30, 20, 10]
    for error_border in error_borders:
        print(f"Error border {error_border}%")
        with open(csv_file, mode="r") as f:
            reader = csv.DictReader(f)
            results = list(reader)
            correct_predictions = 0
            total_predictions = len(results)
            print(f"Total results: {total_predictions}")
            for row in results:
                original_cost = int(row["original_cost"])
                predicted_cost = int(row["predicted_cost"])

                first_border = predicted_cost - round((predicted_cost / 100) * error_border)
                second_border = predicted_cost + round((predicted_cost / 100) * error_border)

                if first_border < original_cost < second_border:
                    correct_predictions += 1

            print(f"Correct predictions: {correct_predictions}, {(correct_predictions / total_predictions) * 100:.2f}%")


if __name__ == "__main__":
    main()
