from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import UnexpectedAlertPresentException, NoAlertPresentException, StaleElementReferenceException


import pandas as pd
import time
import traceback

# custom Libraries
from details import getMatchDetails
from generator import generate
from utils import scroll_to, resource_path


# connecting to the selenium webdriver and opening url

DRIVER_PATH = resource_path('geckodriver')

service = Service(DRIVER_PATH, log_output="myapp.log")
firefox_options = Options()
firefox_options.add_argument('--headless')
driver = webdriver.Firefox(firefox_options, service=service)
driver.maximize_window()
driver.implicitly_wait(10)
driver.get('https://free.nowgoal.ltd/Free/FreeSoccer?tv=false')


# initialise all columns as lists
# put lists in a dictionary and convert into a pandas dataframe

stats = {
    "league": [],
    "home": [],
    "away": [],
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
    "GD": []
}


def append_to_stats(data):
    for key in stats.keys():
        stats[key].append(data[str(key).lower()])


# mute site
def mute_site():  
    driver.find_element(By.CSS_SELECTOR, "li .filterLi:first-child").click()
    driver.find_element(By.CSS_SELECTOR, 'select [name="selectsound"] option:last-child').click()
    driver.find_element(By.CSS_SELECTOR, ".sotit .cc a").click()
    
try:
    mute_site()
except:
    print("couldn't mute")
    pass


def configure_matches():
    # toggling the simplified mode
    driver.find_element(
        By.CSS_SELECTOR, '[value="/free/FreeSoccer/?type=simply"]').click()

    # sorting matches by leagues
    driver.find_element(By.CSS_SELECTOR, '[value="league"]').click()

configure_matches()

# delay so everything gets loaded
time.sleep(2)

# get table with matches in rows
# table = driver.find_element(By.ID, "table_live")
# rows = table.find_elements(By.TAG_NAME, "tr")
rows = driver.find_elements(By.CSS_SELECTOR, "#table_live tr")

# get reference to the current window
parent_window = driver.current_window_handle

i = 0

# loops through each row that has match info
# clicks on the details link to navigate to the match details page

# for row in rows:
# for j in range(len(rows)):
j = 0
while j < len(rows): 
    row = rows[j]
    # print(row.id)
    # check if alert appears and dismiss it
    try:
        alert = driver.switch_to.alert
        alert.dismiss()
        time.sleep(5)
    except NoAlertPresentException as e:
        pass

    try:
        if not row.is_displayed():
            j += 1
            continue

        if row.find_element(By.CSS_SELECTOR, "td").get_attribute("class") == "text-info":
            j += 1
            continue

        row_class = row.get_attribute('class')
        if row_class == "scoretitle":
            j += 1
            continue

        # get league title, home and away teams
        if row_class == "Leaguestitle fbHead":
            league_title = row.find_element(By.CSS_SELECTOR, "a")
            league_name = league_title.text
            j += 1
            continue

        home_team = row.find_element(
            By.CSS_SELECTOR, ".status + td > a:last-child")
        home_name = home_team.text

        away_team = row.find_element(
            By.CSS_SELECTOR, ".f-b + td > a:first-child")
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

        # loop through each window and switch to the most recently opened tab (match details tab)
        for window in windows:
            if window != parent_window:
                try:
                    driver.switch_to.window(window)
                    driver.implicitly_wait(10)

                    print(f"{j + 1} / {len(rows)}")
                    # get match details
                    match_stats = getMatchDetails(
                        driver, home_name, away_name, league_name)

                    # enlist match details
                    append_to_stats(match_stats)

                except Exception as e:
                    print(e)
                    traceback.print_exc()

                # close match details tab and switch driver back to home page
                driver.close()
                driver.switch_to.window(parent_window)

        j += 1
            
        i += 1
        # if i >= 5:
        #     # time.sleep(10)
        #     break

    except StaleElementReferenceException as e:
        # print(e.msg)
        driver.refresh()
        rows = driver.find_elements(By.CSS_SELECTOR, "#table_live tr")
        continue
        

    except Exception as e:
        print('exception')
        # print(e)
        # traceback.print_stack()


try:
    df = pd.DataFrame(stats)

    # place collected info into excel sheet provided
    generate(df)

except Exception as e:
    print(e)

# Stop program
driver.quit()
