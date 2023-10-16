import requests
import re
import sqlite3
import pandas as pd
from requests.adapters import HTTPAdapter, Retry
import time


def run_sql():
    connection = sqlite3.connect('proxies.db')
    cursor = connection.cursor()
    cursor.execute("DROP TABLE IF EXISTS proxies")
    cursor.execute("CREATE TABLE IF NOT EXISTS proxies(ind INTEGER PRIMARY KEY, ip_1 TEXT, ip_2 TEXT)")
    proxies_sql_df = pd.read_sql_query("SELECT * FROM proxies", connection)
    print(proxies_sql_df)
    if not proxies_sql_df.empty:
        last_ind = proxies_sql_df['ind'].iloc[-1]
    else:
        last_ind = 0
    print(last_ind)
    connection.commit()
    return last_ind


def get_proxies():
    start_time = time.time()
    last_ind = run_sql()
    url = "https://free-proxy-list.net/"
    response = requests.get(url)
    response_text = str(response.text)

    ip_list_1 = re.findall('\d+\.\d+\.\d+\.\d+:\d+', response_text)

    ip_list_2 = []
    for i in range(0, len(ip_list_1), 2):
        ip_list_2.append(ip_list_1[i])
    for j in ip_list_2:
        ip_list_1.remove(j)

    tsuku_ip_list_1 = []
    tsuku_ip_list_2 = []
    tsuku_proxies = {}
    working_count = 0
    print("Searching proxies...")
    for l in range(len(ip_list_1)):
        if working_count >= 10:
            break
        try:
            connection = sqlite3.connect('proxies.db')
            cursor = connection.cursor()
            proxies = {
                "http": 'http://' + ip_list_1[l],
                "https": 'http://' + ip_list_2[l],
            }
            session = requests.Session()
            session.proxies.update(proxies)
            adapter = HTTPAdapter(max_retries=Retry(total=1, backoff_factor=1))
            adapter.max_retries.respect_retry_after_header = False
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            r = session.get('https://www.w3schools.com/python/python_lists_remove.asp', timeout=6)
            print(r)
            tsuku_ip_list_1.append(ip_list_1[l])
            tsuku_ip_list_2.append(ip_list_2[l])
            tsuku_proxies = proxies
            session.close()
            print("Working proxies found successfully")
            working_count += 1
            cursor.execute("INSERT INTO proxies VALUES (?, ?, ?)", (working_count, ip_list_1[l], ip_list_2[l]))
            proxies_sql_df = pd.read_sql_query("SELECT * FROM proxies", connection)
            print(proxies_sql_df.iloc[-1])
            connection.commit()
        except:
            print("Searching proxies...")
            continue
        """if working_count == 10:
            break"""
    print(tsuku_proxies)
    print("--- %s seconds ---" % (time.time() - start_time))
    return tsuku_proxies


def get_proxies_no_Check():
    connection = sqlite3.connect('proxies_nc_1.db')
    cursor = connection.cursor()
    cursor.execute("DROP TABLE IF EXISTS proxies")
    cursor.execute("CREATE TABLE IF NOT EXISTS proxies(ind INTEGER PRIMARY KEY, ip_1 TEXT, ip_2 TEXT)")

    url = "https://free-proxy-list.net/"
    response = requests.get(url)
    response_text = str(response.text)

    ip_list_1 = re.findall('\d+\.\d+\.\d+\.\d+:\d+', response_text)

    ip_list_2 = []
    for i in range(0, len(ip_list_1), 2):
        ip_list_2.append(ip_list_1[i])
    for j in ip_list_2:
        ip_list_1.remove(j)

    tsuku_ip_list_1 = []
    tsuku_ip_list_2 = []
    print("Searching proxies...")
    for l in range(len(ip_list_1)):
        tsuku_ip_list_1.append(ip_list_1[l])
        tsuku_ip_list_2.append(ip_list_2[l])
        cursor.execute("INSERT INTO proxies VALUES (?, ?, ?)", (l, ip_list_1[l], ip_list_2[l]))
        proxies_sql_df = pd.read_sql_query("SELECT * FROM proxies", connection)
        print(proxies_sql_df.iloc[-1])
    connection.commit()
    print("Working proxies found successfully")


if __name__ == '__main__':
    get_proxies()
