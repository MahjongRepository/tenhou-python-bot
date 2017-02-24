# -*- coding: utf-8 -*-
"""
Script will load log ids from the database and will download log content.
Log content will be stores in the DB (compressed version) and in the file.
"""
import os
import sqlite3
from distutils.dir_util import mkpath

import requests

# need to find out better way to do relative imports
# noinspection PyUnresolvedReferences
from logs_compressor import TenhouLogCompressorNoFile

current_directory = os.path.dirname(os.path.realpath(__file__))
data_directory = os.path.join(current_directory, 'data')
db_file = os.path.join(current_directory, 'data.db')


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

    log_folder = prepare_log_folder(log_id)

    content = ''
    was_error = False
    try:
        response = requests.get(url)
        content = response.text
        if 'mjlog' not in content:
            was_error = True
    except Exception as e:
        was_error = True

    connection = sqlite3.connect(db_file)

    with connection:
        cursor = connection.cursor()

        # store original content to the file
        # and compressed version to the database
        if not was_error:
            original_content = content
            log_path = os.path.join(log_folder, log_id + '.mjlog')
            with open(log_path, 'w') as f:
                f.write(original_content)

            try:
                compressor = TenhouLogCompressorNoFile(original_content)
                content = compressor.compress(log_id)
            except Exception as e:
                os.remove(log_path)
                was_error = True
                content = ''

        sql = 'UPDATE logs SET is_processed = {}, was_error = {}, log = "{}" WHERE log_id = "{}";'.format(
            1,
            was_error and 1 or 0,
            content,
            log_id
        )
        cursor.execute(sql)

        print('Was errors: {}'.format(was_error))


def load_not_processed_logs(limit):
    connection = sqlite3.connect(db_file)

    with connection:
        cursor = connection.cursor()
        cursor.execute('SELECT log_id FROM logs where is_processed = 0 and was_error = 0 LIMIT {};'.format(limit))
        data = cursor.fetchall()
        results = [x[0] for x in data]

    return results


def prepare_log_folder(log_id):
    """
    To not store million files in the one folder. We will separate them
    based on log has.
    This log 2017022109gm-00a9-0000-897ed93b will be converted to the
    /8/9/7/e/ folder
    """
    temp = log_id.split('-')
    game_hash = list(temp[-1][:4])

    path = os.path.join(data_directory, *game_hash)
    mkpath(path)

    return path

if __name__ == '__main__':
    main()
