import requests
import re
import time
import pandas as pd
import Nologi_search
import Nologi_GZ_sbis
import os.path
import sqlite3
from requests.adapters import HTTPAdapter, Retry
import random
import proxy_

pd.set_option('display.max_columns', None)

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
    proxies_list_local = []
    for ind, k in enumerate(proxies_sql_df['ip_1'], start=0):
        proxies = {
            "http": 'http://' + proxies_sql_df['ip_1'][ind],
            "https": 'http://' + proxies_sql_df['ip_2'][ind],
        }
        proxies_list_local.append(proxies)
    # print(proxies_list_local)
    return proxies_list_local


def countdown(t):
    print("Current request time: ", t, " sec")
    while t:
        time.sleep(1)
        t -= 1


# sites Белгород.xlsx
import_file = input('\n\nВведите название файла (название.xlsx): ')
if import_file == "proxy":
    check_p = input("Обновление прокси займёт от 15 до 20 минут. Вы уверены, что хотите продолжить? (да/нет)")
    if check_p == "да":
        proxy_.get_proxies()
        print("Прокси обновлены.")
        import_file = input('Введите название файла (название.xlsx): ')
    else:
        import_file = input('Введите название файла (название.xlsx): ')

print(import_file)
region_num = input('Введите номер региона, только цифры: ')
comp_list = pd.read_excel(import_file, sheet_name=0)['Компания']
broken_proxy_list = []
proxies_list = take_proxies()


def find_excel(file_nom):
    global comp_list
    file_exists = os.path.exists(file_nom)
    if file_exists:
        existing_df = pd.read_excel(file_nom, sheet_name=0)
        existing_df = existing_df.drop_duplicates(subset=['ИНН'])
        final_df_ = existing_df
        start_index = comp_list.loc[comp_list == existing_df['Изначальное название компании'].iloc[-1]].index[0]
        print("Start index: ", start_index)
        token_series = final_df_['ИНН']
        return final_df_, start_index, token_series
    else:
        start_index = 0
        final_df_ = pd.DataFrame()
        token_series = pd.Series(dtype=pd.StringDtype())
        print("no xlsx file found")
        return final_df_, start_index, token_series


def find_txt():
    file_exists = os.path.exists('comps_to_avoid.txt')
    if file_exists:
        avoid_list = open('comps_to_avoid.txt', 'r', encoding='utf-8')
        avoid_list = avoid_list.read()
        print("Txt file found!")
        return avoid_list
    else:
        print("no 'comps_to_avoid.txt' file found!")
        input("press enter to close")
        quit()


comps_to_avoid = find_txt()

final_df, start_ind, inn_sr = find_excel(re.sub("\.xlsx", '', import_file) + ' data.xlsx')


# last_comp = final_df['Изначальное название компании'].iloc[-1]
# print("last_comp: ", last_comp)


def make_request(url_, session_, headers_, data_, proxies_list_, taken_proxy):
    global broken_proxy_list
    response_ = ""
    r_p = None
    while not response_ == '200':
        if len(broken_proxy_list) == len(proxies_list_)-1:
            broken_proxy_list = []
        try:
            if taken_proxy is None:
                done = False
                while done is not True:
                    taken_proxy_step_1 = random.choice(proxies_list_)
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
                taken_proxy_step_1 = random.choice(proxies_list_)
                if taken_proxy_step_1 not in broken_proxy_list:
                    taken_proxy = taken_proxy_step_1
                    done = True
                else:
                    done = False

            pass
    print(response_)
    return r_p, taken_proxy


