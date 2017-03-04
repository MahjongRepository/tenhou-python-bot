# -*- coding: utf-8 -*-
import os
import sqlite3
import sys

db_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'db')
db_file = ''


def main():
    parse_command_line_arguments()

    connection = sqlite3.connect(db_file)

    with connection:
        cursor = connection.cursor()

        cursor.execute('SELECT COUNT(*) from logs;')
        total = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) from logs where is_processed = 1;')
        processed = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) from logs where was_error = 1;')
        with_errors = cursor.fetchone()[0]

        print('Total: {}'.format(total))
        print('Processed: {}'.format(processed))
        print('With errors: {}'.format(with_errors))


def parse_command_line_arguments():
    if len(sys.argv) > 1:
        year = sys.argv[1]
    else:
        year = '2017'

    global db_file
    db_file = os.path.join(db_folder, '{}.db'.format(year))

if __name__ == '__main__':
    main()
