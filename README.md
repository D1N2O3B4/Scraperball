# Scraperball
A webscrapper built to scrape football match details.

## Requirements
- Python 3.9 or above
- Mozilla firefox (Will need some configuration before using a different browser such as Chrome)
- Gecko Driver (comes with the script, should also be in the same folder as the main script)
- MyFile-decrypted.xlsx

## External Python Libraries used
- Selenium
- Pandas
- Openpyxl

## How to Run
- open up a terminal
- type "pip install selenium pandas openpyxl" and press Enter
- make sure the "MyFile-decrypted.xlsx" Excel file is in the same folder as the main script
- type "python main.py" or "python3 main.py" depending on how python is stored in your PATH

## Results
- A folder called "output" should be created in the same directory if it doesn't already exist
- An excel file saved as the current date and time should be added to the output folder
