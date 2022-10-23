import requests
from bs4 import BeautifulSoup
import datetime
from dateutil.relativedelta import relativedelta
import operator
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import insert
from classes.Player import Player
from tables.team import Team
from tables.coach import Coach
from tables.match import Match
from tables.player import Player as PlayerTable
from tables.player_match import PlayerMatch
import unicodedata
import re

BASE_URL = "https://fbref.com"
URL = "https://fbref.com/en/comps/12/2021-2022/2021-2022-La-Liga-Stats"
page = requests.get(URL)
soup = BeautifulSoup(page.content, "html.parser")
table = soup.select_one('#results2021-2022121_overall>tbody')

game_index = 1
team_index = 1
league_index = 2

position_dict = {
    "GK": 1,
    'RB': 2,
    'CB': 3,
    'LB': 4,
    'RM': 5,
    'CM': 6,
    'LM': 7,
    'FW': 8,
    'AM': 9,
    'DM': 10,
    'WB': 11,
    'WM': 12,
    'RW': 13,
    'LW': 14,
    'DF': 15,
    'MF': 16
}


def get_digits(text):
    if isinstance(text, str):
        return re.sub('\D', '', text)
    else:
        return None

try:
    # Polaczenie z baza danych
    connection_string = 'postgresql://server079348_inzynierka:Aa123456@pgsql14.server079348.nazwa.pl/server079348_inzynierka'
    db = create_engine(connection_string)

    def convert_age_to_datebirth(item):
        datebirth_array = item.text.split('-')
        if len(datebirth_array) == 2:
            years = datebirth_array[0]
            days = datebirth_array[1]
            return match_date - relativedelta(years=int(years), days=int(days))
        else:
            return None

    # Iteracja po klubach
    for row in table.select('td:first-of-type>a'):
        if team_index > 1:
            club_page = requests.get(f'{BASE_URL}{row["href"]}')
            club_page_content = BeautifulSoup(club_page.content, "html.parser")
            match_log = club_page_content.select_one("#matchlogs_for>tbody")
            league_matches = []

            # Filtrujemy mecze - wybieramy tylko mecze ligowe
            for match_type, match in zip(match_log.select('td[data-stat=round]>a'), match_log.select('tr')):
                if match_type.text.split(' ')[0] == 'Matchweek' and match != ' ':
                    league_matches.append(match)

            # Przechodzimy do podstron meczowych
            for match_row in league_matches:
                match_page = requests.get(f'{BASE_URL}{match_row.select_one("td[data-stat=match_report]>a")["href"]}')
                match_page_content = BeautifulSoup(match_page.content, "html.parser")

                # Dane meczu
                match_date_string = \
                    match_page_content.select_one('.scorebox>.scorebox_meta>div:first-of-type>strong>a')['href'].split(
                        '/')[
                        -1]
                match_date_array = match_date_string.split('-')
                match_date = datetime.date(int(match_date_array[0]), int(match_date_array[1]), int(match_date_array[2]))
                home_team = match_page_content.select_one(
                    '.scorebox > div:first-of-type > div > strong > a').text.strip()
                away_team = match_page_content.select_one(
                    '.scorebox > div:nth-of-type(2) > div > strong > a ').text.strip()

                # Dane gospodarza
                home_team_score = get_digits(match_page_content.select_one('.scorebox>div:first-of-type>.scores>.score').text)
                home_team_xG = match_page_content.select_one('.scorebox>div:first-of-type>.scores>.score_xg').text
                home_team_coach = match_page_content.select_one('.scorebox>div:first-of-type>div:nth-of-type(5)').text.split(':')[1]
                home_team_possession = match_page_content.select_one(
                    '#team_stats table td:nth-child(1) div div:nth-child(1) strong').text[:-1]
                home_team_passes_array = match_page_content.select_one(
                    '#team_stats table tr:nth-child(5) td:nth-child(1) div div:nth-child(1)').text.split('of')
                home_team_passes_completed = home_team_passes_array[0][:-1]
                home_team_passes = home_team_passes_array[1][1:].split('—')[0]
                home_team_shots_array = match_page_content.select_one(
                    '#team_stats table tr:nth-child(7) td:nth-child(1) div div:nth-child(1)').text.split('of')
                home_team_shots_on_target = home_team_shots_array[0][:-1]
                home_team_shots = home_team_shots_array[1][1:].split('—')[0]
                home_team_fouls = match_page_content.select_one(
                    '#team_stats_extra>div:first-of-type>div:nth-of-type(4)').text
                home_team_touches = match_page_content.select_one(
                    '#team_stats_extra>div:first-of-type>div:nth-of-type(10)').text
                home_team_aerials_won = match_page_content.select_one(
                    '#team_stats_extra>div:nth-of-type(2)>div:nth-of-type(10)').text
                home_team_offsides = match_page_content.select_one(
                    '#team_stats_extra>div:nth-of-type(3)>div:nth-of-type(4)').text
                home_team_yellow_cards = len(match_page_content.select('tr > td:nth-of-type(1) .yellow_card'))
                home_team_red_cards = len(match_page_content.select('tr > td:nth-of-type(1) .red_card, tr > td:nth-of-type(1) .yellow_red_card'))

                # Dane gościa
                away_team_score = get_digits(match_page_content.select_one('.scorebox>div:nth-of-type(2)>.scores>.score').text)
                away_team_xG = match_page_content.select_one('.scorebox>div:nth-of-type(2)>.scores>.score_xg').text
                away_team_coach = \
                    match_page_content.select_one('.scorebox>div:nth-of-type(2)>div:nth-of-type(5)').text.split(':')[1]
                away_team_possession = match_page_content.select_one(
                    '#team_stats table tr:nth-child(3) td:nth-child(2) div div strong').text[:-1]
                away_team_passes_array = match_page_content.select_one(
                    '#team_stats table tr:nth-child(5) td:nth-child(2) div div:nth-child(1)').text.split('of')
                away_team_passes_completed = away_team_passes_array[0][:-1].split('—')[1]
                away_team_passes = away_team_passes_array[1][1:]
                away_team_shots_array = match_page_content.select_one(
                    '#team_stats table tr:nth-child(7) td:nth-child(2) div div:nth-child(1)').text.split('of')
                away_team_shots_on_target = away_team_shots_array[0][:-1].split('—')[1]
                away_team_shots = away_team_shots_array[1][1:]
                away_team_fouls = match_page_content.select_one(
                    '#team_stats_extra>div:first-of-type>div:nth-of-type(6)').text
                away_team_touches = match_page_content.select_one(
                    '#team_stats_extra>div:first-of-type>div:nth-of-type(12)').text
                away_team_aerials_won = match_page_content.select_one(
                    '#team_stats_extra>div:nth-of-type(2)>div:nth-of-type(12)').text
                away_team_offsides = match_page_content.select_one(
                    '#team_stats_extra>div:nth-of-type(3)>div:nth-of-type(6)').text
                away_team_yellow_cards = len(match_page_content.select('tr > td:nth-of-type(2) .yellow_card'))
                away_team_red_cards = len(match_page_content.select('tr > td:nth-of-type(2) .red_card'))

                # Dane zawodnikow
                index_getter = operator.itemgetter(0, 2)
                players_stats_tables = index_getter(match_page_content.findAll('div', {'class': 'table_wrapper'}))

                home_players = []
                away_players = []

                for table in players_stats_tables:
                    # Najpierw dla gospodarzy, potem dla gosci
                    players_names = table.select(
                        '.table_container.current th[data-stat=player]>a, tfoot>tr>th[data-stat=player]')
                    players_positions = table.select('td[data-stat=position]:not(tfoot *, .shade_zero *)')
                    players_countries = list(map(lambda x: x.text.split(' ')[1], table.select(
                        'td[data-stat=nationality]>a>span:not(tfoot *, .shade_zero *)')))
                    players_age = table.select('td[data-stat=age]:not(tfoot *, .shade_zero *)')
                    players_minutes = table.select('td[data-stat=minutes]:not(tfoot *, .shade_zero *)')
                    players_goals = table.select('td[data-stat=goals]:not(tfoot *)')
                    players_assists = table.select('td[data-stat=assists]:not(tfoot *)')
                    players_pens_made = table.select('td[data-stat=pens_made]:not(tfoot *)')
                    players_pens_att = table.select('td[data-stat=pens_att]:not(tfoot *)')
                    players_shots = table.select('td[data-stat=shots_total]:not(tfoot *)')
                    players_shots_on_target = table.select('td[data-stat=shots_on_target]:not(tfoot *)')
                    players_yellow_cards = table.select('td[data-stat=cards_yellow]:not(tfoot *)')
                    players_red_cards = table.select('td[data-stat=cards_red]:not(tfoot *)')
                    players_touches = table.select('td[data-stat=touches]:not(tfoot *)')
                    players_xg = table.select('td[data-stat=xg]:not(tfoot *)')
                    players_passes = table.select('td[data-stat=passes]:not(tfoot *)')
                    players_passes_completed = table.select('td[data-stat=passes_completed]:not(tfoot *)')
                    players_progressive_passes = table.select('td[data-stat=progressive_passes]:not(tfoot *)')
                    players_dribbles = table.select('td[data-stat=dribbles]:not(tfoot *)')
                    players_dribbles_completed = table.select('td[data-stat=dribbles_completed]:not(tfoot *)')

                    players_names = list(filter(lambda x: x != '-',
                                                [a.text if a.text[2:] != ' Players' else '-' for a in players_names]))
                    players_age = list(map(convert_age_to_datebirth, players_age))

                    team_players = []

                    for player, age, position, country, minutes, goals, assists, \
                        pens_made, pens_att, shots, \
                        shots_on_target, yellow_cards, red_cards, \
                        touches, xg, passes, passes_completed, \
                        progressive_passes, dribbles, dribbles_completed \
                            in zip(players_names, players_age,
                                   players_positions,
                                   players_countries,
                                   players_minutes, players_goals,
                                   players_assists, players_pens_made,
                                   players_pens_att, players_shots,
                                   players_shots_on_target, players_yellow_cards,
                                   players_red_cards, players_touches,
                                   players_xg, players_passes,
                                   players_passes_completed, players_progressive_passes,
                                   players_dribbles, players_dribbles_completed):
                        team_players.append(Player(player,
                                                   position.text.split(',')[0],
                                                   country or None,
                                                   age or None,
                                                   minutes.text or None,
                                                   goals.text or None,
                                                   assists.text or None,
                                                   pens_made.text or None,
                                                   pens_att.text or None,
                                                   shots.text or None,
                                                   shots_on_target.text or None,
                                                   yellow_cards.text or None,
                                                   red_cards.text or None,
                                                   touches.text or None,
                                                   xg.text or None,
                                                   passes.text or None,
                                                   passes_completed.text or None,
                                                   progressive_passes.text or None,
                                                   dribbles.text or None,
                                                   dribbles_completed.text or None
                                                   ))

                    if len(home_players):
                        away_players = team_players
                    else:
                        home_players = team_players

                print(f'> game {game_index} scraped')

                # Sprawdzenie czy istnieje rekord w tabelach coach i team - jesli nie to dodanie go
                home_coach_full_name = unicodedata.normalize('NFKD', home_team_coach).encode('ascii', 'ignore').decode(
                    'utf-8').strip()
                add_home_coach = insert(Coach).returning(Coach.id).values(full_name=home_coach_full_name)
                add_home_coach = add_home_coach.on_conflict_do_update(
                    constraint='name_unique',
                    set_=dict(full_name=home_coach_full_name)
                )

                away_coach_full_name = unicodedata.normalize('NFKD', away_team_coach).encode('ascii', 'ignore').decode(
                    'utf-8').strip()
                add_away_coach = insert(Coach).returning(Coach.id).values(full_name=away_coach_full_name)
                add_away_coach = add_away_coach.on_conflict_do_update(
                    constraint='name_unique',
                    set_=dict(full_name=away_coach_full_name)
                )

                add_home_team = insert(Team).returning(Team.id).values(name=unicodedata.normalize('NFKD', home_team).encode('ascii', 'ignore').decode(
                    'utf-8').strip(), season='2021/2022', league=league_index)
                add_home_team = add_home_team.on_conflict_do_update(
                    constraint='name_and_season_unique',
                    set_=dict(league=league_index)
                )

                add_away_team = insert(Team).returning(Team.id).values(name=unicodedata.normalize('NFKD', away_team).encode('ascii', 'ignore').decode(
                    'utf-8').strip(), season='2021/2022', league=league_index)
                add_away_team = add_away_team.on_conflict_do_update(
                    constraint='name_and_season_unique',
                    set_=dict(league=league_index)
                )

                home_coach_insert = db.execute(add_home_coach)
                away_coach_insert = db.execute(add_away_coach)
                home_team_insert = db.execute(add_home_team)
                away_team_insert = db.execute(add_away_team)

                home_coach_id = home_coach_insert.first()['id']
                away_coach_id = away_coach_insert.first()['id']
                home_team_id = home_team_insert.first()['id']
                away_team_id = away_team_insert.first()['id']

                print('> coach and team inserted')

                # Dodawanie rekordu do tabeli match
                add_match = insert(Match).returning(Match.id).values(
                    league=league_index,
                    date=match_date,
                    is_neutral_ground=False,
                    home_team=home_team_id,
                    away_team=away_team_id,
                    home_team_coach=home_coach_id,
                    away_team_coach=away_coach_id,
                    home_team_score=home_team_score,
                    away_team_score=away_team_score,
                    home_team_shots=int(get_digits(home_team_shots) or '0'),
                    away_team_shots=int(get_digits(away_team_shots) or '0'),
                    home_team_shots_on_target=int(get_digits(home_team_shots_on_target) or '0'),
                    away_team_shots_on_target=int(get_digits(away_team_shots_on_target) or '0'),
                    home_team_possession=int(get_digits(home_team_possession) or '0'),
                    away_team_possession=int(get_digits(away_team_possession) or '0'),
                    home_team_passes=int(get_digits(home_team_passes) or '0'),
                    away_team_passes=int(get_digits(away_team_passes) or '0'),
                    home_team_completed_passes=int(get_digits(home_team_passes_completed) or '0'),
                    away_team_completed_passes=int(get_digits(away_team_passes_completed) or '0'),
                    home_team_fouls=int(get_digits(home_team_fouls) or '0'),
                    away_team_fouls=int(get_digits(away_team_fouls) or '0'),
                    home_team_yellow_cards=home_team_yellow_cards,
                    away_team_yellow_cards=away_team_yellow_cards,
                    home_team_red_cards=home_team_red_cards,
                    away_team_red_cards=away_team_red_cards,
                    home_team_aerials_won=get_digits(home_team_aerials_won or '0'),
                    away_team_aerials_won=get_digits(away_team_aerials_won or '0'),
                    home_team_touches=get_digits(home_team_touches or '0'),
                    away_team_touches=get_digits(home_team_touches or '0'),
                    home_team_xG=float(home_team_xG or '0'),
                    away_team_xG=float(away_team_xG or '0')
                ).on_conflict_do_update(
                    constraint='teams_and_date_unique',
                    set_=dict(league=1)
                )

                match_insert = db.execute(add_match)
                match_id = match_insert.first()['id']

                print('> match inserted')

                # Sprawdzenie czy istnieje zawodnik w tabeli player - jesli nie to dodanie go, dodanie rekordow w tabeli player_match
                for player in home_players + away_players:
                    add_player = insert(PlayerTable).returning(PlayerTable.id).values(
                        full_name=unicodedata.normalize('NFKD', player.name).encode('ascii', 'ignore').decode(
                            'utf-8').strip(), birthday=player.age, nationality=player.country).on_conflict_do_update(
                        constraint='player_unique',
                        set_=dict(birthday=player.age)
                    )
                    player_insert = db.execute(add_player)
                    player_id = player_insert.first()['id']

                    add_player_match = insert(PlayerMatch).values(
                        match_id=match_id,
                        player_id=player_id,
                        position=position_dict[player.position],
                        minutes_played=int(get_digits(player.minutes) or '0'),
                        goals=int(get_digits(player.goals) or '0'),
                        assists=int(get_digits(player.assists) or '0'),
                        shots=int(get_digits(player.shots) or '0'),
                        shots_on_target=int(get_digits(player.shots_on_target) or '0'),
                        penalties=int(get_digits(player.pens_att) or '0'),
                        penalties_made=int(get_digits(player.pens_made) or '0'),
                        passes=int(get_digits(player.passes) or '0'),
                        completed_passes=int(get_digits(player.passes_completed) or '0'),
                        progressive_passes=int(get_digits(player.progressive_passes) or '0'),
                        xG=float(player.xg or '0'),
                        yellow_cards=int(get_digits(player.yellow_cards) or '0'),
                        red_cards=int(get_digits(player.red_cards) or '0'),
                        touches=int(get_digits(player.touches) or '0'),
                        dribbles=int(get_digits(player.dribbles) or '0'),
                        dribbles_completed=int(get_digits(player.dribbles_completed) or '0')
                    ).on_conflict_do_update(
                        constraint='player_and_match_unique',
                        set_=dict(player_id=player_id)
                    )

                    db.execute(add_player_match)

                print('> players inserted')

                print(f'>>> game {game_index} completed')
                game_index += 1

        print(f'>>>>> team {team_index} completed')
        team_index += 1
        game_index = 1

except Exception as error:
    print("Error while connecting to PostgreSQL", error)
