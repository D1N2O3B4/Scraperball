from bs4 import BeautifulSoup as bs

from selenium.webdriver.remote.webdriver import WebDriver
import traceback

from time import sleep
# from bs_scraper_utils import select
from match_odds_utils import get_cols, configure, extract_live, get_live_odds


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

        ah_live = extract_live(ah)
        op_live = extract_live(op)
        ou_live = extract_live(ou)
        if len(ah_live) > 0:
            cols['O-O'], cols['L-O'], cols['Diff'], cols['Hand'], cols["Hand2"] = get_live_odds(
                ah_live)
        if len(ou_live) > 0:
            cols['TGO'], cols['LO2'], cols['Diff2'], cols['TG'], dummy = get_live_odds(
                ou_live)
            
        return cols
    
    except Exception as e:
        print(e)
        traceback.print_stack()
    pass
