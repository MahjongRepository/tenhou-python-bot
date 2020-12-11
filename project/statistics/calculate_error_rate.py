import csv
import os
from pathlib import Path

stats_output_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "output")

CSV_HEADER = [
    "is_dealer",
    "riichi_called_on_step",
    "current_enemy_step",
    "wind_number",
    "scores",
    "is_tsumogiri_riichi",
    "is_oikake_riichi",
    "is_oikake_riichi_against_dealer_riichi_threat",
    "is_riichi_against_open_hand_threat",
    "number_of_kan_in_enemy_hand",
    "number_of_dora_in_enemy_kan_sets",
    "number_of_yakuhai_enemy_kan_sets",
    "number_of_other_player_kan_sets",
    "live_dora_tiles",
    "tile_plus_dora",
    "tile_category",
    "discards_before_riichi_34",
    "predicted_cost",
    "lobby",
    "log_id",
    "win_tile_34",
    "original_cost",
]


def main():
    dealer_csv = os.path.join(stats_output_folder, "dealer_test.csv")
    regular_csv = os.path.join(stats_output_folder, "test.csv")

    calculate_errors(dealer_csv, dealer=True)
    print("")
    calculate_errors(regular_csv, dealer=False)


def calculate_errors(csv_file, dealer):
    print(Path(csv_file).name)

    with open(csv_file, mode="r") as f:
        reader = csv.DictReader(f, fieldnames=CSV_HEADER)
        results = list(reader)
        total_predictions = len(results)
        print(f"Total results: {total_predictions}")
        error_borders = [30, 20, 10]
        for error_border in error_borders:
            correct_predictions = 0
            print(f"Error border {error_border}%")
            for row in results:
                original_cost = int(row["original_cost"])
                predicted_cost = int(row["predicted_cost"])

                first_border = predicted_cost - round((predicted_cost / 100) * error_border)
                second_border = predicted_cost + round((predicted_cost / 100) * error_border)

                if first_border < original_cost < second_border:
                    correct_predictions += 1

            print(f"Correct predictions: {correct_predictions}, {(correct_predictions / total_predictions) * 100:.2f}%")

        print("Empirical")
        correct_predictions = 0
        for row in results:
            original_cost = int(row["original_cost"])
            predicted_cost = int(row["predicted_cost"])
            if dealer and in_dealer_hand_correctly_predicted(original_cost, predicted_cost):
                correct_predictions += 1
            if not dealer and in_regular_hand_correctly_predicted(original_cost, predicted_cost):
                correct_predictions += 1
        print(f"Correct predictions: {correct_predictions}, {(correct_predictions / total_predictions) * 100:.2f}%")


def in_dealer_hand_correctly_predicted(original_cost, predicted_cost):
    assert original_cost >= 2000

    if original_cost <= 3900:
        if predicted_cost <= 3900:
            return True

    if original_cost > 3900 and original_cost <= 5800:
        if predicted_cost > 3900 and predicted_cost <= 5800:
            return True

    if original_cost > 5800 and original_cost <= 7700:
        if predicted_cost > 5800 and predicted_cost <= 7700:
            return True

    if original_cost > 7700 and original_cost <= 9600:
        if predicted_cost > 7700 and predicted_cost <= 9600:
            return True

    if original_cost > 9600 and original_cost <= 12000:
        if predicted_cost > 9600 and predicted_cost <= 12000:
            return True

    error_border = 30
    first_border = predicted_cost - round((predicted_cost / 100) * error_border)
    second_border = predicted_cost + round((predicted_cost / 100) * error_border)

    if first_border < original_cost < second_border:
        return True

    return False


def in_regular_hand_correctly_predicted(original_cost, predicted_cost):
    assert original_cost >= 1300

    if original_cost <= 2600:
        if predicted_cost <= 2600:
            return True

    if original_cost > 2600 and original_cost <= 3900:
        if predicted_cost > 2600 and predicted_cost <= 3900:
            return True

    if original_cost > 3900 and original_cost <= 5200:
        if predicted_cost > 3900 and predicted_cost <= 5200:
            return True

    if original_cost > 5200 and original_cost <= 8000:
        if predicted_cost > 5200 and predicted_cost <= 8000:
            return True

    if original_cost > 8000 and original_cost <= 12000:
        if predicted_cost > 8000 and predicted_cost <= 12000:
            return True

    error_border = 30
    first_border = predicted_cost - round((predicted_cost / 100) * error_border)
    second_border = predicted_cost + round((predicted_cost / 100) * error_border)

    if first_border < original_cost < second_border:
        return True

    return False


if __name__ == "__main__":
    main()
