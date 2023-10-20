from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

# custom javascript to scroll page to given element
def scroll_to(driver: WebDriver, element : WebElement):
    driver.execute_script("arguments[0].scrollIntoView(true);", element)