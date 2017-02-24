# -*- coding: utf-8 -*-
import os

import sqlite3

current_directory = os.path.dirname(os.path.realpath(__file__))
db_file = os.path.join(current_directory, 'data.db')


def main():
    connection = sqlite3.connect(db_file)

    with connection:
        cursor = connection.cursor()

        cursor.execute('SELECT COUNT(*) from logs where is_processed = 1;')
        processed = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) from logs where was_error = 1;')
        with_errors = cursor.fetchone()[0]

        print('Processed: {}'.format(processed))
        print('With errors: {}'.format(with_errors))

if __name__ == '__main__':
    main()
