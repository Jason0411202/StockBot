import pymysql

# Connect to the database
connection = pymysql.connect(
    host='localhost',
    user='root',
    password='Jason910904',
)

# Create a cursor object
cursor = connection.cursor()
