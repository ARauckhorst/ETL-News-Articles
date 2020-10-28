import sqlite3
from sqlite3 import Error


class Database:
    def __init__(self, filename):
        self.filename = filename
        self.conn = None

    def create_connection(self):
        try:
            self.conn = sqlite3.connect(self.filename)
        except Error as e:
            print(e)

        return self.conn

    def create_table(self, sql):
        try:
            c = self.conn.cursor()
            c.execute(sql)
        except Error as e:
            print(e)

    def insert_row(self, sql, row):
        cur = self.conn.cursor()
        cur.execute(sql, row)
        self.conn.commit()
        return cur.lastrowid

    def insert_many_rows(self, sql, rows):
        cur = self.conn.cursor()
        cur.executemany(sql, rows)
        self.conn.commit()
        return cur.lastrowid

    def close_connection(self):
        self.conn.close()
