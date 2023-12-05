from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoAlertPresentException, StaleElementReferenceException
from selenium.webdriver.support.select import Select
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from typing import List

from rich.progress import track, Progress



import pandas as pd
import time
import traceback

# custom Libraries
# from details import getMatchDetails
from generator import generate
from utils import scroll_to, resource_path, get_cols, filter_rows

from bs_scraper import get_data
from match_odds import get_match_odds


# connecting to the selenium webdriver and opening url

DRIVER_PATH = resource_path('geckodriver')
try:
    service = Service(DRIVER_PATH, log_output="myapp.log")
    firefox_options = Options()
    firefox_options.set_preference("media.volume_scale", "0.0")
    firefox_options.add_argument('--headless')
    driver = webdriver.Firefox(firefox_options, service=service)
    driver.maximize_window()
    # driver.implicitly_wait(5)
    driver.get('https://free.nowgoal.ltd/Free/FreeSoccer?tv=false')
except Exception as e:
    print("something went wrong, program will now exit")
    exit()
parent_window = driver.current_window_handle


# initialise all columns as lists
# put lists in a dictionary and convert into a pandas dataframe

stats = get_cols()


def append_to_stats(data):
    for key in stats.keys():
        if key in data.keys():
            stats[key].append(data[str(key)])
    
count = 0
def configure_matches():
    global count
    count += 1
    try:
        # el = driver.find_element(By.CSS_SELECTOR, '#ShowAllSel')
        # select = Select(el)
        # select.select_by_visible_text('Simplify')

        # sorting matches by leagues
        el = driver.find_element(By.CSS_SELECTOR, '#OrderSel')
        select = Select(el)
        # select.select_by_visible_text('By league')
        select.select_by_visible_text('By time')
    except:
        if count < 10:
            configure_matches()
        else:
            print('something went wrong, retrying...')
            driver.quit()
            
            
configure_matches()

# get table with matches in rows
# explicitly wait for the table to load
table = WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.CSS_SELECTOR, "#table_live"))
)
rows = driver.find_elements(By.CSS_SELECTOR, "#table_live tr")
rows = filter_rows(rows)
# get reference to the current window

i = 0

# loops through each row that has match info
# clicks on the details link to navigate to the match details page

