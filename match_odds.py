from bs4 import BeautifulSoup as bs

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By

from time import sleep
# from bs_scraper_utils import select

handicap_definitions = {
    '0': 0,
    '0/0.5': 0.25,
    '0.5': 0.5,
    '0.5/1': 0.75,
    '1':1,
    '1/1.5':1.25,
    '1.5':1.5,
    '1.5/2':1.75,
    '2':2,
    '2/2.5':2.25,
    '2.5':2.5,
}

def get_match_odds(driver:WebDriver):
    try:
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((
                By.CSS_SELECTOR, '#CompanyOddsDiv table tr .odd_a')))
        
        changes_rows = driver.find_elements(By.CSS_SELECTOR, '#CompanyOddsDiv table tr')
        
        changes = [row for row in changes_rows if "title" not in row.get_attribute('class').lower()]
        bet365 = [row for row in changes if row.find_element(By.CSS_SELECTOR, 'td').text.lower() == "bet365"][0]
        # for change in changes:
            # print(change.find_element(By.TAG_NAME, 'td').text)
        # bet365 = [row for row in changes if row.find_element(By.CSS_SELECTOR, 'td').text.lower() == "bet365"][0]

        button = bet365.find_element(By.CSS_SELECTOR, '.odd_a')
        button.click()
        
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".popinfo #detailtable")))

        
        html = driver.page_source
        soup = bs(html, 'lxml')
        # print(soup.prettify())
        odds_table = soup.select('.popinfo #detailtable table tbody')
        
        ah = odds_table[0]
        op = odds_table[1]
        ou = odds_table[2]
        
        # print(ah)
        ah_rows = ah.select('tr')[2:]
        # print(ah_rows[-1].prettify())
        
        # iterate over ah_rows in reverse
        for i in range(len(ah_rows)-1, -1, -1):
            row = ah_rows[i]
            data = row.select('td')
            live = data[0].get_text().strip()
            home = data[2].get_text().strip()
            handicap = data[3].get_text().strip()
            away = data[4].get_text().strip()
            
            if i == len(ah_rows)-1:
                print(live, home, handicap, away)
                continue
        
        # print(op)
        # print(ou)
        
    except Exception as e:
        print(e)
    sleep(5)
    pass