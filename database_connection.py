import sqlite3


class DatabaseConnection:
    res: bool

    def __init__(self):
        self.con = None
        self.cursor = None
        self.db_name = "project_hod.db"
        self.res = False

    def connect(self):
        try:
            self.con = sqlite3.connect(self.db_name)
            self.cursor = self.con.cursor()
            print('connection sucess')
        except sqlite3.Error as e:
            print(f"Errot in connection : {e}")

    def execute_and_fetch_query(self, query, fetch=True, params=None):

        try:
            if params is not None:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            if fetch:
                result = self.cursor.fetchall()
                return result
            else:
                self.con.commit()
                print("Query executed successfully")
                return True

        except sqlite3.Error as e:
            print(f"Error in query: {e}")
            self.con.rollback()
            return e

    # def execute_and_fetech_query(self, query, fetch=True):
    #     try:
    #         self.cursor.execute(query)
    #         if fetch:
    #             result = self.cursor.fetchall()
    #             return result
    #         else:
    #             self.con.commit()
    #             print("query Executed Sucessfully")
    #
    #     except sqlite3.Error as e:
    #         print(f"Error in query : {e}")
    #         return None

    def con_close(self):
        if self.con:
            self.con.close()
            print("connection closed")

    def __del__(self):
        self.con_close()
        print("data base connection  deleteds")
