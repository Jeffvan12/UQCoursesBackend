from databases import Database
import asyncio
import sqlalchemy

metadata = sqlalchemy.MetaData()

courses = sqlalchemy.Table (
    "courses",
    metadata,
    sqlalchemy.Column("course_id", sqlalchemy.CHAR(length=8), primary_key=True),
    sqlalchemy.Column("summary", sqlalchemy.TEXT),
    sqlalchemy.Column("title", sqlalchemy.TEXT),
    sqlalchemy.Column("semesters", sqlalchemy.ARRAY(sqlalchemy.SMALLINT)),
    sqlalchemy.Column("url", sqlalchemy.TEXT),
    sqlalchemy.Column("prereq", sqlalchemy.TEXT),
    sqlalchemy.Column("rec", sqlalchemy.TEXT),
)


programs = sqlalchemy.Table (
    "programs",
    metadata,
    sqlalchemy.Column("url", sqlalchemy.TEXT, primary_key=True),
    sqlalchemy.Column("title", sqlalchemy.TEXT),
)

program_courses = sqlalchemy.Table (
    "program_courses",
    metadata,
    sqlalchemy.Column("program_url", sqlalchemy.TEXT, sqlalchemy.ForeignKey("programs.url"), nullable=False),
    sqlalchemy.Column("course_id", sqlalchemy.CHAR(length=8), sqlalchemy.ForeignKey("courses.course_id"), nullable=False),
    sqlalchemy.PrimaryKeyConstraint("program_url", "course_id"),

)

async def main():
    database : Database = Database('postgresql://jeffvanpost:postpass@localhost/postgres_db')
    await database.connect()

    # Inserting
    # ins = programs.insert().values(url = "thing.com", title = "All things")
    # rows = await database.execute(query=ins)

    ins = program_courses.insert().values(program_url = "thing.com", course_id = "CSSE2310")
    await database.execute(query=ins)

    #Retreiving , use list (rows.values) to get values
    # query = courses.select()
    # rows = await database.fetch_one(query)
    # thing = dict(rows)









asyncio.run(main())
