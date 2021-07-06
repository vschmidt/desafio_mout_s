#!/usr/bin/env python
import tornado.web
import json
import io
import json
import time
import pika
from pika.adapters import tornado_connection
from minio import Minio


class IndexHandler(tornado.web.RequestHandler):
    def initialize(self, minio_client):
        self.minio_client = minio_client

    def set_default_headers(self):
        self.set_header("Content-Type", "application/json")

    def get(self):
        id = self.get_argument("id", None)

        if id:
            response = self.minio_client.get_file(id)
            self.write(response)
        else:
            response = json.dumps({"message": "Not found"})
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

            credentials = pika.PlainCredentials("admin", "nimda")
            parameters = pika.ConnectionParameters(
                "rabbitmq", 5672, "notifications-vhost", credentials
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

        channel.basic_consume(
            queue="notifications-queue",
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

            self.connecting = True

            client = Minio(
                "minios3:9000", access_key="minio", secret_key="oinim123", secure=False
            )
            self.client = client

            self.connected = True
            self.connecting = False
        except:
            print(f"Connection to MinioS3 fail. Another try in 20 seconds")
            time.sleep(20)
            self.connect()

    def save_body(self, body):
        # Decode data
        data_decode = json.loads(body)

        # Upload data.
        filename = str(data_decode["id"]) + ".json"
        file = io.BytesIO(body)

        result = self.client.put_object(
            "notifications",
            filename,
            file,
            file.getbuffer().nbytes,
        )

        print(
            "created {0} object; etag: {1}".format(result.object_name, result.etag),
        )

    def get_file(self, id):
        # Get filename
        filename = str(id) + ".json"

        response = None
        try:
            response = self.client.get_object("notifications", filename)
            # Read data from response.
            response_data = response.read()
        except:
            response_data = json.dumps({"message": "Not found"})
        finally:
            if response:
                response.close()
                response.release_conn()

        return response_data
