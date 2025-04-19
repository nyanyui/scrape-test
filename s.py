import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv
import os
import time
import random
import re
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
    horses = set()
    races = []
    race_ids = generate_race_ids(start,end)
    y = 0
    for race_id in race_ids:
        r = scrape_race(horses,race_id=race_id,y=y)
        if r == None:
            continue
        y+=1
    write_horses(horses)
    print("スクレイピング完了！")
    def write_horses(horses):
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

def scrape_test(raceid):
    horses = set()
    race_ids = [raceid]
    y = 0
    for race_id in race_ids:
        r = scrape_race(horses,race_id=race_id,y=y)
        if r == None:
            continue
        y+=1

    return horses

def save_races_to_csv(race, y,output_dir="Data\\races"):
    os.makedirs(output_dir, exist_ok=True)
    race_cond = race[0]
    race_distance, race_surface, weather_score, turf_condition, dirt_condition, start_time, track_direction, racecourse_index= race_cond
    race_horses = race[1:-1]
    result = race[-1]
    filename = os.path.join(output_dir, f"race_{y}.csv")
    with open(filename, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        i = 0
        for rh in race_horses:
            writer.writerow([
                race_distance,
                race_surface,
                weather_score,
                turf_condition,
                dirt_condition,
                start_time,
                track_direction,
                racecourse_index,
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

    return normalize_horse_id(sire_id), normalize_horse_id(dam_id), normalize_horse_id(grandsire_id), normalize_horse_id(damsire_id)
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
    horse = Horse(horse_id=normalize_horse_id(horse_id), name=name, sex_id=sex_id, farm_id=breeder, sire_id=sire_id, dam_id=dam_id, grandsire_id=grandsire_id, damsire_id=damsire_id)
    horses.add(horse)
    return horse

def scrape_race(horses, race_id, y):
    url = f"https://db.netkeiba.com/race/{race_id}/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers)
    res.raise_for_status()  
    soup = BeautifulSoup(res.content, "html.parser")

    # Add horses into race
    horse_table = soup.select_one("table.race_table_01")
    if not horse_table:
        print(f"レース結果テーブルが見つかりませんでした: {race_id}")
        return None

    # Get list of jockey IDs
    jockey_links = soup.select("a[href^='/jockey/result/recent/']")
    jockeys = []
    for a in jockey_links:
        jockey_id = a['href'].strip("/").split("/")[-1]
        jockeys.append(jockey_id)

    race = []
    race_condition = get_race_condition(res)
    race.append(race_condition)
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
        jockey_id = jockeys.pop(0)
        racehorse = RaceHorse(Horse=horse, frame=frame, post=post, weight=h_weight, weight_change=weight_change,popularity=popularity, jockey_id=jockey_id, jockey_weight=jockey_weight)
        try:
            result.append(int(cols[0].text.strip()))
        except ValueError:
            print(f"[WARN] Could not convert result to int in race {race_id}")

        race.append(racehorse)
    race.append(result)
    # print(race[-1])
    save_races_to_csv(race,y)
    print(f"✅ レース{race_id}のデータを取得しました。")
    time.sleep(random.uniform(1, 3)) # netkeibaへの負荷軽減のため1秒から3秒ランダムで待機
    return y
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

def get_race_condition(res):
    res.raise_for_status()
    res.encoding = 'euc-jp'
    soup = BeautifulSoup(res.text, "html.parser")

    # Extract full info line (e.g., "芝右1800m / 天候 : 曇 / 芝 : 良 ダート : 良 / 発走 : 15:40")
    span = soup.select_one("div.data_intro span")
    if not span:
        print(f"[WARN] Could not find race info span for race {race_id}")
        return None

    text = span.text.strip().replace('\xa0', ' ').replace('　', ' ')
    
    # Initial fields
    surface = -1
    distance = -1
    weather_score = -1
    turf_condition = -1
    dirt_condition = -1
    start_time = -1
    direction = -1

    # Parse distance & surface
    dist_match = re.search(r"(芝|ダ|障)[^\d直左右]*([直左右]?)(\d+)m", text)
    if dist_match:
        surface_text = dist_match.group(1)
        direction_text = dist_match.group(2)
        distance = int(dist_match.group(3))

        surface = classify_surface(surface_text)
        direction = classify_direction(direction_text)

    # Parse weather
    weather_match = re.search(r"天候\s*:\s*(\S+)", text)
    if weather_match:
        weather_score = classify_weather(weather_match.group(1))

    # Parse track condition
    turf_condition, dirt_condition = classify_track_conditions(text)

    # Parse start time
    time_match = re.search(r"発走\s*:\s*(\d{1,2}):(\d{2})", text)
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2))
        start_time = hour * 100 + minute  # e.g., 11:15 → 1115

    racecourse_index = classify_racecourse(soup)

    return [
    distance,
    surface,
    weather_score,
    turf_condition,
    dirt_condition,
    start_time,
    direction,
    racecourse_index
    ]

def classify_track_conditions(text):
    turf_match = re.search(r"芝\s*:\s*(\S+)", text)
    dirt_match = re.search(r"ダート\s*:\s*(\S+)", text)

    turf = turf_match.group(1) if turf_match else 'None'
    dirt = dirt_match.group(1) if dirt_match else 'None'
    if turf:
        turf = turf.replace("良", "1").replace("稍重", "2").replace("重", "3").replace("不良", "4").replace('None', "0")
    if dirt:
        dirt = dirt.replace("良", "1").replace("稍重", "2").replace("重", "3").replace("不良", "4").replace('None', "0")
    return int(turf), int(dirt)
def classify_surface(distance_info: str) -> str:
    if "芝" in distance_info and "ダ" not in distance_info:
        return 1
    elif "ダ" in distance_info:
        return 2
    elif "障" in distance_info:
        return 3
    else:
        return 0
def classify_weather(text: str) -> int:
    if "雪" in text:
        return 4
    elif "雨" in text:
        return 3
    elif "曇" in text:
        return 2
    elif "晴" in text:
        return 1
    else:
        return 0  # unknown
def classify_direction(direction_char: str) -> int:
    if direction_char == "右":
        return 1
    elif direction_char == "左":
        return 2
    elif direction_char == "直":
        return 3
    else:
        return 0
def classify_racecourse(soup) -> int:
    """
    Extracts the racecourse name from the <h1> tag and maps it to a JRA index.
    Returns an integer index from 1–10, or 0 if unknown.
    """
    racecourse_map = {
        "札幌": 1,
        "函館": 2,
        "福島": 3,
        "新潟": 4,
        "東京": 5,
        "中山": 6,
        "中京": 7,
        "京都": 8,
        "阪神": 9,
        "小倉": 10
    }
    active_link = soup.select_one("ul.race_place.fc a.active")
    if active_link:
        name = active_link.text.strip()
        return racecourse_map.get(name, 0)
    return 0  # unknown
def normalize_horse_id(horse_id: str) -> str:
    """
    Converts a hexadecimal horse_id (if detected) to a decimal string.
    If already decimal, returns as-is.
    """
    try:
        if horse_id.startswith("0x") or all(c in "0123456789abcdefABCDEF" for c in horse_id):
            # Treat as hex only if non-decimal characters exist or prefix detected
            return str(int(horse_id, 16))
        else:
            return horse_id
    except ValueError:
        print(f"[WARN] Unable to convert horse_id '{horse_id}' — returning as is.")
        return horse_id
# print(normalize_horse_id('1982102220'))
# scrape(1986,2025)
print(scrape_test(199608010105))