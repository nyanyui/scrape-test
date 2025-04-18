import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv
import os
import time
import random
# def scrape_race_results_as_array(race_id):
#     """指定されたレースIDからレース結果データをスクレイピングし、2次元配列形式で返す関数"""
#     url = f"https://db.netkeiba.com/race/{race_id}/"
#     headers = {'User-Agent': 'Mozilla/5.0'}
#     try:
#         res = requests.get(url, headers=headers)
#         res.raise_for_status()  # HTTPエラーをチェック
#         soup = BeautifulSoup(res.content, "html.parser")

#         # レース結果テーブルの抽出
#         horse_table = soup.select_one("table.race_table_01")
#         if not horse_table:
#             print(f"レース結果テーブルが見つかりませんでした: {race_id}")
#             return None

#         rows = horse_table.find_all("tr")[1:]
#         race_horse_data = []
#         for row in rows:
#             cols = row.find_all("td")
#             if len(cols) < 18:
#                 continue
#             horse_info = {
#                 "name": cols[3].text.strip(),
#                 "age_sex": cols[4].text.strip(),
#                 "weight": cols[5].text.strip(),
#                 "jockey": cols[6].text.strip(),
#                 # 必要に応じて他の馬の情報を追加
#                 "finish_order": cols[0].text.strip(),
#                 "frame_number": cols[1].text.strip(),
#                 "horse_number": cols[2].text.strip(),
#                 "finish_time": cols[7].text.strip(),
#                 "margin": cols[8].text.strip(),
#                 "passing_order": cols[10].text.strip(),
#                 "last_3f": cols[11].text.strip(),
#                 "odds": cols[12].text.strip(),
#                 "popularity": cols[13].text.strip(),
#                 "weight_change": cols[14].text.strip(),
#                 "trainer": cols[18].text.strip() if len(cols) > 18 else "",
#                 "owner": cols[19].text.strip() if len(cols) > 19 else "",
#                 "prize_money": cols[20].text.strip() if len(cols) > 20 else ""
#             }
#             race_horse_data.append(horse_info)
#             print(horse_info)
#             break

#         return race_horse_data

#     except requests.exceptions.RequestException as e:
#         print(f"エラーが発生しました: {race_id} - {e}")
#         return None
#     except Exception as e:
#         print(f"予期しないエラーが発生しました: {race_id} - {e}")
#         return None

# def generate_race_ids(start_year, end_year):
#     """指定された年の範囲でレースIDを生成する関数"""
#     race_ids = []
#     for year in range(start_year, end_year + 1):
#         for region in range(1, 11):  # 競馬場は10箇所
#             for kai in range(1, 6):  # 開催回数は最大5回
#                 for day in range(1, 13):  # 開催日数は最大12日
#                     for r in range(1, 13):  # レース数は最大12レース
#                         race_id = f"{year:04d}{region:02d}{kai:02d}{day:02d}{r:02d}"
#                         race_ids.append(race_id)
#     return race_ids

# # メイン処理
# start_year = 1986
# end_year = 1986 # Let's just test with one year for now
# race_ids = generate_race_ids(start_year, end_year)

# all_races_data = []

# for race_id in race_ids:
#     race_data = scrape_race_results_as_array(race_id)
#     if race_data:
#         all_races_data.append({
#             "race_id": race_id,
#             "horses": race_data
#         })
#         print(f"✅ レース{race_id}のデータを取得しました。")
#     time.sleep(random.uniform(1, 3)) # netkeibaへの負荷軽減のため1秒から3秒ランダムで待機

