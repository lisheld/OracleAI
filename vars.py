import os
from dotenv import load_dotenv

load_dotenv()

catch_errors = True

odds_api_key = os.getenv('odds')
openai_api_key = os.getenv('openai')
discord_api_key = os.getenv('discord')
telegram_api_key = os.getenv('telegram')
GPT_MODEL = "gpt-3.5-turbo"

base_url = 'https://api.the-odds-api.com/v4'
base_params={'apiKey':odds_api_key}

player_props = {
    'americanfootball_nfl': [
    "player_pass_tds",
    "player_pass_yds",
    "player_pass_completions",
    "player_pass_attempts",
    "player_pass_interceptions",
    "player_pass_longest_completion",
    "player_rush_yds",
    "player_rush_attempts",
    "player_rush_longest",
    "player_receptions",
    "player_reception_yds",
    "player_reception_longest",
    "player_kicking_points",
    "player_field_goals",
    "player_tackles_assists",
    "player_1st_td",
    "player_last_td",
    "player_anytime_td"
    ],
    'americanfootball_ncaaf': [
    "player_pass_tds",
    "player_pass_yds",
    "player_pass_completions",
    "player_pass_attempts",
    "player_pass_interceptions",
    "player_pass_longest_completion",
    "player_rush_yds",
    "player_rush_attempts",
    "player_rush_longest",
    "player_receptions",
    "player_reception_yds",
    "player_reception_longest",
    "player_kicking_points",
    "player_field_goals",
    "player_tackles_assists",
    "player_1st_td",
    "player_last_td",
    "player_anytime_td"
    ],
    'basketball_nba': [
    "player_points",
    "player_rebounds",
    "player_assists",
    "player_threes",
    "player_blocks",
    "player_steals",
    "player_blocks_steals",
    "player_turnovers",
    "player_points_rebounds_assists",
    "player_points_rebounds",
    "player_points_assists",
    "player_rebounds_assists",
    "player_first_basket",
    "player_double_double",
    "player_triple_double"
    ],
    'basketball_ncaab': [
    "player_points",
    "player_rebounds",
    "player_assists",
    "player_threes",
    "player_blocks",
    "player_steals",
    "player_blocks_steals",
    "player_turnovers",
    "player_points_rebounds_assists",
    "player_points_rebounds",
    "player_points_assists",
    "player_rebounds_assists",
    "player_first_basket",
    "player_double_double",
    "player_triple_double"
    ],
    'basketball_wnba': [
    "player_points",
    "player_rebounds",
    "player_assists",
    "player_threes",
    "player_blocks",
    "player_steals",
    "player_blocks_steals",
    "player_turnovers",
    "player_points_rebounds_assists",
    "player_points_rebounds",
    "player_points_assists",
    "player_rebounds_assists",
    "player_first_basket",
    "player_double_double",
    "player_triple_double"
    ],
    'baseball_mlb': [
    "batter_home_runs",
    "batter_first_home_run",
    "batter_hits",
    "batter_total_bases",
    "batter_rbis",
    "batter_runs_scored",
    "batter_hits_runs_rbis",
    "batter_singles",
    "batter_doubles",
    "batter_triples",
    "batter_walks",
    "batter_strikeouts",
    "batter_stolen_bases",
    "pitcher_strikeouts",
    "pitcher_record_a_win",
    "pitcher_hits_allowed",
    "pitcher_walks",
    "pitcher_earned_runs",
    "pitcher_outs"
    ],
    'icehockey_nhl': [
    "player_points",
    "player_power_play_points",
    "player_assists",
    "player_blocked_shots",
    "player_shots_on_goal",
    "player_goals",
    "player_total_saves",
    "player_goal_scorer_first",
    "player_goal_scorer_last",
    "player_goal_scorer_anytime"
    ],
    'soccer_epl': [
    "player_goal_scorer_anytime",
    "player_first_goal_scorer",
    "player_last_goal_scorer",
    "player_to_receive_card",
    "player_to_receive_red_card",
    "player_shots_on_target",
    "player_shots",
    "player_assists"
    ],
    'soccer_france_ligue_one': [
    "player_goal_scorer_anytime",
    "player_first_goal_scorer",
    "player_last_goal_scorer",
    "player_to_receive_card",
    "player_to_receive_red_card",
    "player_shots_on_target",
    "player_shots",
    "player_assists"
    ],
    'soccer_germany_bundesliga': [
    "player_goal_scorer_anytime",
    "player_first_goal_scorer",
    "player_last_goal_scorer",
    "player_to_receive_card",
    "player_to_receive_red_card",
    "player_shots_on_target",
    "player_shots",
    "player_assists"
    ],
    'soccer_italy_serie_a': [
    "player_goal_scorer_anytime",
    "player_first_goal_scorer",
    "player_last_goal_scorer",
    "player_to_receive_card",
    "player_to_receive_red_card",
    "player_shots_on_target",
    "player_shots",
    "player_assists"
    ],
    'soccer_spain_la_liga': [
    "player_goal_scorer_anytime",
    "player_first_goal_scorer",
    "player_last_goal_scorer",
    "player_to_receive_card",
    "player_to_receive_red_card",
    "player_shots_on_target",
    "player_shots",
    "player_assists"
    ],
    'soccer_usa_mls': [
    "player_goal_scorer_anytime",
    "player_first_goal_scorer",
    "player_last_goal_scorer",
    "player_to_receive_card",
    "player_to_receive_red_card",
    "player_shots_on_target",
    "player_shots",
    "player_assists"
    ]
}

