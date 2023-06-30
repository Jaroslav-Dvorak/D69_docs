# import MySQLdb
from datetime import datetime
from time import time
from sqlalchemy import create_engine, exc
import pandas as pd
from credintials import host, user, passwd, db


conn_string = f"mysql+mysqldb://{user}:{passwd}@{host}/{db}"
engine = create_engine(conn_string, pool_recycle=280)


class Data:

    def __init__(self, db_table, update_db_interval_s = 10):

        self.db_table = db_table
        self.update_db_interval_s = update_db_interval_s

        self.timestamp = None
        self.power = 0.0
        self.energy = 0.0
        self.voltage = 0.0
        self.current = 0.0

        self._power = []
        self._energy = []
        self._voltage = []
        self._current = []

        try:
            self.df_energy_daily = self.get_energy_daily()
            self.df_energy_weekly = self.get_energy_weekly()
            self.df_energy_monthly = self.get_energy_monthly()
        except exc.ProgrammingError:
            print("Table not created yet...")

        self.last_db_update = time()-self.update_db_interval_s

    def parse_data(self, msg):
        msg = msg[0]
        try:
            self.timestamp = msg["timestamp"]
            self.power = msg["power"]
            self.energy = msg["energy"]
            self.voltage = msg["voltage"]
            self.current = msg["current"]
        except Exception as e:
            print(e)
            return
        print(msg)

        self._power.append(self.power)
        self._energy.append(self.energy)
        self._voltage.append(self.voltage)
        self._current.append(self.current)
        if (time()-self.last_db_update > self.update_db_interval_s):
            self.database_update()

    def database_update(self):
        self.last_db_update = time()
        if ((self._energy[-1] - self._energy[0]) >= 0 and
            (self._energy[-1] - self._energy[0]) < 0.1):
            energy = self._energy[-1]
        else:
            self._power = []
            self._energy = []
            self._voltage = []
            self._current = []
            return
        power = sum(self._power)/len(self._power)
        voltage = sum(self._voltage)/len(self._voltage)
        current = sum(self._current)/len(self._current)

        db_dict = {}
        db_dict["time"] = [str(datetime.fromtimestamp(self.timestamp))]
        db_dict["power"] = [power]
        db_dict["energy"] = [energy]
        db_dict["voltage"] = [voltage]
        db_dict["current"] = [current]
        df = pd.DataFrame.from_dict(db_dict)

        df.to_sql(self.db_table, engine, if_exists="append", index=False)

        self._power = []
        self._energy = []
        self._voltage = []
        self._current = []

        self.df_energy_daily = self.get_energy_daily()
        self.df_energy_weekly = self.get_energy_weekly()
        self.df_energy_monthly = self.get_energy_monthly()

    def get_energy_daily(self):
        query = f"SELECT DATE(time) AS time, (MAX(energy) - MIN(energy)) AS 'DENNÍ VÝROBA [kWh]' FROM {self.db_table} WHERE time BETWEEN (NOW() - INTERVAL 30 DAY) AND NOW() GROUP BY DAYOFYEAR(time)"
        df = pd.read_sql(query, engine)
        return df

    def get_energy_weekly(self):
        query = f"SELECT WEEKOFYEAR(time) AS time, (MAX(energy) - MIN(energy)) AS 'TÝDENNÍ VÝROBA [kWh]' FROM {self.db_table} WHERE time BETWEEN (NOW() - INTERVAL 20 WEEK) AND NOW() GROUP BY WEEKOFYEAR(time)"
        df = pd.read_sql(query, engine)
        return df

    def get_energy_monthly(self):
        query = f"SELECT MONTHNAME(time) AS time, (MAX(energy) - MIN(energy)) AS 'MĚSÍČNÍ VÝROBA [kWh]' FROM {self.db_table} WHERE time BETWEEN (NOW() - INTERVAL 11 MONTH) AND NOW() GROUP BY MONTH(time)"
        df = pd.read_sql(query, engine)
        return df

    def get_power(self, time_from, time_to):
        query = f"SELECT time, Power AS 'VÝKON' FROM {self.db_table} WHERE time BETWEEN '{time_from}' AND '{time_to}' ORDER BY time"
        df = pd.read_sql(query, engine)
        return df
