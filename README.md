# python_rest_tutorial

[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=RVJC5VUM5ZEW8&source=url)
[![License](http://img.shields.io/badge/Licence-MIT-brightgreen.svg)](LICENSE.md)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/53014a434fb340f2afde9853e2314a8a)](https://www.codacy.com/gh/DewaldOosthuizen/python_rest_tutorial/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=DewaldOosthuizen/python_rest_tutorial&amp;utm_campaign=Badge_Grade)

Example project to show how to to build and design RESTful web services using Python, Flask, Docker and MongoDB.

Here is an article you can follow to create this project from the beginning:
<https://www.dvt.co.za/news-insights/insights/item/355-restful-web-services-using-python-flask-docker-and-mongodb>

## Docker and docker-compose

Inside the root project you can run

```shell
sudo docker-compose build
```

and then run the folowing to start the container and expose the API:

```shell
sudo docker-compose up
```

Once the container is running, you can access it by opening your browser and typing in localhost:5000/hello. This should
display a "Hello World!" message.

There are also other endpoints to test with, and can be found in the article mentioned at the top.

## Using postman

When using postman to test your rest endpoints, be sure to add content-type: application/json to your headers.

If you don't want to specify content type in the header then you can use
request.get_json(force=True) inside your endpoint when fetching the data from the request
to force the data to be read as JSON.

For reference have a look at <https://github.com/DewaldOosthuizen/python_rest_tutorial/issues/1>
