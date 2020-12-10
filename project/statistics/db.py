import bz2
import sqlite3


def load_logs_from_db(db_path: str, limit: int, offset: int):
    """
    Load logs from db and decompress logs content.
    How to download games content you can learn there: https://github.com/MahjongRepository/phoenix-logs
    """
    connection = sqlite3.connect(db_path)

    with connection:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT log_id, log_content FROM logs where is_sanma = 0 ORDER BY date LIMIT ? OFFSET ?;",
            [limit, offset],
        )
        data = cursor.fetchall()

    results = []
    for x in data:
        log_id = x[0]
        try:
            results.append({"log_id": log_id, "log_content": bz2.decompress(x[1]).decode("utf-8")})
        except Exception as e:
            print(e)
            print(log_id)

    return results


def get_total_logs_count(db_path: str):
    connection = sqlite3.connect(db_path)

    with connection:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM logs where is_sanma = 0;",
        )
        result = cursor.fetchall()
        return result[0][0]
