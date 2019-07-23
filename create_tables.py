import psycopg2

commands = (
    """
    CREATE TABLE courses (
        course_id CHAR(8) PRIMARY KEY,
        summary TEXT, 
        url TEXT, 
        title TEXT, 
        semesters SMALLINT [] ,
        prereq TEXT, 
        rec TEXT 
    )
    """,
    """
    CREATE TABLE programs (
        url TEXT PRIMARY KEY, 
        title TEXT  
    )
    """,
    """
    CREATE TABLE program_courses (
        program_url TEXT NOT NULL, 
        course_id CHAR(8) NOT NULL, 
        PRIMARY KEY (program_url, course_id), 
        FOREIGN KEY (program_url)
            REFERENCES programs (url)
            ON UPDATE CASCADE ON DELETE CASCADE, 
        FOREIGN KEY (course_id)
            REFERENCES courses (course_id)
            ON UPDATE CASCADE ON DELETE CASCADE 
    )
    """
)


def connect():
    connection = None
    try:
        connection = psycopg2.connect(
            user="jeffvanpost",
            host="127.0.0.1",
            port="5432",
            database="postgres_db",
            password="postpass",
        )

        cursor = connection.cursor()

        for command in commands:
            cursor.execute(command)

        cursor.close()

        connection.commit()

        print(f"You are connected")

    except(Exception, psycopg2.Error) as error:
        print("Error while connecting to POstgreSQL", error)


    finally:
        if (connection):
            connection.close()
            print("PostGreSql connection closed")


connect()
