from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
import traceback

from utils import scroll_to


def getMatchDetails(driver: WebDriver, homeTeam: str, awayTeam: str, leagueTitle: str) -> object:
    print(f'{homeTeam} vs {awayTeam}')
    table = driver.find_element(By.CSS_SELECTOR, "#porletP3 .team-div")

    vals = {
        "home": homeTeam,
        "away": awayTeam,
        "league": leagueTitle,
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
        '5h': 0,
        '5a': 0,
        'l3h': 0,
        'l3a': 0,
        'h%': 0,
        'a%': 0,
        'gd': 0
    }

    # try:
    # Team Form
    # home team stats

    home_count_selector = driver.find_element(
        By.CSS_SELECTOR, "#selectMatchCount1 > option:last-child")
    scroll_to(driver, home_count_selector)
    home_count_selector.click()

    away_count_selector = driver.find_element(
        By.CSS_SELECTOR, "#selectMatchCount2 > option:last-child")
    scroll_to(driver, away_count_selector)
    away_count_selector.click()

    same_league = driver.find_element(By.ID, "checkboxleague1")
    # same_league_checked = same_league.get_attribute('checked')
    same_league_checked = same_league.is_selected()
    if not same_league_checked:
        same_league.click()
    away_league = driver.find_element(By.ID, "checkboxleague2")
    away_league_checked = away_league.is_selected()
    if not away_league_checked:
        away_league.click()

    home_team_matches = driver.find_elements(
        By.CSS_SELECTOR, "#table_v1 > tbody > tr")

    home_team_stats = {
        "home": 0,
        "away": 0,
        # "last_5_goals": 0
    }

    num_of_home = 0
    # num_of_home_goals = 1
    num_of_away = 0

    # get the last 3 home matches and 3 away match for the home team

    for match in home_team_matches:
        if "tr1" not in match.get_attribute("id"):
            continue

        home = match.find_element(By.CSS_SELECTOR, "td:nth-child(3n)").text
        scores = match.find_element(
            By.CSS_SELECTOR, "td:nth-child(4n) .fscore_1").text
        away = match.find_element(By.CSS_SELECTOR, "td:nth-child(5n)").text

        diff = scores.split('-')

        if home == homeTeam and num_of_home < 3:
            if int(diff[0]) > int(diff[1]):
                home_team_stats['home'] += 3
            elif int(diff[0]) == int(diff[1]):
                home_team_stats['home'] += 1
            num_of_home += 1
        elif away == homeTeam and num_of_away < 3:
            if int(diff[0]) < int(diff[1]):
                home_team_stats['away'] += 3
            elif int(diff[0]) == int(diff[1]):
                home_team_stats['away'] += 1
            num_of_away += 1

    # away team stats
    away_team_matches = driver.find_elements(
        By.CSS_SELECTOR, "#table_v2 > tbody > tr")
    away_team_stats = {
        "home": 0,
        "away": 0,
    }
    num_of_home = 0
    num_of_away = 0

    for match in away_team_matches:
        if "tr2" not in match.get_attribute("id"):
            continue
        home = match.find_element(By.CSS_SELECTOR, "td:nth-child(3n)").text
        scores = match.find_element(
            By.CSS_SELECTOR, "td:nth-child(4n) > .fscore_2").text
        away = match.find_element(By.CSS_SELECTOR, "td:nth-child(5n)").text
        diff = scores.split('-')

        if home == awayTeam and num_of_home < 3:
            if int(diff[0]) > int(diff[1]):
                away_team_stats['home'] += 3
            elif int(diff[0]) == int(diff[1]):
                away_team_stats['home'] += 1
            num_of_home += 1
        elif away == awayTeam and num_of_away < 3:
            if int(diff[0]) < int(diff[1]):
                away_team_stats['away'] += 3
            elif int(diff[0]) == int(diff[1]):
                away_team_stats['away'] += 1
            num_of_away += 1

    vals['fm'] = (home_team_stats['home'] + home_team_stats['away']) - \
        (away_team_stats['home'] + away_team_stats['away'])

    # click home check button
    home_check = driver.find_element(By.ID, "cb_sos1")
    home_checked = home_check.is_selected()
    if not home_checked:
        scroll_to(driver, home_check)
        home_check.click()

    home_scores = driver.find_elements(
        By.CSS_SELECTOR, "#table_v1 tbody tr td span.fscore_1")

    # click away check button
    away_check = driver.find_element(By.ID, "cb_sos2")
    away_checked = away_check.is_selected()
    if not away_checked:
        scroll_to(driver, away_check)
        away_check.click()

    away_scores = driver.find_elements(
        By.CSS_SELECTOR, "#table_v2 tbody tr td span.fscore_2")

    homeRank = 0
    home_matches = 0
    awayRank = 0
    away_matches = 0

    try:
        # print("trying")
        # select home rank and number of home matches
        homeRank = driver.find_element(
            By.CSS_SELECTOR, ".home-div tbody > tr:nth-child(3n) > td:nth-child(9n)").text
        home_matches = driver.find_element(
            By.CSS_SELECTOR, ".home-div tbody > tr:nth-child(4n) > td:nth-child(2n)").text

        # select away rank and number of away matches
        awayRank = driver.find_element(
            By.CSS_SELECTOR, ".guest-div tbody > tr:nth-child(3n) > td:nth-child(9n)").text
        away_matches = driver.find_element(
            By.CSS_SELECTOR, ".guest-div tbody > tr:nth-child(5n) > td:nth-child(2n)").text
        # print(rank.text)
    except Exception as e:
        print(e)
        traceback.print_stack()
        pass

    if (homeRank == '' or awayRank == '') or (int(home_matches) < 5 or int(away_matches) < 5):
        hf = 0
        af = 0
        if homeRank == '' or awayRank == '' or homeRank == 0 or awayRank == 0:
            homeRank = 0
            awayRank = 0

        i = 1
        for score in home_scores:
            showing = score.is_displayed()
            if not showing:
                continue
            # print(score.text)

            diff = score.text.split('-')
            if int(diff[0]) > int(diff[1]):
                hf += 3
            elif int(diff[0]) == int(diff[1]):
                hf += 1
            if i >= 5:
                break
            i += 1
    #         pass
        hf = hf / (i*3)
        # print(hf)
        vals['hf'] = hf
        vals['lh'] = homeRank

        i = 1
        for score in away_scores:
            showing = score.is_displayed()
            if not showing:
                continue
            # print(score.text)

            diff = score.text.split('-')
            if int(diff[1]) > int(diff[0]):
                af += 3
            elif int(diff[0]) == int(diff[1]):
                af += 1
            if i >= 5:
                break
            i += 1

        # print(af)
        af = af / (i*3)
        vals['af'] = af
        vals['la'] = awayRank

    else:
        # try:
        # home_perfomance = home_team[3].find_elements(By.TAG_NAME, 'td')
        home_points = driver.find_element(
            By.CSS_SELECTOR, ".home-div tbody > tr:nth-child(4n) > td:nth-child(8n)").text

        # home_total = home_perfomance.find_element(By.CSS_SELECTOR, ":nth-selector(8n)")
    #         print(home_perfomance[1].text)
        # home_form = int(home_perfomance[7].text) / (int(home_perfomance[1].text) * 3)
        home_form = int(home_points) / (int(home_matches) * 3)

        vals['hf'] = home_form
        vals['lh'] = homeRank

        # away rank
        # away_perfomance = away_team[4].find_elements(By.TAG_NAME, 'td')
        away_points = driver.find_element(
            By.CSS_SELECTOR, ".guest-div tbody > tr:nth-child(5n) > td:nth-child(8n)").text

        # away_form = int(away_perfomance[7].text) / (int(away_perfomance[1].text) * 3)
        away_form = int(away_points) / (int(away_matches) * 3)

        vals['af'] = away_form
        vals['la'] = awayRank
        # except Exception as e:
        #     print("home form and away form")
        #     print(e)
        #     traceback.print_exc()
        #     # print(e)

