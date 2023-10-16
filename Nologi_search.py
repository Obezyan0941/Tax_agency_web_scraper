import random
import time
import requests
from requests.adapters import HTTPAdapter, Retry
import sqlite3
import pandas as pd

url = 'https://pb.nalog.ru/search.html#'

headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'ru-RU,ru;q=0.9,ja-JP;q=0.8,ja;q=0.7,en-US;q=0.6,en;q=0.5,zh-CN;q=0.4,zh;q=0.3',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Length': '194',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Cookie': '_ym_uid=1675194518300678781; _ym_d=1675194518; _ym_isad=2; _ym_visorc=b; JSESSIONID='
              'B1E185D62E51873F1A92B3844C'
              'AE8C78',
    'DNT': '1',
    'Host': 'pb.nalog.ru',
    'Origin': 'https://pb.nalog.ru',
    'Pragma': 'no-cache',
    'Referer': 'https://pb.nalog.ru/company.html?token=E72E0923F114BE457B2F6315F592917A995925C264BBD54866E6412CD38688'
               '581E56D37C0F2EF61FB0DB123EF551C0756B7D3FC5EFE600C38B45B4114D207835',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0'
                  ' Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua': '\"Not_A Brand\";v=\"99\", \"Google Chrome\";v=\"109\", \"Chromium\";v=\"109\"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '\"Windows\"'}


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
    # print(proxies_list)
    return proxies_list


proxies_list_ = take_proxies()
broken_proxy_list = []


def countdown(t):
    print("Current request time: ", t, " sec")
    while t:
        time.sleep(1)
        t -= 1


def make_request(url_, session_, headers_, data_, proxies_list_local, taken_proxy):
    global broken_proxy_list
    response_ = ""
    r_p = None
    while not response_ == '200':
        if len(broken_proxy_list) == len(proxies_list_local)-1:
            broken_proxy_list = []
        try:
            if taken_proxy is None:
                done = False
                while done is not True:
                    taken_proxy_step_1 = random.choice(proxies_list_local)
                    if taken_proxy_step_1 not in broken_proxy_list:
                        taken_proxy = taken_proxy_step_1
                        done = True
                    else:
                        done = False
            # print(taken_proxy)
            # print("broken proxies: ", broken_proxy_list)
            session_.proxies.update(taken_proxy)
            start_time = time.time()
            while time.time() - start_time < 11:
                r_p = session_.post(url_, headers=headers_, data=data_, timeout=10)
                if time.time() - start_time >= 11 and not str(r_p.status_code) == '200':
                    r_p.close()
                    # print("Time's up!")
                    raise Exception("Going op")
                elif str(r_p.status_code) == '200' and time.time() - start_time < 11:
                    # print("break")
                    break
            # print("--- %s seconds ---" % (time.time() - start_time))
            response_ = str(r_p.status_code)
            r_p.close()
        except:
            print("Повторный запрос")
            broken_proxy_list.append(taken_proxy)
            done = False
            while done is not True:
                taken_proxy_step_1 = random.choice(proxies_list_local)
                if taken_proxy_step_1 not in broken_proxy_list:
                    taken_proxy = taken_proxy_step_1
                    done = True
                else:
                    done = False
            pass
    print(response_)
    return r_p, taken_proxy


def search_tokens(comp_nom, region):
    global headers, url
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=Retry(total=1, backoff_factor=1))
    adapter.max_retries.respect_retry_after_header = False
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    data1 = {'method': 'get-lst'}
    region = "31"
    data3 = {'mode': 'search-ul-ext', 'page': '1', 'pageSize': '10', 'pbCaptchaToken': '', 'token': '',
             'queryUlExt': comp_nom, 'okvedUlExt': '', 'regionUlExt': region, 'districtUlExt': '', 'cityUlExt': '',
             'arrearUlExt': '0;10000001', 'sschrUlExt': '0;10001', 'taxpayUlExt': '0;10000001',
             'expenseUlExt': '0;10000001', 'revenueUlExt': '0;10000001', 'offenseUlExt': '', 'kgnUlExt': '',
             'taxmodeUlExt': '', 'invalidUlExt': '', 'rsmpUlExt': ''}
    data4 = {'c': 'getDict',
             'dict': 'PB_REGION',
             'kind': 'TREE',
             'delimiter': ',',
             'val': region
             }
    data5 = {'parentLevel': '1', 'parentCode': region + '00000000000'}
    print("Страница поиска: первый запрос (1/4)")
    r, chosen_pr = make_request('https://pb.nalog.ru/compare-proc.json', session, headers, data1, proxies_list_, None)
    # r = session.post('https://pb.nalog.ru/compare-proc.json', headers=headers, data=data1)
    countdown(1)
    print("Страница поиска: второй запрос (2/4)")
    r_2, chosen_pr_ = make_request('https://pb.nalog.ru/static/set-proc.json', session, headers, data4, proxies_list_,
                                   chosen_pr)
    countdown(1)
    print("Страница поиска: третий запрос (3/4)")
    r_2, chosen_pr__ = make_request('https://pb.nalog.ru/kladr-proc.json', session, headers, data5, proxies_list_,
                                    chosen_pr_)
    countdown(1)
    print("Страница поиска: четвёртый запрос (4/4)")
    l_, chosen_pr_2 = make_request('https://pb.nalog.ru/search-proc.json', session, headers, data3, proxies_list_,
                                   chosen_pr__)
    # l = session.post('https://pb.nalog.ru/search-proc.json', headers=headers, data=data2)
    # print(l.json())
    if "Требуется ввести цифры с картинки" in l_.text:
        print('Требуется ввести цифры с картинки')
        input("press enter to close")
        quit()

    tokens = []
    for i in l_.json()['ul']['data']:
        tokens.append(i['token'])
    print("Компания %s найдена" % comp_nom)
    tokens = tokens[0:5]
    # print(tokens)
    session.close()
    return tokens, chosen_pr_2


if __name__ == "__main__":
    for l in range(0, 10):
        search_tokens("МИРАТОРГ", "31")

    # browser = mechanicalsoup.Browser()
    # browser.session.headers.update(headers)
    # login_page = browser.get(url)
    # login_html = login_page.soup
    # form = login_html.select("form")
    # form[0].select("input")[5]["value"] = comp_nom
    # search_page = browser.submit(form[0], url)
    # search_page_dict = search_page.json()
    # proxies = {'http': 'http://117.54.114.98:80', 'https': 'http://5.135.240.70:8080'}
