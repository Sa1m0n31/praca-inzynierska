import sqlalchemy as db
from sqlalchemy import create_engine
from tables.match import Match
import random

connection_string = 'postgresql://server079348_inzynierka:Aa123456@pgsql14.server079348.nazwa.pl/server079348_inzynierka'


class Database:
    def __init__(self):
        self.db = create_engine(connection_string)
        self.connection = self.db.connect()

    def get_random_matches(self, n):
        select_all_matches = db.select([Match])
        result_proxy = self.connection.execute(select_all_matches)
        return random.choices(result_proxy.fetchall(), k=n)

    def get_all_matches(self):
        select_all_matches = db.select([Match])
        result_proxy = self.connection.execute(select_all_matches)
        return result_proxy.fetchall()