# last three home matches for the home team
    last_3_home = 0
    i = 1
    for score in home_scores:
        showing = score.is_displayed()
        if not showing:
            continue
        # print(score.text)

        diff = score.text.split('-')
        if int(diff[0]) > int(diff[1]):
            last_3_home += 3
        elif int(diff[0]) == int(diff[1]):
            last_3_home += 1
        if i == 3:
            break
        i += 1

    last_3_home = last_3_home / (i*3)

    vals['3h'] = last_3_home

    # last home match for the home team
    last_home = ''

    for score in home_scores:
        if score.is_displayed():
            diff = score.text.split('-')
            if int(diff[0]) > int(diff[1]):
                last_home = 'W'
            elif int(diff[0]) < int(diff[1]):
                last_home = 'L'
            else:
                last_home = "D"
            break

    # print(last_3_home, last_home)
    vals['h'] = last_home

    # last 5 home games total goals scored and
    # last 3 home games total goals and
    # home team handicap percentage

    last_5_home_goals = []
    last_3_home_goals = []
    home_handicap_percentage = []
    goal_difference = []
    # i = 0
    for score in home_scores:
        if not score.is_displayed():
            continue
        if not len(last_5_home_goals) < 5:
            continue
        diff = score.text.split('-')
        last_5_home_goals.append(int(diff[0]))
        if int(diff[0]) > int(diff[1]):
            home_handicap_percentage.append(1)
        else:
            home_handicap_percentage.append(0)
        if not len(last_3_home_goals) < 3:
            continue
        last_3_home_goals.append(int(diff[0]))
        goal_difference.append(
            int(diff[0]) - int(diff[1])
        )

    vals['5h'] = sum(last_5_home_goals) / max(len(last_5_home_goals), 1)
    vals['l3h'] = sum(last_3_home_goals) / max(len(last_3_home_goals), 1)
    vals['h%'] = sum(home_handicap_percentage) / \
        max(len(home_handicap_percentage), 1)
    vals['gd'] = sum(goal_difference)

    last_3_away = 0
    i = 1
    for score in away_scores:
        showing = score.is_displayed()
        if not showing:
            continue
        # print(score.text)
        diff = score.text.split('-')
        if int(diff[0]) < int(diff[1]):
            last_3_away += 3
        elif int(diff[0]) == int(diff[1]):
            last_3_away += 1
        if i == 3:
            break
        i += 1

    last_3_away = last_3_away / (i*3)

    vals['3w'] = last_3_away

    last_away = ''

    for score in away_scores:
        if score.is_displayed():
            diff = score.text.split('-')
            if int(diff[0]) < int(diff[1]):
                last_away = 'W'
            elif int(diff[0]) > int(diff[1]):
                last_away = 'L'
            else:
                last_away = "D"
            break

    # print(last_3_away, last_away)

    vals['a'] = last_away

    # last 5 away games total goals scored and
    # last 3 away games total games and
    # away team handicap percentage

    last_5_away_goals = []
    last_3_away_goals = []
    away_handicap_percentage = []
    goal_difference = []

    for score in away_scores:
        if not score.is_displayed():
            continue
        if not len(last_5_away_goals) < 5:
            continue
        diff = score.text.split('-')
        last_5_away_goals.append(int(diff[1]))
        if (int(diff[1]) > int(diff[0])):
            away_handicap_percentage.append(1)
        else:
            away_handicap_percentage.append(0)
        if not len(last_3_away_goals) < 3:
            continue
        last_3_away_goals.append(int(diff[1]))
        goal_difference.append(int(diff[1]) - int(diff[0]))

    vals['5a'] = sum(last_5_away_goals) / max(len(last_5_away_goals), 1)
    vals['l3a'] = sum(last_3_away_goals) / max(len(last_3_away_goals), 1)
    vals['a%'] = sum(away_handicap_percentage) / \
        max(len(away_handicap_percentage), 1)
    vals['gd'] = vals['gd'] - sum(goal_difference)

    # head to head meetings

    head_home_five = []
    head_away_five = []

    h2h_same_league = driver.find_element(By.ID, "checkboxleague3")

    if not h2h_same_league.is_selected():
        h2h_same_league.click()

    try:
        driver.find_element(
            By.CSS_SELECTOR, "#selectMatchCount3 > option:last-child").click()
    except:
        pass

    h2h_matches = driver.find_elements(
        By.CSS_SELECTOR, "#table_v3 > tbody > tr")
    i = []

    for match in h2h_matches:
        showing = match.is_displayed()
        if not showing:
            continue
        if not ("tr3" in match.get_attribute('id')):
            continue
        # print(match.text)

        # if len(head_home_five) >= 5 and len(head_away_five) >= 5:
        #     break

        home_h2h = match.get_attribute('vs')

        scores = match.find_element(
            By.CSS_SELECTOR, "td:nth-child(4n) .fscore_3")

        diff = scores.text.split('-')

        if home_h2h == '1':
            if len(head_home_five) < 5:
                if int(diff[0]) > int(diff[1]):
                    head_home_five.append(3)
                elif int(diff[0]) == int(diff[1]):
                    head_home_five.append(1)
                else:
                    head_home_five.append(0)
        else:
            if len(head_away_five) < 5:
                if int(diff[0]) < int(diff[1]):
                    head_away_five.append(3)
                elif int(diff[0]) == int(diff[1]):
                    head_away_five.append(1)
                else:
                    head_away_five.append(0)

    if len(head_home_five) >= 1:
        vals['h2h'] = head_home_five[0] / 3
        head_home_five = sum(head_home_five) / (len(head_home_five) * 3)
        vals['hh'] = head_home_five
    else:
        vals['h2h'] = 0
        vals['hh'] = 0

    if len(head_away_five) >= 1:
        vals['h2a'] = head_away_five[0] / 3
        head_away_five = sum(head_away_five) / (len(head_away_five) * 3)
        vals['ha'] = head_away_five
    else:
        vals['h2a'] = 0
        vals['ha'] = 0

    return vals
