from sanic import Sanic
from sanic import response
from sanic.response import json
from sanic_cors import CORS, cross_origin
import uq_scraper as uq_scraper
from uq_scraper import InvalidCoursePageError
import aiohttp
import json

app = Sanic()
CORS(app)


@app.route("/", methods=["POST", "GET"])
async def test(request):
    url = json.loads(request.body)["courseUrl"]

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
            print (text)
            return response.text(text)
        elif isinstance(uqcourses, InvalidCoursePageError):
            text = f"Invalid program code : {url}"
            print(text)
            return response.text(text)
        else:
            text = f"Some unhandled error occured, Sorry"
            print(text)
            return response.text(text)

    return response.json({"Courses": uqcourses})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000)
