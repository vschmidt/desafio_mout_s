import tornado.ioloop
import tornado.web
import json
import time
import os
import pika
import swagger_ui
from init_swagger import generate_swagger_file

SWAGGER_API_OUTPUT_FILE = "./swagger_service_a.json"


class IndexHandler(tornado.web.RequestHandler):
    """
    IndexHandler
    """

    def get(self):
        """Return index page
        ---
        tags: [index]
        summary: Return index page
        description: Index page is UI interface with users
        responses:
            200:
                description: Index page
                content:
                    application/html:
                        schema:
                            type: array
        """
        self.render("pages/index.html", title="Send interface")

    def post(self):
        id = self.get_argument("id", None)  # Get id
        notification = self.get_argument("notification", None)  # Get notification
        payload = {"id": id, "notification": notification}  # Create payload

        # Get rabbitmq env variables
        RABBITMQ_USER = os.getenv("RABBITMQ_USER", None)
        RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", None)
        RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", None)
        RABBITMQ_PORT = os.getenv("RABBITMQ_PORT", None)
        RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST", None)
        RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", None)
        RABBITMQ_EXCHANGE = os.getenv("RABBITMQ_EXCHANGE", None)

        # Create connection
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
        parameters = pika.ConnectionParameters(
            RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_VHOST, credentials
        )
        connection = pika.BlockingConnection(parameters)

        channel = connection.channel()  # Open channel
        channel.queue_declare(
            queue=RABBITMQ_QUEUE,
            durable=True,
            auto_delete=False,
            arguments={"x-max-length": 5, "x-queue-type": "classic"},
        )

        channel.basic_publish(
            exchange=RABBITMQ_EXCHANGE,
            routing_key="notifications",
            body=json.dumps(payload),
        )  # Publish message

        connection.close()  # Close connection

        self.render(
            "pages/success.html", title="Success page", notification=notification
        )


class SearchHandler(tornado.web.RequestHandler):
    def get(self):
        # Get env variables
        SERVICEB_HOST = os.getenv("SERVICEB_HOST", None)
        SERVICEB_PORT = os.getenv("SERVICEB_PORT", None)

        self.render(
            "pages/search.html",
            title="Search interface",
            serviceb_host=SERVICEB_HOST,
            serviceb_port=SERVICEB_PORT,
        )


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

    return app


if __name__ == "__main__":
    SERVICE_PORT = os.getenv("SERVICE_PORT", None)
    check_rabit()
    app = make_app()
    app.listen(SERVICE_PORT)
    print(f"Service A running in: {SERVICE_PORT}")
    tornado.ioloop.IOLoop.current().start()
