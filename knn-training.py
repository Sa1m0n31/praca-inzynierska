from helpers.database import Database
import pandas as pd
import random
# from sklearn.model_selection import train_test_split
# from sklearn.neighbours import KNeighboursRegressor


class KnnTraining:
    def __init__(self, n, r):
        self.db = Database()
        self.last_matches = n
        self.all_matches = self.db.get_all_matches()
        self.matches = pd.DataFrame(self.all_matches).sort_values(by='date')
        self.matches.columns = self.all_matches[0].keys()
        self.matches['home_team_goal_diff'] = self.matches.apply(lambda x: x['home_team_score'] - x['away_team_score'], axis=1)
        self.matches['away_team_goal_diff'] = self.matches.apply(lambda x: x['away_team_score'] - x['home_team_score'], axis=1)
        self.matches['home_team_shots_diff'] = self.matches.apply(lambda x: x['home_team_shots'] - x['away_team_shots'], axis=1)
        self.matches['away_team_shots_diff'] = self.matches.apply(lambda x: x['away_team_shots'] - x['home_team_shots'], axis=1)
        self.matches['home_team_shots_on_target_diff'] = self.matches.apply(lambda x: x['home_team_shots_on_target'] - x['away_team_shots_on_target'], axis=1)
        self.matches['away_team_shots_on_target_diff'] = self.matches.apply(lambda x: x['away_team_shots_on_target'] - x['home_team_shots_on_target'], axis=1)
        self.matches['home_team_pass_diff'] = self.matches.apply(lambda x: x['home_team_passes'] - x['away_team_passes'], axis=1)
        self.matches['away_team_pass_diff'] = self.matches.apply(lambda x: x['away_team_passes'] - x['home_team_passes'], axis=1)

        self.matches = self.matches[['id', 'home_team', 'away_team', 'home_team_goal_diff', 'away_team_goal_diff',
                                     'date', 'home_team_shots_diff', 'away_team_shots_diff',
                                     'home_team_shots_on_target_diff', 'away_team_shots_on_target_diff',
                                     'home_team_pass_diff', 'away_team_pass_diff']]
        self.sample_size = r
        self.sample = pd.DataFrame()

    def get_sample(self):
        self.sample = self.matches.sample(n=self.sample_size)

    def get_last_n_matches_of_team(self, team_id, match_id, n):
        current_match_date = self.matches[self.matches.id == match_id]
        current_match_date_index = self.matches[self.matches.id == match_id].index

        team_matches = self.matches[(self.matches.away_team == team_id) | (self.matches.home_team == team_id)]
        previous_team_matches = team_matches[team_matches['date'] < current_match_date['date'][current_match_date_index[0]]]

        return previous_team_matches[-n:]

    def get_stats_from_last_n_matches(self, row, team, stat_name):
        current_match_id = row['id']
        home_team_id = row[team]

        last_n_matches = self.get_last_n_matches_of_team(home_team_id, current_match_id, self.last_matches)
        stat_diff = 0

        for index, match in last_n_matches.iterrows():
            stat_diff += match[stat_name]

        return stat_diff

    def update_matches_table(self):
        self.sample['home_team_goal_diff_in_last_n_matches'] = self.sample.apply(self.get_stats_from_last_n_matches, args=('home_team', 'home_team_goal_diff'), axis=1)
        print('home_team_goal_diff updated')
        self.sample['away_team_goal_diff_in_last_n_matches'] = self.sample.apply(self.get_stats_from_last_n_matches, args=('away_team', 'away_team_goal_diff'), axis=1)
        print('away_team_goal_diff updated')
        self.sample['home_team_shots_diff_in_last_n_matches'] = self.sample.apply(self.get_stats_from_last_n_matches, args=('home_team', 'home_team_shots_diff'), axis=1)
        print('home_team_shots_diff updated')
        self.sample['away_team_shots_diff_in_last_n_matches'] = self.sample.apply(self.get_stats_from_last_n_matches, args=('away_team', 'home_team_shots_diff'), axis=1)
        print('away_team_shots_diff updated')
        self.sample['home_team_pass_diff_in_last_n_matches'] = self.sample.apply(self.get_stats_from_last_n_matches, args=('home_team', 'home_team_pass_diff'), axis=1)
        print('home_team_pass_diff updated')
        self.sample['away_team_pass_diff_in_last_n_matches'] = self.sample.apply(self.get_stats_from_last_n_matches, args=('away_team', 'home_team_pass_diff'), axis=1)
        print('away_team_pass_diff updated')


knn_training = KnnTraining(2, 500)

for i in range(2, 10):
    knn_training.last_matches = i
    knn_training.get_sample()
    knn_training.update_matches_table()
    data = knn_training.sample

    train, test = train_test_split(data, test_size=0.3)
    x_columns = ['home_team_shots_diff', 'home_team_shots_on_target_diff', 'home_team_pass_diff']
    y_column = 'home_team_goal_diff'

    knn = KNeighboursRegressor(n_neighbours=5)
    knn.fit(train[x_columns], train[y_column])

    prediction = knn.predict(test[x_columns])

    print(prediction)
    print('end of iteration')
