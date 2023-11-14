from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

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


def data_blueprint():
    return {
        "home": "",
        "away": "",
        "league": "",
        'hf': 0,
        'lh': 0,
        'af': 0,
        'la': 0,
        '3h': 0,
        '3w': 0,
        'h': '-',
        'a': '-',
        'hh': 0,
        'ha': 0,
        'h2h': 0,
        'h2a': 0,
        'fm': 0,
        '5h': [0, 0],
        '5a': [0, 0],
        'l3h': [0, 0],
        'l3a': [0, 0],
        'h%': 0,
        'a%': 0,
        'gd': 0
    }
