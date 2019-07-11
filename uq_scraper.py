import asyncio
import aiohttp
import random
import sql_alchemy_tables as sql_tables
import datetime
import random
from bs4 import BeautifulSoup
import time
from databases import Database
import sqlalchemy

programs = sql_tables.programs
courses = sql_tables.courses
program_courses = sql_tables.program_courses


class Error(Exception):
    pass


# class InValidPageError():
class InvalidCoursePageError(Error):
    def __int__(self, message):
        self.message = message


class UqScraper:
    def __init__(self, program_url):
        self.program_url = program_url
        self.program_name = ""
        UAS = ("Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1",
               "Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0",
               "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10; rv:33.0) Gecko/20100101 Firefox/33.0",
               "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
               "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36",
               "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
               )

        ua = UAS[random.randrange(len(UAS))]
        headers = {"user-agent": ua}
        self.headers = headers
        self.database: Database = Database('postgresql://jeffvanpost:postpass@localhost/postgres_db', max_size=30)
        self.loop = asyncio.get_event_loop()
        self.num = random.randint(1, 200)

    async def connect(self):
        print(f"{self.num} at {datetime.datetime.now()} : Connected to Database")
        await self.database.connect()

    async def disconnect(self):
        print(f"{self.num} at {datetime.datetime.now()} : Disconnected from Database")
        await self.database.disconnect()

    async def run(self):

        start = time.time()
        await self.connect()
        program_entry = await self.database.fetch_one(programs.select().where(programs.c.url == self.program_url))

        print(f'{self.num} at {datetime.datetime.now()} : {self.program_url}')

        if not program_entry:

            uqcourses = await self.do_get_courses_from_program()

            if isinstance(uqcourses, Exception):
                await self.disconnect()
                return uqcourses

            courses_to_scrap = []
            for course in uqcourses:
                get_course = await self.database.fetch_one(
                    courses.select().where(courses.c.course_id == course[1][-8:]))
                if not get_course:
                    courses_to_scrap.append(course)

            ins = programs.insert().values(url=self.program_url, title=self.program_name)
            await self.database.execute(query=ins)

            print(f"{self.num} at {datetime.datetime.now()} : Scraping")
            await asyncio.gather(*(self.do_scrap_course(url[1]) for url in courses_to_scrap[0:]))

            for course in uqcourses:
                ins = program_courses.insert().values(
                    program_url=self.program_url,
                    course_id=course[1][-8:],
                )
                await self.database.execute(query=ins)

        returncourses = await self.query_courses_for_program()
        print(f"{self.num} at {datetime.datetime.now()} : Time Took : {time.time() - start}")
        await self.disconnect()
        return returncourses

    async def query_courses_for_program(self):
        query = sqlalchemy.select([program_courses, courses]) \
            .where(program_courses.c.program_url == self.program_url) \
            .where(program_courses.c.course_id == courses.c.course_id)

        selected_courses = await self.database.fetch_all(query=query)
        selected_courses = [dict(course) for course in selected_courses]

        return selected_courses

    async def do_get_courses_from_program(self):
        async with aiohttp.ClientSession() as session:
            return await self.get_courses_from_program_page(session)

    async def do_scrap_course(self, course_url):
        async with aiohttp.ClientSession() as session:
            await self.get_course_page(session, course_url)

    def css_selector(self, soup: BeautifulSoup, css: str) -> str:
        try:
            return soup.select_one(css).text
        except:
            return "No Value"

    async def get_course_page(self, session: aiohttp.ClientSession, course_url: str) -> dict:
        # try:
        async with session.get(course_url, ssl=False, headers=self.headers) as res:
            page = await res.text()
            soup = BeautifulSoup(page, "lxml")

            try:
                firstYear = soup.select_one("tbody")
                sems = firstYear.select(".course-offering-year")
                semesters = list(map(lambda x: int(x.text[9]), sems))
            except:
                semesters = []

            details = {
                "code": course_url[-8:],
                "title": self.css_selector(soup, "#course-title"),
                "prereq": self.css_selector(soup, "#course-prerequisite"),
                "summary": self.css_selector(soup, "#course-summary"),
                "url": course_url,
                "rec": self.css_selector(soup, "#course-recommended-prerequisite"),
                "semesters": semesters,
            }

            print(f'{self.num} at {datetime.datetime.now()} : {details["title"]}')
            ins = courses.insert().values(
                course_id=details["code"],
                summary=details["summary"],
                url=course_url,
                title=details["title"],
                semesters=details["semesters"],
                prereq=details["prereq"],
                rec=details["rec"]
            )
            try:
                await self.database.execute(query=ins)
            except Exception as e:
                print(f'{type(e)}, \n {e}')

            return await res.release()

    async def get_courses_from_program_page(self, session: aiohttp.ClientSession):
        try:
            async with session.get(self.program_url, ssl=False, headers=self.headers) as res:
                soup = BeautifulSoup(await res.text(), "lxml")
                self.program_name = soup.select_one("#page-head h1").text

                if self.program_name == "The program course list you requested could not be found." \
                        or self.program_name == "Error: Page not found"\
                        or self.program_name == "The plan course list you requested could not be found.":
                    print(f"Invalid program code : {self.program_url}")
                    return InvalidCoursePageError()

                courses = [course for course in soup.select(
                    "tr a") if len(course["href"]) > 15]
                courses = [[course.text.strip(), "https://my.uq.edu.au" + course["href"]]
                           for course in courses]
                fcourses = []
                for course in courses:
                    if course not in fcourses:
                        fcourses.append(course)

                return fcourses


        except aiohttp.client.ClientConnectionError as e:
            print(f"Invalid Url : {e}")
            return e
        except aiohttp.client.InvalidURL as e:
            print(f"Invalid Url : {e}")
            return e
        except AttributeError as e:
            print(f"Not a uq Program URL : {e}")
            return e
        except Exception as e:
            print(f"Some unhandled error occured : {e}\n of type {type(e)}")
            return e


async def main(url):
    scraper = UqScraper(url)
    # loop = asyncio.get_event_loop()
    uqcourses = await scraper.run()
    return uqcourses


# asyncio.run(main(";lksdjf;sdf"))
# asyncio.run(main("https://my.uq.edu.au/programs-courses/plan_display.html?acad_plan=FINANX2424"))
# asyncio.run(main("https://my.uq.edu.au/programs-courses/program_list.html?acad_prog=2369"))
