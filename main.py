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
from utils import scroll_to, resource_path, get_cols

from bs_scraper import get_data


# connecting to the selenium webdriver and opening url

DRIVER_PATH = resource_path('geckodriver')

service = Service(DRIVER_PATH, log_output="myapp.log")
firefox_options = Options()
firefox_options.set_preference("media.volume_scale", "0.0")
firefox_options.add_argument('--headless')
driver = webdriver.Firefox(firefox_options, service=service)
driver.maximize_window()
# driver.implicitly_wait(5)
driver.get('https://free.nowgoal.ltd/Free/FreeSoccer?tv=false')


# initialise all columns as lists
# put lists in a dictionary and convert into a pandas dataframe

stats = get_cols()


def append_to_stats(data):
    for key in stats.keys():
        stats[key].append(data[str(key).lower()])
    
count = 0
def configure_matches():
    global count
    count += 1
    try:
        el = driver.find_element(By.CSS_SELECTOR, '#ShowAllSel')
        select = Select(el)
        select.select_by_visible_text('Simplify')

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



# delay so everything gets loaded
# time.sleep(2)

def filter_rows(rows: List[WebElement]) -> list[WebElement]:
    print('processing matches...')
    filtered_rows = []
    with Progress(transient=True) as progress:
        task = progress.add_task("", total=len(rows))

        for row in rows:
            progress.update(task, advance=1)

            if len(filtered_rows) >= 10:
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

# get table with matches in rows
# explicitly wait for the table to load
table = WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.CSS_SELECTOR, "#table_live"))
)
rows = driver.find_elements(By.CSS_SELECTOR, "#table_live tr")
rows = filter_rows(rows)
# get reference to the current window
parent_window = driver.current_window_handle

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
            league_short = league_info.find_element(By.TAG_NAME, "a").text

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

            # loop through each window and switch to the most recently opened tab (match details tab)
            for window in windows:
                if window != parent_window:
                    try:
                        driver.switch_to.window(window)

                        print(f"{j + 1} / {len(rows)}")
                        # get match details

                        match_data = get_data(driver, home_name, away_name, league_title, league_short)
                        append_to_stats(match_data)

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
            rows = driver.find_elements(By.CSS_SELECTOR, "#table_live tr")
            continue


        except Exception as e:
            print("encountered an error....app will now exit")
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
    pass

# Stop program
driver.quit()
