from bs4 import BeautifulSoup
from bs4 import Comment
import pandas as pd
import requests
import os

def crawler(url, stat_id, table_id):
    response = requests.get(url)
    if response.status_code == 200:
        html_content = response.text
    else:
        print(f"Error fetching the page: {response.status_code}")
        return
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('div', {'id': stat_id})
    comment = table.find_all(string=lambda text: isinstance(text, Comment))
    data = BeautifulSoup(comment[0], 'html.parser').find_all('tr')
    res = dict()
    for i, g in enumerate(data[1].find_all('th')):
        if i != 0:
            res[g.get('data-stat')] = []
    for i in range(2, len(data)):
        tmp = data[i].find_all('td')
        for x in tmp:
            if x.get('data-stat') in res.keys():
                if x.get('data-stat') != 'nationality':
                    res[x.get('data-stat')].append(x.getText())
                else:
                    s = x.getText().split(" ")
                    res[x.get('data-stat')].append(s[0])
    dframe = pd.DataFrame(res)
    if table_id == 2:
        dframe.drop(['gk_games', 'gk_games_starts', 'gk_minutes', 'minutes_90s'], axis=1, inplace=True)
    dframe.to_csv(f'table{table_id}.csv')

def cleaner():
    result = pd.read_csv('table1.csv')
    for i in range(3, 11):
        table = pd.read_csv(f"table{i}.csv")
        for i in table.columns:
            if i in result.columns:
                if i != 'Unnamed: 0':
                    table.drop(i, axis=1, inplace=True)
        result = pd.merge(result, table, on=['Unnamed: 0'], how='inner')
    merge = []
    table2 = pd.read_csv("table2.csv")
    for i in table2.columns:
        if i in result.columns:
            merge.append(i)
    merge.pop(0)
    result = pd.merge(result, table2, on=merge, how='left')
    result.drop(['Unnamed: 0_x', 'Unnamed: 0_y', 'minutes_90s', 'birth_year', 'matches'], axis=1, inplace=True)
    result['minutes'] = result['minutes'].apply(lambda x: int(''.join(x.split(','))))
    result = result[result['minutes'] > 90]
    result.sort_values(by=["player", 'age'], ascending=[True, False])
    result.to_csv('result.csv')

def delete_tables():
    for i in range(1, 11):
        try:
            os.remove(f'table{i}.csv')
        except FileNotFoundError:
            continue

def delete_result():
    try:
        os.remove(f'result.csv')
    except FileNotFoundError:
        pass

if __name__ == '__main__':
    delete_result()
    urls = [
        'https://fbref.com/en/comps/9/2023-2024/keepers/2023-2024-Premier-League-Stats',
        'https://fbref.com/en/comps/9/2023-2024/shooting/2023-2024-Premier-League-Stats',
        'https://fbref.com/en/comps/9/2023-2024/passing/2023-2024-Premier-League-Stats',
        'https://fbref.com/en/comps/9/2023-2024/passing_types/2023-2024-Premier-League-Stats',
        'https://fbref.com/en/comps/9/2023-2024/gca/2023-2024-Premier-League-Stats',
        'https://fbref.com/en/comps/9/2023-2024/defense/2023-2024-Premier-League-Stats',
        'https://fbref.com/en/comps/9/2023-2024/possession/2023-2024-Premier-League-Stats',
        'https://fbref.com/en/comps/9/2023-2024/playingtime/2023-2024-Premier-League-Stats',
        'https://fbref.com/en/comps/9/2023-2024/misc/2023-2024-Premier-League-Stats'
    ]
    stat_ids = ['all_stats_keeper', 'all_stats_shooting', 'all_stats_passing', 'all_stats_passing_types', 'all_stats_gca',
           'all_stats_defense',
           'all_stats_possession', 'all_stats_playing_time', 'all_stats_misc']
    url = 'https://fbref.com/en/comps/9/2023-2024/stats/2023-2024-Premier-League-Stats'
    response = requests.get(url)
    if response.status_code == 200:
        html_content = response.text
    else:
        print(f"Error fetching the page: {response.status_code}")
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('div', {'id': 'all_stats_standard'})
    comment = table.find_all(string=lambda text: isinstance(text, Comment))
    data = BeautifulSoup(comment[0], 'html.parser').find_all('tr')  # chuyển string về dạng tags
    idx = [0, 6, 10, 11, 13, 16, 22, 36]
    res = dict()
    for i, g in enumerate(data[1].find_all('th')):
        if i not in idx:
            res[g.get('data-stat')] = []
    for i in range(2, len(data)):
        tmp = data[i].find_all('td')
        for x in tmp:

            if x.get('data-stat') in res.keys():
                if x.get('data-stat') != 'nationality':
                    res[x.get('data-stat')].append(x.getText())
                else:
                    s = x.getText().split(" ")
                    res[x.get('data-stat')].append(s[0])

    dframe = pd.DataFrame(res)
    dframe.rename(columns={'goals_pens': 'non-Penalty Goals', 'pens_made': 'Penalty Goals'}, inplace=True)
    dframe.to_csv('table1.csv')
    for i, x in enumerate(zip(urls, stat_ids)):
        crawler(x[0], x[1], i + 2)
    cleaner()
    delete_tables()