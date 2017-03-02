# -*- coding: utf-8 -*-
"""
Script will load log ids from the database and will download log content
"""
import bz2
import os
import sqlite3

import requests
import sys

db_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'db')
db_file = ''


def main():
    should_continue = True
    while should_continue:
        try:
            limit = 50
            print('Load {} records'.format(limit))
            results = load_not_processed_logs(limit)
            if not results:
                should_continue = False

            for log_id in results:
                print('Process {}'.format(log_id))
                download_log_content(log_id)
        except KeyboardInterrupt:
            should_continue = False


def download_log_content(log_id):
    """
    We will download log content and will store it in the file,
    also we will store compressed version in the database
    """
    url = 'http://e.mjv.jp/0/log/?{0}'.format(log_id)

    binary_content = None
    was_error = False
    try:
        response = requests.get(url)
        binary_content = response.content
        if 'mjlog' not in response.text:
            was_error = True
    except Exception as e:
        was_error = True

    connection = sqlite3.connect(db_file)

    with connection:
        cursor = connection.cursor()

        compressed_content = ''
        if not was_error:
            try:
                compressed_content = bz2.compress(binary_content)
            except:
                was_error = True

        cursor.execute('UPDATE logs SET is_processed = ?, was_error = ?, log_content = ? WHERE log_id = ?;',
                       [1, was_error and 1 or 0, compressed_content, log_id])

        print('Was errors: {}'.format(was_error))


def load_not_processed_logs(limit):
    connection = sqlite3.connect(db_file)

    with connection:
        cursor = connection.cursor()
        cursor.execute('SELECT log_id FROM logs where is_processed = 0 and was_error = 0 LIMIT ?;', [limit])
        data = cursor.fetchall()
        results = [x[0] for x in data]

    return results


def parse_command_line_arguments():
    if len(sys.argv) > 1:
        year = sys.argv[1]
    else:
        year = '2017'

    global db_file
    db_file = os.path.join(db_folder, '{}.db'.format(year))

if __name__ == '__main__':
    main()
