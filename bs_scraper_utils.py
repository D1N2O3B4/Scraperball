from bs4 import BeautifulSoup as bs
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from bs4.element import ResultSet, Tag


from utils import scroll_to

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
    # select(driver, "#checkboxleague1")
    select(driver, "#selectMatchCount1 > option:last-child")

    # select(driver, "#checkboxleague2")
    select(driver, "#selectMatchCount2 > option:last-child")

    # select(driver, "#checkboxleague3")
    select(driver, "#selectMatchCount3 > option:last-child")

def filter_rows(rows: ResultSet[Tag], league: str, num: int):
    filtered_rows = []
    for row in rows:
        try:
            id = row['id']
            # print(id, f"tr{num}")
            if f"tr{num}" not in id:
                # print("true")
                continue
        except KeyError as e:
            continue
        # print("style", row.attrs['style'])
        try:
            style = row.attrs['style']
        except KeyError as e:
            style = ""

        if "none" in style:
            continue
        try:
            league_name = row.select_one("td:first-child").attrs['title']
        except Exception as e:
            league_name = ""
            
        if league in league_name:
            filtered_rows.append(row)
        
    return filtered_rows


def get_table_rows(soup: bs, selector: str, league: str, num: int):
    rows = soup.select(selector)
    rows = filter_rows(rows, league, num)
    return rows


def get_last_goals(rows: ResultSet[Tag], team: str, num: int, home_team_match: bool, is_team_form=False, is_h2h=False):
    home_scores = []
    away_scores = []
    for row in rows:
        home_team = row.select_one("td:nth-child(3n)").get_text()
        away_team = row.select_one("td:nth-child(5n)").get_text()
        match_scores = row.select_one(
            f"td:nth-child(4n) > .fscore_{num}").get_text()

        if is_team_form or is_h2h:
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
