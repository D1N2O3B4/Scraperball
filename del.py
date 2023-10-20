leagues = []
home = []
away = []
hf_list = []
af_list = []
home3_list = []
away3_list = []
h_list = []
a_list = []
home_rank = []
away_rank = []
head_home_five = []
last_head_home = []
head_away_five = []
last_head_away = []
team_form = []
home_last_5_goals = []
away_last_5_goals = []
home_last_3_goals = []
away_last_3_goals = []
goal_difference = []
home_handicap_percentage = []
away_handicap_percentage = []

leagues.append(match_stats["league"])
home.append(match_stats["home"])
away.append(match_stats["away"])

# task 2
hf_list.append(match_stats['hf'])
af_list.append(match_stats['af'])
home3_list.append(match_stats['3h'])
away3_list.append(match_stats['3w'])
h_list.append(match_stats['h'])
a_list.append(match_stats['a'])
home_rank.append(match_stats['lh'])
away_rank.append(match_stats['la'])
head_home_five.append(match_stats['hh'])
head_away_five.append(match_stats['ha'])
last_head_home.append(match_stats['h2h'])
last_head_away.append(match_stats['h2a'])
team_form.append(match_stats['fm'])
home_last_5_goals.append(match_stats['5h'])
away_last_5_goals.append(match_stats['5a'])
home_last_3_goals.append(match_stats['l3h'])
away_last_3_goals.append(match_stats['l3a'])
goal_difference.append(match_stats['gd'])
home_handicap_percentage.append(match_stats['h%'])
away_handicap_percentage.append(match_stats['a%'])
