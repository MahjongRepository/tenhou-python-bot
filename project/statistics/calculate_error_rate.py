import csv
import json
import os

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
    "han",
    "fu",
    "original_cost",
]


def main():
    data_csv = os.path.join(stats_output_folder, "combined_test.csv")
    calculate_errors(data_csv)


def calculate_errors(csv_file):
    data = {}

    with open(csv_file, mode="r") as f:
        reader = csv.DictReader(f, fieldnames=CSV_HEADER)

        results = list(reader)
        total_predictions = len(results)

        error_borders = [30, 20, 10]
        for error_border in error_borders:
            correct_predictions = 0
            for row in results:
                original_cost = int(row["original_cost"])
                predicted_cost = int(row["predicted_cost"])

                if error_border_predicted(original_cost, predicted_cost, error_border):
                    correct_predictions += 1

            data[f"{error_border}% border"] = (correct_predictions / total_predictions) * 100

        correct_predictions = 0
        for row in results:
            original_cost = int(row["original_cost"])
            predicted_cost = int(row["predicted_cost"])
            is_dealer = bool(int(row["is_dealer"]))

            if is_dealer and is_dealer_hand_correctly_predicted(original_cost, predicted_cost):
                correct_predictions += 1

            if not is_dealer and is_regular_hand_correctly_predicted(original_cost, predicted_cost):
                correct_predictions += 1

        data["empirical"] = (correct_predictions / total_predictions) * 100

        print("Correct % of predictions:")
        print(json.dumps(data, indent=2))


def error_border_predicted(original_cost, predicted_cost, border_percentage):
    first_border = predicted_cost - round((predicted_cost / 100) * border_percentage)
    second_border = predicted_cost + round((predicted_cost / 100) * border_percentage)

    if first_border < original_cost < second_border:
        return True

    return False


def is_dealer_hand_correctly_predicted(original_cost, predicted_cost):
    assert original_cost >= 2000

    if original_cost <= 3900 and predicted_cost <= 5800:
        return True

    if 3900 < original_cost <= 5800 and predicted_cost <= 7700:
        return True

    if 5800 < original_cost <= 7700 and 3900 <= predicted_cost <= 12000:
        return True

    if 7700 < original_cost <= 12000 and 5800 <= predicted_cost <= 18000:
        return True

    if 12000 < original_cost <= 18000 and 7700 <= predicted_cost <= 24000:
        return True

    if original_cost > 18000 and predicted_cost > 12000:
        return True

    return False


def is_regular_hand_correctly_predicted(original_cost, predicted_cost):
    assert original_cost >= 1300

    if original_cost <= 2600 and predicted_cost <= 3900:
        return True

    if 2600 < original_cost <= 3900 and predicted_cost <= 5200:
        return True

    if 3900 < original_cost <= 5200 and 2600 <= predicted_cost <= 8000:
        return True

    if 5200 < original_cost <= 8000 and 3900 <= predicted_cost <= 12000:
        return True

    if 8000 < original_cost <= 12000 and 5200 <= predicted_cost <= 16000:
        return True

    if original_cost > 12000 and predicted_cost > 8000:
        return True

    return False


if __name__ == "__main__":
    main()
