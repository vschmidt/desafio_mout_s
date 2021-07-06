#!/usr/bin/env python
import tornado.web
import json
import io
import json
import time
import pika
import os
from pika.adapters import tornado_connection
from minio import Minio


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
        id = self.get_argument("id", None)

        if id:
            response = self.minio_client.get_file(id)
            self.write(response)
        else:
            response = json.dumps({"notification": "Not found"})
            self.write(response)


class PikaClient:
    def __init__(self, io_loop, minio_client):
        self.io_loop = io_loop
        self.minio = minio_client
        self.connected = False
        self.connecting = False
        self.connection = None
        self.channel = None

    def connect(self):
        try:
            if self.connecting:
                return

            # Get rabbit envs
            RABBITMQ_USER = os.getenv("RABBITMQ_USER", None)
            RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", None)
            RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", None)
            RABBITMQ_PORT = os.getenv("RABBITMQ_PORT", None)
            RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST", None)

            # Create connection
            credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
            parameters = pika.ConnectionParameters(
                RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_VHOST, credentials
            )

            self.connection = tornado_connection.TornadoConnection(
                parameters,
                custom_ioloop=self.io_loop,
                on_open_callback=self.on_connected,
            )
            self.connection.add_on_close_callback(self.on_closed)
            self.connecting = True
        except:
            print(f"Connection with RabitMQ fail. Another try in 20 seconds")
            time.sleep(20)
            self.connect()

    def on_connected(self, conn):
        print("connected")
        self.connected = True
        self.connection = conn
        self.connection.channel(channel_number=1, on_open_callback=self.on_channel_open)

    def on_message(self, channel, method, properties, body):
        print(" [x] Received %r" % body)
        self.minio.save_body(body)

    def on_channel_open(self, channel):
        self.channel = channel

        RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", None)

        channel.basic_consume(
            queue=RABBITMQ_QUEUE,
            on_message_callback=self.on_message,
            auto_ack=True,
        )
        return

    def on_closed(self, conn, c):
        self.io_loop.stop()


class MinioS3Client:
    def __init__(self):
        self.connected = False
        self.connecting = False
        self.client = None
        self.connect()

    def connect(self):
        try:
            if self.connecting:
                return

            # Get minio envs
            MINIO_USER = os.getenv("MINIO_USER", None)
            MINIO_PASSWORD = os.getenv("MINIO_PASSWORD", None)
            MINIO_HOST = os.getenv("MINIO_HOST", None)
            MINIO_PORT = os.getenv("MINIO_PORT", None)

            self.connecting = True

            client = Minio(
                f"{MINIO_HOST}:{MINIO_PORT}",
                access_key=MINIO_USER,
                secret_key=MINIO_PASSWORD,
                secure=False,
            )
            self.client = client

            self.connected = True
            self.connecting = False
        except:
            print(f"Connection to MinioS3 fail. Another try in 20 seconds")
            time.sleep(20)
            self.connect()

    def save_body(self, body):
        # Get minio envs
        MINIO_BUCKET = os.getenv("MINIO_BUCKET", None)

        # Decode data
        data_decode = json.loads(body)

        # Upload data.
        filename = str(data_decode["id"]) + ".json"
        file = io.BytesIO(body)

        result = self.client.put_object(
            MINIO_BUCKET,
            filename,
            file,
            file.getbuffer().nbytes,
        )

        print(
            "created {0} object; etag: {1}".format(result.object_name, result.etag),
        )

    def get_file(self, id):
        # Get minio envs
        MINIO_BUCKET = os.getenv("MINIO_BUCKET", None)

        # Get filename
        filename = str(id) + ".json"

        response = None
        try:
            response = self.client.get_object(MINIO_BUCKET, filename)
            # Read data from response.
            response_data = response.read()
        except:
            response_data = json.dumps({"notification": "Not found"})
        finally:
            if response:
                response.close()
                response.release_conn()

        return response_data
