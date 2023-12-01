from bs4 import BeautifulSoup as bs
# import ResultSet from beatifulsoup

from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By

import traceback

from utils import data_blueprint
from bs_scraper_utils import joinString, prepare, get_percentage, get_goals, calculate_points, calculate_team_form, get_last_goals, get_table_rows


def get_data(driver: WebDriver, home: str, away: str, league: str):
    vals = data_blueprint()

    # wait for page to load
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((
            By.CSS_SELECTOR, '#table_v1')))

    try:
        prepare(driver)
    except Exception as e:
        pass

    html = driver.page_source
    soup = bs(html, 'lxml')

    # get home and away team names
    try:
        home = soup.select_one("#fbheader .home .sclassName").get_text()
        away = soup.select_one("#fbheader .guest .sclassName").get_text()
    except Exception as e:
        print(e)
        pass

    vals['home'] = home
    vals['away'] = away
    vals['league'] = league

    print(f'{home} vs {away}')

    home_rows = get_table_rows(soup, '#table_v1 > tbody > tr', league, 1)
    home_team_form = get_last_goals(
        home_rows, team=home, num=1, home_team_match=False, is_team_form=True)

    away_rows = get_table_rows(soup, '#table_v2 > tbody > tr', league, 2)
    away_team_form = get_last_goals(
        away_rows, team=away, num=2, home_team_match=False, is_team_form=True)

    team_form = calculate_team_form(home_team_form, away_team_form)
    vals['fm'] = team_form

    home_scores = get_last_goals(
        home_rows, team=home, num=1, home_team_match=True)
    if len(home_scores) > 0:
        vals['hf'] = calculate_points(
            home_scores[:5], home_team_match=True)/(min(5, len(home_scores)) * 3)
        vals['3h'] = calculate_points(
            home_scores[:3], home_team_match=True)/(min(3, len(home_scores)) * 3)
        vals['h'] = 'W' if int(home_scores[0].split('-')[0]) > int(home_scores[0].split('-')[1]) else 'D' if int(home_scores[0].split(
            '-')[0]) == int(home_scores[0].split('-')[1]) else 'L'
        vals['5h'] = get_goals(home_scores[:5], home_team_match=True)
        vals['l3h'] = get_goals(home_scores[:3], home_team_match=True)
        vals['h%'] = get_percentage(home_scores[:5], home_team_match=True)

    away_scores = get_last_goals(
        away_rows, team=away, num=2, home_team_match=False)
    if len(away_scores) > 0:
        vals['af'] = calculate_points(
            away_scores[:5], home_team_match=False)/(min(5, len(away_scores)) * 3)
        vals['3w'] = calculate_points(
            away_scores[:3], home_team_match=False)/(min(3, len(away_scores)) * 3)
        vals['a'] = 'W' if int(away_scores[0].split('-')[0]) < int(away_scores[0].split('-')[1]) else 'D' if int(away_scores[0].split(
            '-')[0]) == int(away_scores[0].split('-')[1]) else 'L'
        vals['5a'] = get_goals(away_scores[:5], home_team_match=False)
        vals['l3a'] = get_goals(away_scores[:3], home_team_match=False)
        vals['a%'] = get_percentage(away_scores[:5], home_team_match=False)

    if len(home_scores) > 0 and len(away_scores) > 0:
        min_len = min(len(home_scores), len(away_scores), 3)

        home_goals = get_goals(
            home_scores[:min_len], home_team_match=True, gd=True)
        away_goals = get_goals(
            away_scores[:min_len], home_team_match=False, gd=True)
        vals['gd'] = home_goals - away_goals

    h2h_rows = get_table_rows(soup, '#table_v3 > tbody > tr', league, 3)
    h2h_home_scores, h2h_away_scores = get_last_goals(
        h2h_rows, home, 3, True, is_team_form=False, is_h2h=True)

    if len(h2h_home_scores) > 0:
        vals['hh'] = calculate_points(
            h2h_home_scores, home_team_match=True)/(min(5, len(h2h_home_scores)) * 3)
        vals['h2h'] = calculate_points(
            h2h_home_scores[:1], home_team_match=True)/3

    if len(h2h_away_scores) > 0:
        vals['ha'] = calculate_points(
            h2h_away_scores, home_team_match=False)/(min(5, len(h2h_away_scores)) * 3)
        vals['h2a'] = calculate_points(
            h2h_away_scores[:1], home_team_match=False)/3
    try:
        home_rank = soup.select_one(
            ".home-div tbody > tr:nth-child(3n) > td:nth-child(9n)").get_text()
        num_home_matches = soup.select_one(
            ".home-div tbody > tr:nth-child(4n) > td:nth-child(2n)").get_text()
        home_points = soup.select_one(
            ".home-div tbody > tr:nth-child(4n) > td:nth-child(8n)").get_text()

        away_rank = soup.select_one(
            ".guest-div tbody > tr:nth-child(3n) > td:nth-child(9n)").get_text()
        num_away_matches = soup.select_one(
            ".guest-div tbody > tr:nth-child(5n) > td:nth-child(2n)").get_text()
        away_points = soup.select_one(
            ".guest-div tbody > tr:nth-child(5n) > td:nth-child(8n)").get_text()
    except:
        home_rank = ''
        num_home_matches = ''
        home_points = ''

        away_rank = ''
        num_away_matches = ''
        away_points = ''

    cup_standings = {}

    try:
        # getting cup standings
        rows = soup.select("#porletP3 .team-table-other tr")
        for i, row in enumerate(rows):
            if i == 0:
                continue

            cup_rank = row.select_one('td:first-child').get_text()
            cup_team = row.select_one('td:nth-child(2n)').get_text()
            cup_matches = row.select_one('td:nth-child(3n)').get_text()
            cup_points = row.select_one('td:nth-child(9n)').get_text()

            if joinString(cup_team) == joinString(home):
                cup_standings[home] = {
                    'rank': cup_rank,
                    'matches': cup_matches,
                    'points': cup_points
                }
            if joinString(cup_team) == joinString(away):
                cup_standings[away] = {
                    'rank': cup_rank,
                    'matches': cup_matches,
                    'points': cup_points
                }
    except Exception as e:
        # print(e)
        # traceback.print_stack()
        pass

    # print(cup_standings)

    def use_cup_standings(rank: bool = False, matches: bool = False):
        # check if cup standings dict is not empty
        if len(cup_standings) < 1:
            return
        try:
            if rank:
                vals['lh'] = int(cup_standings[home]['rank'])
                vals['la'] = int(cup_standings[away]['rank'])
        except Exception as e:
            # print(e)
            pass

        try:
            if matches:
                home_matches = int(cup_standings[home]['matches'])
                away_matches = int(cup_standings[away]['matches'])
                if home_matches >= 5 and away_matches >= 5:
                    vals['hf'] = int(cup_standings[home]['points']) / \
                        (int(cup_standings[home]['matches']) * 3)
                    vals['af'] = int(cup_standings[away]['points']) / \
                        (int(cup_standings[away]['matches']) * 3)
        except Exception as e:
            # print(e)
            pass

    if home_rank != '' and away_rank != '' and home_rank.isdigit() and away_rank.isdigit():
        try:
            vals['lh'] = int(home_rank)
            vals['la'] = int(away_rank)
        except:
            vals['lh'] = 0
            vals['la'] = 0
            use_cup_standings(rank=True)
            # update this to include cup standings/groups

        use_table = False

        if num_home_matches != '' and num_away_matches != '' and num_home_matches.isdigit() and num_away_matches.isdigit():
            if int(num_home_matches) >= 5 and int(num_away_matches) >= 5:
                use_table = True
            else:
                use_cup_standings(matches=True)
                use_table = False

        if use_table:
            vals['hf'] = int(home_points) / (int(num_home_matches) * 3)
            vals['af'] = int(away_points) / (int(num_away_matches) * 3)
            pass
        # else:
            # vals['hf'] = calculate_points(home_scores[:5], home_team_match=True)/(min(5, len(home_scores)) * 3)
            # pass
    else:
        use_cup_standings(rank=True, matches=True)

    # if ranks are empty use cup_standings
    if vals['lh'] == 0 or vals['la'] == 0:
        use_cup_standings(rank=True)

    return vals