# print("スクレイピング完了！")
# print(all_races_data[0]) # Let's take a peek at the structure
y = 0
def scrape(start, end):
    jockeys = {}
    horses = set()
    jockey_seen = set()
    races = []
    race_ids = generate_race_ids(start,end)
    # race_ids = [202406050811]
    y = 0
    for race_id in race_ids:
        r = scrape_race(jockeys, horses,race_id=race_id, jockey_seen=jockey_seen,y=y)
        if r == None:
            continue
        y+=1
    with open("Data\\jockeys.csv", "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["jockey_name", "jockey_id"])
        for name, jid in jockeys.items():
            writer.writerow([name, jid])
    
    with open("Data\\horses.csv", "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["horse_id", "name", "sex_id", "farm_id", "sire_id", "dam_id", "grandsire_id", "damsire_id"])
        for horse in horses:
            writer.writerow([
                horse.horse_id,
                horse.name,
                horse.sex_id,
                horse.farm_id,
                horse.sire_id,
                horse.dam_id,
                horse.grandsire_id,
                horse.damsire_id
            ])

    return jockeys, horses, races

def save_races_to_csv(race, jockeys, y,output_dir="Data\\races"):
    os.makedirs(output_dir, exist_ok=True)
    race_horses = race[:-1]
    result = race[-1]
    filename = os.path.join(output_dir, f"race_{y}.csv")
    with open(filename, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        i = 0
        for rh in race_horses:
            writer.writerow([
                rh.Horse.horse_id,
                rh.Horse.name,
                rh.Horse.sex_id,
                rh.Horse.farm_id,
                rh.Horse.sire_id,
                rh.Horse.dam_id,
                rh.Horse.grandsire_id,
                rh.Horse.damsire_id,
                rh.frame,
                rh.post,
                rh.jockey_id,
                rh.jockey_weight,
                rh.weight,
                rh.weight_change,
                rh.popularity,
                result[i]
            ])
            i += 1



class Horse:
    def __init__(self, horse_id, name, sex_id, farm_id=None,
                 sire_id=None, dam_id=None, grandsire_id=None, damsire_id=None):
        self.horse_id = horse_id
        self.name = name
        self.sex_id = sex_id
        self.farm_id = farm_id
        self.sire_id = sire_id
        self.dam_id = dam_id
        self.grandsire_id = grandsire_id
        self.damsire_id = damsire_id

    def __repr__(self):
        return f"{self.name} ({self.horse_id})"
    def printHorse(self):
        print(self.horse_id)
        print(self.name)
        print(self.sex_id)
        print(self.farm_id)
        print(self.sire_id)
        print(self.dam_id)
        print(self.grandsire_id)
        print(self.damsire_id)
    def __lt__(self, other):
        return self.horse_id < other.horse_id

    def __eq__(self, other):
        return self.horse_id == other.horse_id
    def __hash__(self):
        return hash(self.horse_id)

class RaceHorse:
    def __init__(self, Horse, frame, post, weight, weight_change, popularity, jockey_id, jockey_weight):
        self.Horse = Horse
        self.frame = frame
        self.post = post
        self.weight = weight
        self.weight_change = weight_change
        self.popularity = popularity
        self.jockey_id = jockey_id
        self.jockey_weight = jockey_weight

    def printhorse(self):
        print(self.Horse)
        print(self.frame)
        print(self.post)
        print(self.weight)
        print(self.weight_change)
        print(self.popularity)
        print(self.jockey_id)
        print(self.jockey_weight)
    

def extract_breeder(soup):
    rows = soup.select("table.db_prof_table tr")
    for row in rows:
        th = row.select_one("th")
        td = row.select_one("td")
        if th and "生産者" in th.text and td:
            name = td.text.strip()
            link = td.select_one("a[href*='/breeder/']")
            if link:
                breeder_id = link['href'].strip('/').split('/')[-1]
            else:
                breeder_id = None
            return breeder_id
    return None, None
def extract_lineage_ids(soup):
    pedigree = soup.select_one("table.blood_table")
    if not pedigree:
        return None, None, None, None

    # Each ancestor is in its <td>
    cells = pedigree.select("td")

    def extract_id_or_name(td):
        a = td.select_one("a[href*='/horse/']")
        if a:
            return a['href'].split('/')[3]  # e.g., '2013100011'
        return td.text.strip()  # fallback to name

    try:
        sire_id = extract_id_or_name(cells[0])
        grandsire_id = extract_id_or_name(cells[1])
        dam_id = extract_id_or_name(cells[3])
        damsire_id = extract_id_or_name(cells[4])
    except IndexError:
        print("[WARN] Not enough pedigree cells found.")
        return None, None, None, None

    return sire_id, dam_id, grandsire_id, damsire_id
def sex_to_id(sex_tag):
    if '牡' in sex_tag:
        return 1
    elif '牝' in sex_tag:
        return 0
    elif 'セ' in sex_tag:
        return 2
    return -1
def scrape_horse_lineage(horse_id, horses):
    for h in horses:
        if h.horse_id == horse_id:
            return h
    url = f"https://db.netkeiba.com/horse/{horse_id}/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers)
    res.raise_for_status()  
    soup = BeautifulSoup(res.content, "html.parser")

    name_tag = soup.select_one("div.horse_title h1")
    name = name_tag.text.strip() if name_tag else "Unknown"

    sex_tag = soup.select_one("p.txt_01")
    sex_id = sex_to_id(sex_tag.text.strip() if sex_tag else "?")
    breeder = extract_breeder(soup)
    sire_id, dam_id, grandsire_id, damsire_id = extract_lineage_ids(soup)
    horse = Horse(horse_id=horse_id, name=name, sex_id=sex_id, farm_id=breeder, sire_id=sire_id, dam_id=dam_id, grandsire_id=grandsire_id, damsire_id=damsire_id)
    horses.add(horse)
    return horse

def scrape_race(jockeys,horses, race_id, jockey_seen,y):
    url = f"https://db.netkeiba.com/race/{race_id}/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers)
    res.raise_for_status()  
    soup = BeautifulSoup(res.content, "html.parser")

    # Add new jockeys 
    jockey_links = soup.select("a[href^='/jockey/result/recent/']")
    
    for a in jockey_links:
        jockey_name = a.text.strip()
        jockey_id = a['href'].strip("/").split("/")[-1]
        if jockey_id not in jockey_seen:
            jockey_seen.add(jockey_id)
            jockeys.update({jockey_name:jockey_id})

    # Add horses into race
    horse_table = soup.select_one("table.race_table_01")
    if not horse_table:
        print(f"レース結果テーブルが見つかりませんでした: {race_id}")
        return None

    race = []
    result = []
    rows = horse_table.find_all("tr")[1:]
    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 18:
            continue

        try: a = int(cols[0].text.strip())
        except ValueError:
            continue
        horse_cell = cols[3]
        horse_link = horse_cell.select_one("a[href*='/horse/']")
        if not horse_link:
            print(f"[WARN] Horse link not found in race {race_id}")
            continue
        
        horse_id = horse_link['href'].strip('/').split('/')[-1] if horse_link else None
        horse = scrape_horse_lineage(horse_id=horse_id,horses=horses)
        frame = cols[1].text.strip()
        post = cols[2].text.strip()
        jockey_weight = cols[5].text.strip()
        h_weight = cols[14].text.strip()[:3]
        try:
            w = int(h_weight)
        except ValueError:
            continue
        weight_change = cols[14].text.strip()[4:-1]
        if(weight_change[0]== '+'):
            weight_change = weight_change[1:]
        popularity = cols[13].text.strip()
        jockey_id = jockeys[cols[6].text.strip()]
        racehorse = RaceHorse(Horse=horse, frame=frame, post=post, weight=h_weight, weight_change=weight_change,popularity=popularity, jockey_id=jockey_id, jockey_weight=jockey_weight)
        try:
            result.append(int(cols[0].text.strip()))
        except ValueError:
            print(f"[WARN] Could not convert result to int in race {race_id}")

        race.append(racehorse)
    race.append(result)
    # print(race[-1])
    save_races_to_csv(race,jockeys,y)
    print(f"✅ レース{race_id}のデータを取得しました。")
    time.sleep(random.uniform(1, 3)) # netkeibaへの負荷軽減のため1秒から3秒ランダムで待機

def generate_race_ids(start_year, end_year):
    race_ids = []
    for year in range(start_year, end_year + 1):
        for region in range(1, 11):  # 競馬場は10箇所
            for kai in range(1, 6):  # 開催回数は最大5回
                for day in range(1, 13):  # 開催日数は最大12日
                    for r in range(1, 13):  # レース数は最大12レース
                        race_id = f"{year:04d}{region:02d}{kai:02d}{day:02d}{r:02d}"
                        race_ids.append(race_id)
    return race_ids


scrape(1986,2025)