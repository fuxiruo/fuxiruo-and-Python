import sqlite3
import logging
import os

LOG_FORMAT = '[%(asctime)s][%(levelname)5s][%(module)s:%(funcName)s][%(threadName)10s:%(thread)5d]->%(message)s'

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# create formatter
formatter = logging.Formatter(LOG_FORMAT)

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)

class MySqlite():
    def __init__(self, db_file=None):
        self._db_file = db_file
        if db_file is None:
            self._conn = None
            return

        try:
            self._conn = sqlite3.connect(self._db_file)
            self._c = self._conn.cursor()
        except sqlite3.Error as e:
            logger.error(str(e))
            raise e

    def open(self, db_file):            
        try:
            if db_file=="":
                return

            if self._conn:
                self._conn.close()

            self._db_file = db_file
            self._conn = sqlite3.connect(self._db_file)
            self._c = self._conn.cursor()

            logger.info(self._db_file + ' open')
        except sqlite3.Error as e:
            logger.error(str(e))
            raise e

    def __del__(self):
        try: 
            if self._conn:
                logger.info(self._db_file + ' close')
                self._conn.close()
        except sqlite3.Error as e:
            logger.error(str(e))
            raise e

    def _execute(self, sql):
        logger.debug(sql)
        self._c.execute(sql)

    def get_tables(self):
        try:
            self._execute('select name from sqlite_sequence order by name')
            tables = []
            while True:
                r = self._c.fetchone()
                if r is None:
                    break
                else:
                    tables.append(r[0])
            return tables
        except sqlite3.Error as e:
            logger.error(str(e))
            raise e

    def del_table(self, table):
        try:
            self._execute('delete from ' + table)
            self._execute('commit')
        except sqlite3.Error as e:
            logger.error(str(e))
            raise e

def test_my_sqlite():
    logger.info(__file__)
    current_path = os.path.dirname(__file__)
    mySqlite = MySqlite(current_path + '/data.db')
    tables = mySqlite.get_tables()
    logger.info(tables)

if __name__ == '__main__':
    test_my_sqlite()
