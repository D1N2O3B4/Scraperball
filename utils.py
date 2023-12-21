from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from typing import List
from rich.progress import Progress
from selenium.webdriver.common.by import By




import os
import sys


def get_driver():
    DRIVER_PATH = resource_path('geckodriver')
    try:
        service = Service(DRIVER_PATH, log_output="myapp.log")
        firefox_options = Options()
        firefox_options.set_preference("media.volume_scale", "0.0")
        firefox_options.set_preference("network.image.imageBehavior", "2")
        firefox_options.set_preference("permissions.default.image", 2)
        firefox_options.set_preference("browser.chrome.site_icons", False) 
        firefox_options.set_preference("editor.use_css", False)
        firefox_options.set_preference("dom.ipc.plugins.enabled.libflashplayer.so", False)
        firefox_options.set_preference("permissions.default.stylesheet", 2)
        firefox_options.set_preference("browser.display.show_image_placeholders", False)
        firefox_options.add_argument('--headless')
        driver = webdriver.Firefox(firefox_options, service=service)
        driver.maximize_window()
        driver.get('https://free.nowgoal.ltd/Free/FreeSoccer?tv=false')
        return driver
    except Exception as e:
        
        print("something went wrong, program will now exit")
        exit()



def scroll_to(driver: WebDriver, element: WebElement):
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    return


def resource_path(file):
    data_dir = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(data_dir, file)

def to_2_dec(num):
    num = f"{round(float(num), 2)}"
    dec = num.split('.')[1]
    length = len(dec)
    if length >= 2:
        return num
    return num + "0"


def get_cols():
    return {
        "League": [],
        "Home": [],
        "Away": [],
        "HF": [],
        "AF": [],
        "3H": [],
        "3W": [],
        "H": [],
        "A": [],
        "LH": [],
        "LA": [],
        "HH": [],
        "H2H": [],
        "HA": [],
        "H2A": [],
        "FM": [],
        "5A": [],
        "5H": [],
        "L3H": [],
        "L3A": [],
        "H%": [],
        "A%": [],
        "GD": [],
        "Hand": [],
        "O-O": [],
        "L-O": [],
        "Diff": [],
        "Hand2": [],
        "HT Odds": [],
        "TGO": [],
        "LO2": [],
        "Diff2": [],
        "TG": [],
        "TG-HT": [],
        "TG-2H": [],
        "BF" : [],
        "Res": [],
        "Bet": []
    }


    
    
def filter_rows(rows: List[WebElement]) -> list[WebElement]:
    print('processing matches...')
    filtered_rows = []
    # with Progress(transient=True) as progress:
        # task = progress.add_task("", total=len(rows))

    for row in rows:
        # progress.update(task, advance=1)
        if len(filtered_rows) >= 20:
            # break
            pass
        try:
            if not row.is_displayed():
                continue
            
            
            row_id = row.get_attribute('id')
            if "tr1" not in row_id:
                continue
            if row.find_element(By.CSS_SELECTOR, "td").get_attribute("class") == "text-info":
                continue
            
            row_class = row.get_attribute('class')
            if row_class == "scoretitle" or row_class == "notice":
                continue
        except Exception as e:
            # print(e)
            pass
        
        filtered_rows.append(row)
    print('matches processed')
    return filtered_rows



def append_to_stats(stats, data):
    for key in stats.keys():
        if key in data.keys():
            stats[key].append(data[str(key)])
    return stats



def get_for(match_data):
    if match_data['HF'] != '' and match_data['AF'] != '':
        an = match_data['HF']*(40) - match_data['AF']*(40)
    else:
        an = 0
    ao = 1 if an > 0.01 else 0

    if match_data['3H'] != '' and match_data['3W'] != '':
        ap = match_data['3H']*50 - match_data['3W']*50
    else:
        ap = 0
    aq = 1 if ap > 0.01 else 0

    if match_data['HH'] != '':
        ar = 1 if match_data["HH"] > 0.51 else 0
    else:
        ar = 0
    
    if match_data['H2H'][0] != '':
        as_ = 1 if match_data["H2H"][0] > 0.34 else 0
    else:
        as_ = 0

    if match_data['HH'] != '' and match_data['HA'] != '' and match_data['H2H'][0] != '' and match_data['H2A'] != '':
        at = (match_data["HH"]*20 + match_data["HA"]*10 + match_data["H2H"][0] *30 + match_data["H2A"] *10)
    else:
        at = 0
        
    if match_data['FM'] != '':
        au = match_data["FM"] * 2
    else:
        au = 0
    av = 1 if au > 0.01 else 0

    if match_data['GD'] != '':
        aw = match_data["GD"] * 2
    else:
        aw = 0
    ax = 1 if aw > 0.01 else 0
    
    if match_data['LH'] != '' and match_data['LA'] != '':
        ay = (match_data["LH"] - match_data["LA"]) * -1
    else:
        ay = 0
    for_ = an + ap + at + au + aw + ay
    return for_


def append_all(stats, match_data, match_odds, home_away):
    try:
        stats_copy = append_to_stats(stats, match_data)
        stats_copy = append_to_stats(stats, match_odds)
        opening_odds = match_odds['O-O']
        odds_movement = match_odds['Diff']
        h2h = match_data['H2H']
        l3h = match_data['L3H'][0]
        l3a = match_data['L3A'][0]
        hand = match_odds['Hand']
        bf = [0, 5]

        if opening_odds != '':
            if float(opening_odds) < 1.95:
                bf[0] += 1
        else:
            bf[1] -= 1

        if odds_movement != '':
            if int(odds_movement) >= 0:
                bf[0] += 1
        else: 
            bf[1] -= 1

        if h2h[0] != '':
            # print(h2h)
            point = h2h[0]
            score = h2h[1]
            diff = score[0] - score[1]
            if hand != '' and home_away[0] != '' and home_away[1] != '':
                hand = float(hand)
                # if hand <= 0:
                if float(home_away[0] <= home_away[1]):
                    if diff >= abs(hand):
                         bf[0] += 1
                else:
                    if abs(diff) <= abs(hand):
                        bf[0] += 1
            else:
                if diff >= 0:
                    bf[0] += 1
           
        else:
            bf[1] -= 1

        if l3h != '' and l3a != '':
            if hand != '' and home_away[0] != '' and home_away[1] != '':
                hand = float(hand)
                # if hand <= 0:
                if float(home_away[0] <= home_away[1]):
                    if round(l3h - l3a) >= abs(hand):
                        bf[0] += 1
                else:
                    if round(abs(l3h - l3a)) < abs(hand):
                        bf[0] += 1
            else:
                if l3h - l3a >= 0:
                    bf[0] += 1
        else:
            bf[1] -= 1

        for_ = get_for(match_data)

        if for_ >= 50:
            bf[0] += 1


        stats_copy['BF'].append(bf)

        banker_bet = int((bf[0]/bf[1]) * 100)
        # stats_copy['Bet'].append(for_)
        if banker_bet == 100:
            stats_copy["Bet"].append("H10")
        elif banker_bet == 0:
            stats_copy["Bet"].append("A10")
        else:
            stats_copy["Bet"].append("")


        if for_ > 89:
            stats_copy['Res'].append('SHW')
        elif for_ > 49:
            stats_copy['Res'].append('MHW')
        elif for_ > 19:
            stats_copy['Res'].append('D')
        elif for_ > -14:
            stats_copy['Res'].append('MAW')
        else:
            stats_copy['Res'].append('SAW')
        return stats_copy
    except Exception as e:
        print('unable to append data...continuing...')
        # print(e)
        return stats