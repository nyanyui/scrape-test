import requests
from bs4 import BeautifulSoup
import pandas as pd

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
def sex_to_id(sex):
    if sex=='牡':
        return 1
    elif sex=='牝':
        return 0
    return -1
def scrape_horse_lineage(horse_id):
    url = f"https://db.netkeiba.com/horse/{horse_id}/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers)
    res.raise_for_status()  
    soup = BeautifulSoup(res.content, "html.parser")

    name_tag = soup.select_one("div.horse_title h1")
    name = name_tag.text.strip() if name_tag else "Unknown"

    sex_tag = soup.select_one("p.txt_01")
    sex_id = sex_to_id(sex_tag.text.strip()[3] if sex_tag else "?")
    breeder = extract_breeder(soup)
    sire_id, dam_id, grandsire_id, damsire_id = extract_lineage_ids(soup)

    return Horse(horse_id=horse_id, name=name, sex_id=sex_id, farm_id=breeder, sire_id=sire_id, dam_id=dam_id, grandsire_id=grandsire_id, damsire_id=damsire_id)

