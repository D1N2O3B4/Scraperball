from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

import os
import sys

# custom javascript to scroll page to given element
def scroll_to(driver: WebDriver, element : WebElement):
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    
    
def resource_path(file):
    data_dir = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(data_dir, file)