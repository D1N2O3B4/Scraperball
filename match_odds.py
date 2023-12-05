from bs4 import BeautifulSoup as bs
from selenium.webdriver.common.by import By

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver
import traceback

from time import sleep
# from bs_scraper_utils import select
from match_odds_utils import get_cols, configure, extract_live, get_live_odds, get_handicap


def get_match_odds(driver: WebDriver):
    cols = get_cols()
    try:
        configure(driver)

        html = driver.page_source
        soup = bs(html, 'lxml')
        # print(soup.prettify())
        odds_table = soup.select('.popinfo #detailtable table tbody')

        ah = odds_table[0]
        op = odds_table[1]
        ou = odds_table[2]
        
        ou_ht = None
        try:
            driver.find_element(By.CSS_SELECTOR, "#winHTBtn").click()
            WebDriverWait(driver, 10).until(EC.staleness_of(driver.find_element(By.CSS_SELECTOR, ".popinfo #detailtable table tbody:last-child")))
            # el = driver.find_element(By.CSS_SELECTOR, ".popinfo #detailtable table tbody:last-child")
            el = driver.page_source
            el_soup = bs(el, 'lxml')
            odds_table_ = el_soup.select('.popinfo #detailtable table tbody')
            # ou_ht = bs(el.get_attribute('innerHTML'), 'lxml')
            ou_ht = odds_table_[2]
            ou_ht_live = extract_live(ou_ht)
            # print("half-time", ou_ht_live)
            if len(ou_ht_live) > 0:
                # print("half-time", ou_ht_live)
                goal_odds = ou_ht_live[0][1]
                goal_hand = ou_ht_live[0][2]
                goal_odds_to_2 = f"{round(1 + float(goal_odds), 2)}"
                
                val = f"{get_handicap(goal_hand)} {goal_odds_to_2}"
                # print(val)
                cols['TG-HT'] = val
        except Exception as e:
            # print(e)
            pass

        ah_live = extract_live(ah)
        op_live = extract_live(op)
        ou_live = extract_live(ou)
        
        if len(ah_live) > 0:
            cols['O-O'], cols['L-O'], cols['Diff'], cols['Hand'], cols["Hand2"] = get_live_odds(
                ah_live)
        if len(ou_live) > 0:
            cols['TGO'], cols['LO2'], cols['Diff2'], cols['TG'], dummy = get_live_odds(
                ou_live, True)
            
        return cols
    
    except Exception as e:
        # print(e)
        # traceback.print_stack()
        pass