# start timer
start = time.time()
j = 0
print("fetching match details...")
print("this may take a while")
with Progress(transient=True) as progress:
    task = progress.add_task("", total=len(rows))
    while j < len(rows): 
        progress.update(task, advance=1)
        row = rows[j]
        try:
            alert = driver.switch_to.alert
            alert.dismiss()
            # time.sleep(5)
        except NoAlertPresentException as e:
            pass

        try:
            row_id = row.get_attribute('id')

            _id = row_id.split("_")[1]

            league_info = row.find_element(By.CLASS_NAME, "black-down")
            league_title = league_info.get_attribute("title")
            # league_short = league_info.find_element(By.TAG_NAME, "a").text

            home_team = row.find_element(By.ID, f"team1_{_id}")
            home_name = home_team.text

            away_team = row.find_element(By.ID, f"team2_{_id}")
            away_name = away_team.text

            actions = ActionChains(driver)

            # gets match details link button
            link = row.find_element(By.CSS_SELECTOR, ".toolimg > .analyze-icon")

            # scroll to make button visible on the page
            scroll_to(driver, link)

            # click to navigate to match details page
            actions.click(link).perform()
            actions.reset_actions()

            # get list of tabs opened by the driver
            windows = driver.window_handles
            match_data = None
            match_odds = None

            # loop through each window and switch to the most recently opened tab (match details tab)
            for window in windows:
                if window != parent_window:
                    try:
                        driver.switch_to.window(window)

                        print(f"{j + 1} / {len(rows)}")
                        print(f"{home_name} vs {away_name}")
                        # get match details

                        match_data = get_data(driver, home_name, away_name, league_title)
                        # append_to_stats(match_data)

                    except Exception as e:
                        print('match skipped!!! - contact support team')
                        # print(str(e))
                        # traceback.print_stack()
                        
                    

                    # close match details tab and switch driver back to home page
                    driver.close()
                    driver.switch_to.window(parent_window)
            
            # getting odds data
            # gets match odds link button
            link2 = row.find_element(By.CSS_SELECTOR, ".toolimg > .odds-icon")

            # scroll to make button visible on the page
            scroll_to(driver, link2)

            # click to navigate to match details page
            actions.click(link2).perform()
            actions.reset_actions()

            windows2 = driver.window_handles

            for window in windows2:
                if window != parent_window:
                    try:
                        driver.switch_to.window(window)

                        # print(f"")
                        # get match details

                        match_odds = get_match_odds(driver)
                        # print(match_odds)
                        if match_data is not None and match_odds is not None:
                            append_to_stats(match_data)
                            append_to_stats(match_odds)
                            # calculating banker bet
                            opening_odds = match_odds['O-O']
                            odds_movement = match_odds['Diff']
                            h2h = match_data['H2H']
                            l3h = match_data['L3H'][0]
                            l3a = match_data['L3A'][0]
                            bf = [0, 5]
                            # print(type(odds_movement), type(opening_odds), type(h2h), type(l3h), type(l3a))
                            # print(odds_movement, opening_odds, h2h, l3h, l3a)

                            if float(opening_odds) < 1.95:
                                bf[0] += 1
                            if int(odds_movement) >= 0:
                                bf[0] += 1
                            if h2h > 0.67:
                                bf[0] += 1
                            if (l3h - l3a) > 0:
                                bf[0] += 1
                                
                            an = (match_data['HF']*40) - (match_data['AF']*40)
                            ao = 1 if an > 0.01 else 0
                            ap = (match_data['3H']*50) - (match_data['3W']*50)
                            aq = 1 if ap > 0.01 else 0
                            ar = 1 if match_data["HH"] > 0.51 else 0
                            as_ = 1 if match_data["H2H"] > 0.34 else 0
                            at = (match_data["HH"]*20) + (match_data["HA"]*10) + (match_data["H2H"] *30) + (match_data["H2A"] *10)
                            au = (match_data["FM"] * 2)
                            av = 1 if au > 0.01 else 0
                            aw = match_data["GD"] * 2
                            ax = 1 if aw > 0.01 else 0
                            ay = (match_data["LH"] - match_data["LA"]) * -1
                            
                            # add the above
                            for_ = an + ap + at + au + aw + ay
                            
                            if for_ >= 50:
                                bf[0] += 1
                            
                            
                            stats['BF'].append(bf)
                            
                            if for_ > 89:
                                stats['Res'].append('SHW')
                            elif for_ > 49:
                                stats['Res'].append('MHW')
                            elif for_ > 19:
                                stats['Res'].append('D')
                            elif for_ > -14:
                                stats['Res'].append('MAW')
                            else:
                                stats['Res'].append('SAW')
                            
                            

                    except Exception as e:
                        print('match skipped!!! - contact support team')
                        # print(e)
                        # traceback.print_stack()
                        pass

                    # close match details tab and switch driver back to home page
                    driver.close()
                    driver.switch_to.window(parent_window)            
            

            j += 1

        except StaleElementReferenceException as e:
            # print(e.msg)
            driver.refresh()
            time.sleep(5)
            configure_matches()
            rows = driver.find_elements(By.CSS_SELECTOR, "#table_live tr")
            continue


        except Exception as e:
            # print("encountered an error....app will now exit")
            # driver.quit()

            # print(e)
            # traceback.print_stack()
            pass

# end timer
end = time.time()

print(f'total runtime = {end - start} seconds')

try:
    df = pd.DataFrame(stats)
    # print(df)
    # place collected info into excel sheet provided
    generate(df)

except Exception as e:
    # print(e)
    # traceback.print_stack()
    pass

# Stop program
driver.quit()
