import sqlalchemy

metadata = sqlalchemy.MetaData()

courses = sqlalchemy.Table(
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

programs = sqlalchemy.Table(
    "programs",
    metadata,
    sqlalchemy.Column("url", sqlalchemy.TEXT, primary_key=True),
    sqlalchemy.Column("title", sqlalchemy.TEXT),
)

program_courses = sqlalchemy.Table(
    "program_courses",
    metadata,
    sqlalchemy.Column("program_url", sqlalchemy.TEXT, sqlalchemy.ForeignKey("programs.url"), nullable=False),
    sqlalchemy.Column("course_id", sqlalchemy.CHAR(length=8), sqlalchemy.ForeignKey("courses.course_id"),
                      nullable=False),
    sqlalchemy.PrimaryKeyConstraint("program_url", "course_id"),
)
