#!/usr/bin/env python
import tornado.web
import time
import pika
import os
from handlers import IndexHandler
from clients import PikaClient, MinioS3Client
import swagger_ui
from init_swagger import generate_swagger_file

SWAGGER_API_OUTPUT_FILE = "./docs/swagger_service_b.json"


def check_rabit():
    """
    Check if RabitMQ is ready
    """
    # Get rabbitmq env variables
    RABBITMQ_USER = os.getenv("RABBITMQ_USER", None)
    RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", None)
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", None)
    RABBITMQ_PORT = os.getenv("RABBITMQ_PORT", None)
    RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST", None)

    while True:
        try:
            credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
            parameters = pika.ConnectionParameters(
                RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_VHOST, credentials
            )
            connection = pika.BlockingConnection(parameters)
            connection.close()
            break
        except:
            print(f"Connection with RabitMQ fail. Another try in 20 seconds")
            time.sleep(20)


def main():
    # get env variables
    DEV_MODE = os.getenv("DEV_MODE", False)
    SERVICE_PORT = os.getenv("SERVICE_PORT", False)

    settings = {
        "debug": DEV_MODE,
    }

    io_loop = tornado.ioloop.IOLoop.instance()

    minio_client = MinioS3Client()

    HANDLERS = [(r"/", IndexHandler, {"minio_client": minio_client})]

    app = tornado.web.Application(
        HANDLERS,
        **settings,
    )
    # Generate a fresh Swagger file
    generate_swagger_file(handlers=HANDLERS, file_location=SWAGGER_API_OUTPUT_FILE)

    # Start the Swagger UI. Automatically generated swagger.json can also
    # be served using a separate Swagger-service.
    swagger_ui.tornado_api_doc(
        app,
        config_path=SWAGGER_API_OUTPUT_FILE,
        url_prefix="/swagger/spec.html",
        title="Car Brand API",
    )

    app.pc = PikaClient(io_loop, minio_client)
    app.pc.connect()
    app.listen(SERVICE_PORT)

    try:
        io_loop.start()
    except KeyboardInterrupt:
        io_loop.stop()

    print("listen {}".format(SERVICE_PORT))


if __name__ == "__main__":
    check_rabit()
    main()
