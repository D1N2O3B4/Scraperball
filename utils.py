from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from typing import List
from rich.progress import Progress
from selenium.webdriver.common.by import By




import os
import sys

# custom javascript to scroll page to given element


def scroll_to(driver: WebDriver, element: WebElement):
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    return


def resource_path(file):
    data_dir = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(data_dir, file)


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
        "BF" : []
    }


def data_blueprint():
    return {
        "Home": "",
        "Away": "",
        "League": "",
        'HF': 0,
        'LH': 0,
        'AF': 0,
        'LA': 0,
        '3H': 0,
        '3W': 0,
        'H': '-',
        'A': '-',
        'HH': 0,
        'HA': 0,
        'H2H': 0,
        'H2A': 0,
        'FM': 0,
        '5H': [0, 0],
        '5A': [0, 0],
        'L3H': [0, 0],
        'L3A': [0, 0],
        'H%': 0,
        'A%': 0,
        'GD': 0
    }
    
    
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
