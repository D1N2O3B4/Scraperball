from bs4 import BeautifulSoup as bs
# import ResultSet from beatifulsoup
from bs4.element import ResultSet, Tag

from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
import traceback

from utils import scroll_to, data_blueprint



def select(driver: WebDriver, selector: str):
    try:
        select = driver.find_element(By.CSS_SELECTOR, selector)
        scroll_to(driver, select)
        select.click()

    except Exception as e:
        # print(traceback.format_exc())
        pass
    pass


def prepare(driver: WebDriver):
    # click checkboxes
    select(driver, "#checkboxleague1")
    select(driver, "#selectMatchCount1 > option:last-child")

    select(driver, "#checkboxleague2")
    select(driver, "#selectMatchCount2 > option:last-child")

    select(driver, "#checkboxleague3")
    select(driver, "#selectMatchCount3 > option:last-child")


def get_table_rows(soup: bs, selector: str):
    rows = soup.select(selector)
    return rows


def get_last_goals(rows: ResultSet[Tag], team: str, num: int, home_team_match: bool, is_team_form=False, is_h2h=False):
    home_scores = []
    away_scores = []
    for row in rows:
        # print(row.attrs['id'])
        try:
            id = row['id']
            # print(id, f"tr{num}")
            if f"tr{num}" not in id:
                # print("true")
                continue
        except KeyError as e:
            continue
        # print("style", row.attrs['style'])
        if "none" in row.attrs['style']:
            # print('none')
            continue

        home_team = row.select_one("td:nth-child(3n)").get_text()
        away_team = row.select_one("td:nth-child(5n)").get_text()
        match_scores = row.select_one(
            f"td:nth-child(4n) > .fscore_{num}").get_text()

        # [home_score, away_score] = [int(score) for score in match_scores.split('-')]

        # if home_team_match:

        if is_team_form or is_h2h:
            # print(home_team, match_scores, away_team)
            if team == home_team:
                home_scores.append(match_scores)
                continue
            elif team == away_team:
                away_scores.append(match_scores)
                continue
        else:
            if home_team_match:
                if team == home_team:
                    home_scores.append(match_scores)
                    continue
            else:
                if team == away_team:
                    away_scores.append(match_scores)
                    continue
    if is_team_form:
        return home_scores[:3], away_scores[:3]
    elif is_h2h:
        return home_scores[:5], away_scores[:5]
    elif home_team_match:
        return home_scores
    else:
        return away_scores


def calculate_points(scores: list, home_team_match: bool):
    points = 0
    for score in scores:
        final_scores = [int(s) for s in score.split('-')]
        # print(final_scores)
        if home_team_match:
            if final_scores[0] > final_scores[1]:
                points += 3
            elif final_scores[0] == final_scores[1]:
                points += 1
        else:
            if final_scores[0] < final_scores[1]:
                points += 3
            elif final_scores[0] == final_scores[1]:
                points += 1

    return points


def calculate_team_form(home_scores: list, away_scores: list):
    home_team__home_points = calculate_points(
        home_scores[0], home_team_match=True)
    home_team_away_points = calculate_points(
        home_scores[1], home_team_match=False)
    home_team_points = home_team__home_points + home_team_away_points

    away_team__home_points = calculate_points(
        away_scores[0], home_team_match=True)
    away_team_away_points = calculate_points(
        away_scores[1], home_team_match=False)
    away_team_points = away_team__home_points + away_team_away_points

    return home_team_points - away_team_points


def get_goals(scores: list, home_team_match: bool, gd=False):
    last_goal = 0
    if home_team_match:
        last_goal = int(scores[0].split('-')[0])
    else:
        last_goal = int(scores[0].split('-')[1])

    goals = 0
    for score in scores:
        final_scores = [int(s) for s in score.split('-')]
        if home_team_match:
            if gd:
                goals += final_scores[0] - final_scores[1]
            else:
                goals += final_scores[0]
        else:
            if gd:
                goals += final_scores[1] - final_scores[0]
            else:
                goals += final_scores[1]
    if gd:
        return goals
    return goals/len(scores), last_goal


def get_percentage(scores: list, home_team_match: bool):
    wins = 0
    for score in scores:
        final_scores = [int(s) for s in score.split('-')]
        if home_team_match:
            if final_scores[0] > final_scores[1]:
                wins += 1
        else:
            if final_scores[0] < final_scores[1]:
                wins += 1
    return wins/len(scores)


def get_data(driver: WebDriver, home: str, away: str, league: str):
    vals = data_blueprint()
    
    vals['home'] = home
    vals['away'] = away
    vals['league'] = league
    
    print(f'{home} vs {away}')

    try:
        prepare(driver)
    except Exception as e:
        pass
    
    html = driver.page_source
    soup = bs(html, 'lxml')

    home_rows = get_table_rows(soup, '#table_v1 > tbody > tr')
    home_team_form = get_last_goals(
        home_rows, team=home, num=1, home_team_match=True, is_team_form=True)

    away_rows = get_table_rows(soup, '#table_v2 > tbody > tr')
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

    h2h_rows = get_table_rows(soup, '#table_v3 > tbody > tr')
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

    if home_rank != '' and away_rank != '':
        vals['lh'] = int(home_rank)
        vals['la'] = int(away_rank)
        use_table = False

        if num_home_matches != '' and num_away_matches != '':
            if int(num_home_matches) >= 5 and int(num_away_matches) >= 5:
                use_table = True
            else:
                use_table = False

        if use_table:
            vals['hf'] = int(home_points) / (int(num_home_matches) * 3)
            vals['af'] = int(away_points) / (int(num_away_matches) * 3)
            pass
        # else:
            # vals['hf'] = calculate_points(home_scores[:5], home_team_match=True)/(min(5, len(home_scores)) * 3)
            # pass

    return vals
