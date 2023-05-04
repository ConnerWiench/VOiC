import mysql.connector # import the mysql.connector module
import os

# define a function to create a database connection
def get_db():
    # establish a connection to the database using the specified parameters
    conn = mysql.connector.connect(
    host=os.getenv("DB_HOST"), # the host name where the MySQL server is running
    user=os.getenv("DB_USER"),  # the username for accessing the database
    password=os.getenv("DB_PASSWORD"), # the password for the specified user
    database=os.getenv("DB_NAME"),    # the name of the database to be used
    )

    # return the connection object to the calling function
    return conn

#Note: Its a good practice to use .env file if you dont want other to know about your database information