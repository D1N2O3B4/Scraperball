from selenium.webdriver.common.by import By

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

from generator import generate
from utils import get_driver, scroll_to, resource_path, get_cols, filter_rows, get_for, append_all

from bs_scraper import get_data
from match_odds import get_match_odds


driver = get_driver()

parent_window = driver.current_window_handle

stats = get_cols()



    
count = 0
def configure_matches():
    global count
    count += 1
    try:
        el = driver.find_element(By.CSS_SELECTOR, '#OrderSel')
        select = Select(el)
        select.select_by_visible_text('By time')
    except:
        if count < 10:
            configure_matches()
        else:
            print('something went wrong, retrying...')
            driver.quit()
            
            
configure_matches()

table = WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.CSS_SELECTOR, "#table_live"))
)
rows = driver.find_elements(By.CSS_SELECTOR, "#table_live tr")
rows = filter_rows(rows)

i = 0

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
        except NoAlertPresentException as e:
            pass

        try:
            row_id = row.get_attribute('id')

            _id = row_id.split("_")[1]

            league_info = row.find_element(By.CLASS_NAME, "black-down")
            league_title = league_info.get_attribute("title")

            home_team = row.find_element(By.ID, f"team1_{_id}")
            home_name = home_team.text

            away_team = row.find_element(By.ID, f"team2_{_id}")
            away_name = away_team.text

            actions = ActionChains(driver)

            link = row.find_element(By.CSS_SELECTOR, ".toolimg > .analyze-icon")
            scroll_to(driver, link)
            link.click()

            driver.switch_to.window(parent_window)

            link2 = row.find_element(By.CSS_SELECTOR, ".toolimg > .odds-icon")
            scroll_to(driver, link2)
            link2.click()


            windows = driver.window_handles
            match_data = None
            match_odds = None
            
            def contains_title(driver):
                title = driver.title
                # print("title", title)
                return 'Analysis' in title or 'Odds' in title

            print(f"{j + 1} / {len(rows)}")
            print(f"{home_name} vs {away_name}")

            for window in windows:
                if window != parent_window:
                    try:
                        driver.switch_to.window(window)
                        # WebDriverWait(driver, 10).until(lambda:
                        #     EC.title_contains('Analysis') or EC.title_contains('Odds'))

                        WebDriverWait(driver, 10).until(contains_title)

                        title = driver.title
                        # print(title)

                        if 'analysis' in title.lower():
                            match_data = get_data(driver, home_name, away_name, league_title)
                        if 'odds' in title.lower():
                            match_odds = get_match_odds(driver)
                            pass

                    except Exception as e:
                        match_data = None
                        match_odds = None
                        print('match skipped!!! - contact support team')
                        # print('match_data', 'match odds')
                        # print(e)
                        break
                        
                    finally:
                        driver.close()
                        driver.switch_to.window(parent_window)
                                   
            try:
                if not (match_data is None or match_odds is None):
                    stats = append_all(stats, match_data, match_odds)
                    
            except Exception as e:
                # print('append')
                # print(e)
                pass

            

            j += 1

        except StaleElementReferenceException as e:
            # print(e.msg)
            driver.refresh()
            time.sleep(5)
            configure_matches()
            rows = driver.find_elements(By.CSS_SELECTOR, "#table_live tr")
            rows = filter_rows(rows)
            continue


        except Exception as e:
            # print(e)
            # print("encountered an error....app will now exit")
            print('Match skipped!!! - contact support team')
            # driver.quit()
            # exit()

            # traceback.print_stack()
            pass

end = time.time()

print(f'total runtime = {end - start} seconds')

# print the length of all the values in stats with their keys
# for key in stats.keys():
    # print(f'{key} = {len(stats[key])}')

try:
    df = pd.DataFrame(stats)
    # print(df)
    generate(df)

except Exception as e:
    # print(e)
    print("couldn't generate excel, please try again or contact support!")
    # traceback.print_stack()
    pass

driver.quit()
