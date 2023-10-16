import re
import requests
import sqlite3
import pandas as pd
from requests.adapters import HTTPAdapter, Retry


def take_proxies():
    connection = sqlite3.connect('proxies_2.db')
    proxies_sql_df = pd.read_sql_query("SELECT * FROM proxies", connection)
    proxies_list = []
    for ind, k in enumerate(proxies_sql_df['ip_1'], start=0):
        proxies = {
            "http": 'http://' + proxies_sql_df['ip_1'][ind],
            "https": 'http://' + proxies_sql_df['ip_2'][ind],
        }
        proxies_list.append(proxies)
    print(proxies_list)
    return proxies_list


broken_proxy_list = []
proxies_list_ = take_proxies()
inns = ['2720056787', '7729483920']


def get_gz(inn):
    url = 'https://sbis.ru/contragents/'+str(inn)

    session = requests.Session()
    adapter = HTTPAdapter(max_retries=Retry(total=1, backoff_factor=1))
    adapter.max_retries.respect_retry_after_header = False
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    # response, chosen_proxy = make_request(url, session, None, None, proxies_list_, proxy)
    response = session.get(url)
    response_text = str(response.text)
    session.close()

    if 'Нет данных об участии в торгах и заключенных госконтрактах' in response_text:
        print("Нет данных об участии в торгах и заключенных госконтрактах")
        gz_count = 0
    else:
        if ">Госконтракты<" in response_text:
            gz_count = re.findall("<div class=\"cCard__Reliability-Tender-Block-C2\">.*?</div>", response_text)
            gz_count = re.findall(">\d+<", str(gz_count[len(gz_count)-1]))
            gz_count = re.sub(">", '', gz_count[0])
            gz_count = re.sub("<", '', gz_count)
        else:
            print("Нет данных об участии в торгах и заключенных госконтрактах")
            gz_count = 0
    return gz_count


if __name__ == "__main__":
    for i in inns:
        gz_c = get_gz(i)
        print(gz_c)


# <div class="cCard__Reliability-Tender-Block-C2">18</div>
# <div class="cCard__Reliability-Tender-Block-C2">9</div>
# <div class="cCard__Reliability-Tender-Block-C2">2</div>
