import sqlite3 as sql
import os


class SQLClient:

    def __init__(self):
        if os.path.exists('BioDT/process.db'):
            self.conn = sql.connect(database='BioDT/process.db')
            self.cur = self.conn.cursor()
        else:
            self.conn = sql.connect(database='BioDT/process.db')
            self.cur = self.conn.cursor()
            self.cur.execute('''CREATE TABLE dt
                              (id INTEGER PRIMARY KEY, time INTEGER, biomass REAL, do REAL, glucose REAL, lac REAL, agitation INTEGER)''')
            self.cur.execute('''CREATE TABLE NIR
                              (id INTEGER PRIMARY KEY, time INTEGER, biomass REAL)''')
            self.cur.execute('''CREATE TABLE glucose
                                (id INTEGER PRIMARY KEY, time INTEGER, glucose REAL)''')
            self.cur.execute('''CREATE TABLE lac
                                (id INTEGER PRIMARY KEY, time INTEGER, lac REAL)''')
            self.conn.commit()

    def insert_dt(self, time, biomass, do, glucose, lac, agitation):
        self.cur.execute("""INSERT INTO dt VALUES (NULL, ?, ?, ?, ?, ?, ?)""",
                         (time, biomass, do, glucose, lac, agitation))
        self.conn.commit()

    def insert_NIR(self, time, biomass):
        self.cur.execute("""INSERT INTO NIR VALUES (NULL, ?, ?)""", (time, biomass))
        self.conn.commit()

    def insert_glucose(self, time, glucose):
        self.cur.execute("""INSERT INTO glucose VALUES (NULL, ?, ?)""", (time, glucose))
        self.conn.commit()

    def insert_lac(self, time, lac):
        self.cur.execute("""INSERT INTO lac VALUES (NULL, ?, ?)""", (time, lac))
        self.conn.commit()

    def get_lac(self):
        self.cur.execute("""SELECT * FROM lac""")
        rows = self.cur.fetchall()
        return rows