def run_scrape():
    file_name = re.sub("\.xlsx", '', import_file) + ' data'
    # sites Белгород.xlsx
    print("Название файла: ", file_name)
    global final_df, start_ind, comps_to_avoid
    for cn_ind, comp_name in enumerate(comp_list):
        print(comp_list[cn_ind + start_ind])
        if comp_list[cn_ind + start_ind] not in comps_to_avoid:
            # countdown(2)
            tokens, first_proxy = Nologi_search.search_tokens(comp_list[cn_ind + start_ind], region_num)
        else:
            print("Компания в списке пропускаемых компаний, переход к следующей из списка.")
            continue

        for init_token in tokens:
            init_url = 'https://pb.nalog.ru/company.html?token=' + init_token
            url = 'https://pb.nalog.ru/company-proc.json'

            token = re.findall("token=.*", init_url)
            token = re.sub("\[\'token=", "", str(token))
            token = re.sub("\']", "", token)

            payload2 = {
                'token': token,
                'method': 'get-request',
                'success': 'undefined'
            }
            # countdown(2)
            session = requests.Session()
            adapter = HTTPAdapter(max_retries=Retry(total=3, backoff_factor=2))
            adapter.max_retries.respect_retry_after_header = False
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            print("Страница компании: первый запрос (1/2)")
            r, chosen_pr = make_request(url, session, headers, payload2, proxies_list, first_proxy)
            # r = session.post(url, headers=headers, data=payload2)
            r_dict = r.json()

            payload3 = {  # ____________
                'token': r_dict['token'],
                'id': r_dict['id'],
                'method': 'get-response'
            }  # _______________________
            countdown(2)
            print("Страница компании: второй запрос (2/2)")
            r2, chosen_pr_2 = make_request(url, session, headers, payload3, proxies_list, chosen_pr)
            # r2 = session.post(url, headers=headers, data=payload3)
            r2_dict = r2.json()
            session.close()

            try:
                inn_local = r2_dict['vyp']['ИНН']
                if inn_sr.astype(str).str.contains(inn_local, regex=False).any():
                    print("Компания уже в списке, переход к следующей из списка.")
                    continue
                else:
                    pass
            except:
                print("Сломанная компания, переход к следующей из списка.")
                continue

            comp_info = pd.DataFrame()
            comp_info['Изначальное название компании'] = ['none']
            comp_info['Название компании'] = ['none']
            comp_info['ИНН'] = ['none']
            comp_info['ОКВЭД'] = ['none']
            comp_info['Адрес'] = ['none']
            comp_info['Уставной капитал'] = ['none']
            comp_info['Среднесписочная численность сотрудников'] = ['none']
            comp_info['Выручка 2021'] = ['none']
            comp_info['Выручка 2020'] = ['none']
            comp_info['Выручка 2019'] = ['none']

            try:
                comp_info['Изначальное название компании'] = comp_list[cn_ind + start_ind]
                comp_info['Название компании'] = r2_dict['vyp']['НаимЮЛСокр']
                comp_info['ИНН'] = r2_dict['vyp']['ИНН']
            except:
                print("Сломанная компания, переход к следующей из списка.")
                continue
            try:
                comp_info['ОКВЭД'] = r2_dict['vyp']['КодОКВЭД']
            except:
                pass
            try:
                comp_info['Адрес'] = r2_dict['vyp']['Адрес']
            except:
                pass
            try:
                comp_info['Уставной капитал'] = r2_dict['vyp']['СумКап']
                comp_info['Среднесписочная численность сотрудников'] = r2_dict['vyp']['sschr']
                comp_info['Выручка 2021'] = r2_dict['form1'][0]['revenue']
                comp_info['Выручка 2020'] = r2_dict['form1'][1]['revenue']
                comp_info['Выручка 2019'] = r2_dict['form1'][2]['revenue']
            except:
                pass

            print("Поиск госзакупок: запрос")
            gz_num = Nologi_GZ_sbis.get_gz(comp_info['ИНН'])
            comp_info['Госзаказ контракты'] = gz_num

            final_df = pd.concat([final_df, comp_info], axis=0, ignore_index=True)
            final_df.to_excel('%s.xlsx' % file_name, index=False)
            print("Добавлена компания ", r2_dict['vyp']['НаимЮЛСокр'])
    final_df = final_df[~final_df['Выручка 2021'].isin(['none'])]
    final_df.to_excel('final %s.xlsx' % file_name, index=False)
    print("Все компании из списка найдены!")
    input("Нажмите Enter чтобы выйти")


run_scrape()

"""prx_lit = take_proxies()
end_point = len(prx_lit)
p = 0
while p < end_point:
    print("Current proxy: ", prx_lit[p])
    run_scrape(prx_lit[p])
    p += 1
    if p == end_point - 1:
        p = 0"""

# pyinstaller --onefile Web_scrp\Nologi_scrape\Nologi_comp_info.py
