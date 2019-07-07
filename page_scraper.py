import asyncio
import requests
import time
import aiohttp
import aiofiles
import random
from bs4 import BeautifulSoup

UAS = ("Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1",
       "Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0",
       "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10; rv:33.0) Gecko/20100101 Firefox/33.0",
       "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
       "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36",
       "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
       )

ua = UAS[random.randrange(len(UAS))]
headers = {"user-agent": ua}


def css_selector(soup : BeautifulSoup, css : str) -> str:
    try:
        return soup.select_one(css).text
    except:
        return "No Value"

async def getCoursePage(session, url):
    try:
        async with session.get(url, ssl=False, headers=headers) as res:
            page = await res.text()
            soup = BeautifulSoup(page, "lxml")

            try:
                firstYear = soup.select_one("tbody")
                sems = firstYear.select(".course-offering-year")
                semesters = list(map(lambda x: int(x.text[9]), sems))
            except: 
                semesters = []


            details = {
                "code" : url[-8:],
                "title" : css_selector(soup, "#course-title"), 
                "prereq" : css_selector(soup, "#course-prerequisite"),
                "summary" : css_selector(soup, "#course-summary"),
                "url" : url, 
                "rec" : css_selector(soup, "#course-recommended-prerequisite"),
                "semesters" : semesters, 
            }

            print(details["title"])

            async with aiofiles.open("courses.json", "a") as f:
                await f.write(f"{details},\n")

            return await res.release()

    except:
        return (f"Failed to connected to: {url}")


async def getProgramPage(session, url):
    try:
        async with session.get(url, ssl=False, headers=headers) as res:
            page = await res.text()
            soup = BeautifulSoup(page, "lxml")
            title = soup.select_one(".trigger")
            if title is not None:
                print(title)
            else:
                print(f"Failed for: {url}")

            return await res.release()

    except:
        return f"Failed to connected to: {url}"


def getCourseList(programurl):
    page = requests.get(programurl).text
    soup = BeautifulSoup(page, "lxml")
    courses = [course for course in soup.select(
        "tr a") if len(course["href"]) > 15]
    courses = [[course.text.strip(), "https://my.uq.edu.au" + course["href"]]
                 for course in courses]
    fcourses = []
    for course in courses:
        if course not in fcourses:
            fcourses.append(course)
    return fcourses


def getProgramList():
    url = "https://my.uq.edu.au/programs-courses/browse.html?level=ugpg"
    page = requests.get(url).text
    soup = BeautifulSoup(page, "lxml")
    programs = [[course.text.strip(), "https://my.uq.edu.au" + course["href"]]
                for course in soup.select(".plan a")]
    return programs


async def main(url):
    async with aiohttp.ClientSession() as session:
        await getCoursePage(session, url)


# programs = getProgramList()

# programs = [[program[0],"https://my.uq.edu.au/programs-courses/plan_display.html?acad_plan=" + program[1][-10:]]  for program in programs if "plan.html?acad_plan" in program[1]]

# for i in range(1500):
#     programs.pop()
# print(programs)

# loop = asyncio.get_event_loop()
# loop.run_until_complete(
#     asyncio.gather(*(main(url[1]) for url in programs))
# )


def courseDestroyer(url):
    f = open("courses.json", "w")
    f.write("[\n")
    f.close()

    start = time.time()

    uqcourses = getCourseList(url)

    print(len(uqcourses))

    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        asyncio.gather(*(main(url[1]) for url in uqcourses[1:40]))
    )

    f = open("courses.json","a") 
    f.write("]")
    f.close() 

    print(f"Time : {time.time()-start}")


courseDestroyer(
    "https://my.uq.edu.au/programs-courses/program_list.html?acad_prog=2342")
