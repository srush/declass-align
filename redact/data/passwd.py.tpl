"Get db info."

import MySQLdb as mysql

def get_db():
  return mysql.connect(user="", db="", host="", passwd="")

def get_cursor(db):
  return db.cursor(mysql.cursors.SSDictCursor)
