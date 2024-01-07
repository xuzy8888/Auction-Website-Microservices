import pymysql
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

host = os.environ.get("340DBHOST")
user = os.environ.get("340DBUSER")
passwd = os.environ.get("340DBPW")
db = os.environ.get("340DB")


def connect_to_database(host=host, user=user, passwd=passwd, db=db):
    db_connection = pymysql.connect(host=host, user=user, password=passwd, db=db)
    return db_connection


def execute_query(db_connection=None, query=None, query_params=()):
    if db_connection is None:
        print("No connection to the database found! Have you called connect_to_database() first?")
        return None

    if query is None or len(query.strip()) == 0:
        print("query is empty! Please pass a SQL query in query")
        return None

    # print("Executing %s with %s" % (query, query_params))

    cursor = db_connection.cursor(pymysql.cursors.DictCursor)
    cursor.execute(query, query_params)
    db_connection.commit()
    return cursor


def execute_many(db_connection=None, query=None, query_params=()):
    if db_connection is None:
        print("No connection to the database found! Have you called connect_to_database() first?")
        return None

    if query is None or len(query.strip()) == 0:
        print("query is empty! Please pass a SQL query in query")
        return None

    print("Executing %s with %s" % (query, query_params))

    cursor = db_connection.cursor(pymysql.cursors.DictCursor)
    cursor.executemany(query, query_params)
    db_connection.commit()
    return cursor


if __name__ == '__main__':
    print("Executing a sample query on the database using the credentials from db_credentials.py")
    db_connection = connect_to_database()
    query = "SELECT * from Users;"
    results = execute_query(db_connection, query)
    print("Printing results of %s" % query)

    for r in results.fetchall():
        print(r)
