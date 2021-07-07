#!/usr/bin/env python
import os
import tornado.ioloop
import tornado.web
from tornado.testing import AsyncHTTPTestCase
from handlers import IndexHandler, SearchHandler


def make_app():
    DEV_MODE = os.getenv("DEV_MODE", None)

    settings = {
        "debug": DEV_MODE,
    }

    HANDLERS = [
        (r"/", IndexHandler),
        (r"/search", SearchHandler),
    ]

    app = tornado.web.Application(
        HANDLERS,
        **settings,
    )

    return app


class TestHandlersApp(AsyncHTTPTestCase):
    def get_app(self):
        return make_app()

    def test_homepage(self):
        response = self.fetch("/")
        self.assertEqual(response.code, 200)

    def test_searchpage(self):
        response = self.fetch("/search")
        self.assertEqual(response.code, 200)
