#!/usr/bin/env python
import tornado.web
import json
import os


class IndexHandler(tornado.web.RequestHandler):
    def initialize(self, minio_client):
        self.minio_client = minio_client

    def set_default_headers(self):
        DEV_MODE = os.getenv("DEV_MODE", False)

        self.set_header("Content-Type", "application/json")

        if DEV_MODE:
            # Browsers CORS policy blocks localhost to localhost requests
            self.set_header("access-control-allow-origin", "*")
            self.set_header("Access-Control-Allow-Headers", "*")
            self.set_header("Access-Control-Allow-Methods", "*")

    def options(self):
        self.set_status(204)
        self.finish()

    def get(self):
        """Return notification in MinioS3
        ---
        tags: [minios3]
        summary: Return the id and notification
        description: Return the id and notification
        responses:
            200:
                description: Index page
                content:
                    application/html:
                        schema:
                            type: array
        """
        id = self.get_argument("id", None)

        if id:
            response = self.minio_client.get_file(id)
            self.write(response)
        else:
            response = json.dumps({"notification": "Not found"})
            self.write(response)
