#!/usr/bin/env python
import tornado.web
import time
import pika
from handlers import IndexHandler, PikaClient, MinioS3Client

HANDLERS = [(r"/", IndexHandler)]
settings = {
    "debug": True,
}
port = 8889

app = tornado.web.Application(
    HANDLERS,
    **settings,
)


def check_rabit():
    while True:
        try:
            credentials = pika.PlainCredentials("admin", "nimda")
            parameters = pika.ConnectionParameters(
                "rabbitmq", 5672, "notifications-vhost", credentials
            )
            connection = pika.BlockingConnection(parameters)
            connection.close()
            break
        except:
            print(f"Connection with RabitMQ fail. Another try in 20 seconds")
            time.sleep(20)


def main():
    io_loop = tornado.ioloop.IOLoop.instance()
    minio_client = MinioS3Client()
    app.pc = PikaClient(io_loop, minio_client)
    app.pc.connect()
    app.listen(port)

    try:
        io_loop.start()
    except KeyboardInterrupt:
        io_loop.stop()

    print("listen {}".format(port))


if __name__ == "__main__":
    check_rabit()
    main()
