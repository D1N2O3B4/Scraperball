from bs4 import BeautifulSoup, Tag

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By


def get_cols():
    return {
        'Hand': 0,
        'O-O': 0,
        'L-O': 0,
        'Diff': 0,
        "Hand2": 0,
        'HT Odds': 0,
        'TGO': 0,
        'LO2': 0,
        'Diff2': 0,
        'TG': 0,
        'TG-HT': 0,
        'TG-2H': 0
    }


def configure(driver: WebDriver):
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((
            By.CSS_SELECTOR, '#CompanyOddsDiv table tr .odd_a')))

    changes_rows = driver.find_elements(
        By.CSS_SELECTOR, '#CompanyOddsDiv table tr')

    changes = [row for row in changes_rows if "title" not in row.get_attribute(
        'class').lower()]
    bet365 = [row for row in changes if row.find_element(
        By.CSS_SELECTOR, 'td').text.lower() == "bet365"][0]

    button = bet365.find_element(By.CSS_SELECTOR, '.odd_a')
    button.click()

    WebDriverWait(driver, 10).until(EC.visibility_of_element_located(
        (By.CSS_SELECTOR, ".popinfo #detailtable")))


def extract_live(table_body: Tag):
    live_odds = []
    rows = table_body.select('tr')[2:]
    rows_reversed = rows[::-1]

    for row in rows_reversed:
        data = row.select('td')
        if len(data) < 6:
            continue

        live = data[0].get_text().strip()
        home = data[2].get_text().strip()
        handicap = data[3].get_text().strip()
        away = data[4].get_text().strip()

        if live == 'Live':
            live_odds.append([live, home, handicap, away])
        else:
            break
    return live_odds
    pass


def get_handicap(handicap: str):
    neg = False
    if '-' in handicap:
        handicap = handicap.replace('-', '')
        neg = True

    split = handicap.split('/')
    if len(split) == 1:
        if neg:
            return float(split[0]) * -1
        return float(split[0])

    hand = float(split[0]) + float(split[1])
    if neg:
        hand = hand * -1
    return hand/2


def get_movement(odds: list):
    movement = 0
    start_odds = float(odds[0][1])
    end_odds = float(odds[-1][1])
    movement = int(end_odds * 100) - int(start_odds * 100)
    return movement


def get_live_odds(odds_data: list):
    prev = odds_data[0]
    # transition = [0, [ah_live[0]]]
    transition = {
        'diff': 0,
        'movement': 0,
        'odds': [odds_data[0]],
        'range': ''
    }
    for i in range(len(odds_data)):
        if i == 0:
            continue
        live = odds_data[i]

        if live[2] == prev[2]:
            transition['odds'].append(live)
            transition['movement'] = get_movement(transition['odds'])
            prev = live
        else:

            prev_handicap = get_handicap(transition['odds'][-1][2])
            live_handicap = get_handicap(live[2])
            if prev_handicap > live_handicap:
                transition['diff'] += transition['movement'] + 1
            else:
                transition['diff'] += transition['movement'] - 1
            transition['movement'] = 0
            transition['odds'] = [live]
            transition['range'] = f"{prev_handicap * -1} - {live_handicap * -1}"
            prev = live

    transition['diff'] += transition['movement']
    # print(transition)
    opening = f"{round(1 + float(odds_data[0][1]), 2)}"
    closing = f"{round(1 + float(odds_data[-1][1]), 2)}"
    hand_goal = f"{get_handicap(odds_data[0][2]) * -1}"
    return opening, closing, f"{transition['diff']}", hand_goal, f"{transition['range']}"
