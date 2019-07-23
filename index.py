from sanic import Sanic
from sanic import response
from sanic.response import json
from sanic_cors import CORS
import uq_scraper as uq_scraper
from uq_scraper import InvalidCoursePageError
import aiohttp
import json
import re

app = Sanic()
CORS(app)

regex = r"https://my\.uq\.edu\.au/programs-courses/" \
        r"(plan_display\.html\?acad_plan" \
        r"|program_list\.html\?acad_prog)" \
        r"=([A-Z]{6})?[0-9]{4}"


@app.route("/", methods=["POST", "GET"])
async def test(request):
    url = json.loads(request.body)["courseUrl"]

    if not re.search(regex, url):
        text = f"Invalid Url : {url}"
        print(text)
        return response.text(text)

    uqcourses = await uq_scraper.main(url)

    if isinstance(uqcourses, Exception):
        if isinstance(uqcourses, aiohttp.client.ClientConnectionError):
            text = f"Invalid Url : {uqcourses}"
            print(text)
            return response.text(text)
        if isinstance(uqcourses, aiohttp.client.InvalidURL):
            text = f"Invalid Url : {uqcourses}"
            print(text)
            return response.text(text)
        elif isinstance(uqcourses, AttributeError):
            text = f"Not a uq URL : {url}"
            print(text)
            return response.text(text)
        elif isinstance(uqcourses, InvalidCoursePageError):
            text = f"Invalid program code : {url}"
            print(text)
            return response.text(text)
        else:
            text = f"Some unhandled error occurred, Sorry"
            print(text)
            return response.text(text)

    return response.json({"Courses": uqcourses})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000)
