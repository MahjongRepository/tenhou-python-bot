# -*- coding: utf-8 -*-
"""
Script to download latest phoenix games and store their ids in the database
We can run it once a day or so, to get new data
"""
import shutil
from datetime import datetime
import calendar
import gzip
import os

import sqlite3
from distutils.dir_util import mkpath

import requests
import sys

current_directory = os.path.dirname(os.path.realpath(__file__))
logs_directory = os.path.join(current_directory, 'data', 'logs')
db_folder = os.path.join(current_directory, 'db')
db_file = ''

if not os.path.exists(logs_directory):
    mkpath(logs_directory)

if not os.path.exists(db_folder):
    mkpath(db_folder)


def main():
    parse_command_line_arguments()

    # for the initial set up
    # set_up_database()

    download_game_ids()

    results = process_local_files()
    if results:
        add_logs_to_database(results)


def process_local_files():
    """
    Function to process scc*.html files that can be obtained
    from the annual archives with logs or from latest phoenix games
    """
    print('Preparing the list of games')

    results = []
    for file_name in os.listdir(logs_directory):
        if 'scc' not in file_name:
            continue

        # after 2013 tenhou produced compressed logs
        if '.gz' in file_name:
            with gzip.open(os.path.join(logs_directory, file_name), 'r') as f:
                for line in f:
                    line = str(line, 'utf-8')
                    _process_log_line(line, results)
        else:
            with open(os.path.join(logs_directory, file_name)) as f:
                for line in f:
                    _process_log_line(line, results)

    print('Found {} games'.format(len(results)))

    shutil.rmtree(logs_directory)

    return results


def download_game_ids():
    """
    Download latest phoenix games from tenhou
    """
    connection = sqlite3.connect(db_file)

    last_name = ''
    with connection:
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM last_downloads ORDER BY date DESC LIMIT 1;')
        data = cursor.fetchone()
        if data:
            last_name = data[0]

    download_url = 'http://tenhou.net/sc/raw/dat/'
    url = 'http://tenhou.net/sc/raw/list.cgi'

    response = requests.get(url)
    response = response.text.replace('list(', '').replace(');', '')
    response = response.split(',\r\n')

    records_was_added = False
    for archive_name in response:
        if 'scc' in archive_name:
            archive_name = archive_name.split("',")[0].replace("{file:'", '')

            file_name = archive_name
            if '/' in file_name:
                file_name = file_name.split('/')[1]

            if file_name > last_name:
                last_name = file_name
                records_was_added = True

                archive_path = os.path.join(logs_directory, file_name)
                if not os.path.exists(archive_path):
                    print('Downloading... {}'.format(archive_name))

                    url = '{}{}'.format(download_url, archive_name)
                    page = requests.get(url)
                    with open(archive_path, 'wb') as f:
                        f.write(page.content)

    if records_was_added:
        unix_time = calendar.timegm(datetime.utcnow().utctimetuple())
        with connection:
            cursor = connection.cursor()
            cursor.execute('INSERT INTO last_downloads VALUES (?, ?);', [last_name, unix_time])


def _process_log_line(line, results):
    line = line.strip()
    # sometimes there is empty lines in the file
    if not line:
        return None

    result = line.split('|')
    game_type = result[2].strip()

    # we don't need hirosima replays for now
    if game_type.startswith('三'):
        return None

    # example: <a href="http://tenhou.net/0/?log=2009022023gm-00e1-0000-c603794d">牌譜</a>
    game_id = result[3].split('log=')[1].split('"')[0]

    # example: 四鳳東喰赤
    is_tonpusen = game_type[2] == '東'

    results.append([game_id, is_tonpusen])


def set_up_database():
    """
    Init logs table and add basic indices
    :return:
    """
    if os.path.exists(db_file):
        print('Remove old database')
        os.remove(db_file)

    connection = sqlite3.connect(db_file)

    print('Set up new database')
    with connection:
        cursor = connection.cursor()
        cursor.execute("""
        CREATE TABLE logs(log_id text primary key,
                          is_tonpusen int,
                          is_processed int,
                          was_error int,
                          log_content text);
        """)
        cursor.execute("CREATE INDEX is_tonpusen_index ON logs (is_tonpusen);")
        cursor.execute("CREATE INDEX is_processed_index ON logs (is_processed);")
        cursor.execute("CREATE INDEX was_error_index ON logs (was_error);")

        cursor.execute("""
        CREATE TABLE last_downloads(name text,
                                    date int);
        """)


def add_logs_to_database(results):
    """
    Store logs to the sqllite3 database
    """
    print('Inserting new values to the database')
    connection = sqlite3.connect(db_file)
    with connection:
        cursor = connection.cursor()

        for item in results:
            cursor.execute('INSERT INTO logs VALUES (?, ?, 0, 0, "");', [item[0],
                                                                         item[1] and 1 or 0])


def parse_command_line_arguments():
    if len(sys.argv) > 1:
        year = sys.argv[1]
    else:
        year = '2017'

    global db_file
    db_file = os.path.join(db_folder, '{}.db'.format(year))


if __name__ == '__main__':
    main()
