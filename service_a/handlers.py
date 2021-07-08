import tornado.web
import json
import os
import pika


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
        """Return success page
        ---
        tags: [index]
        summary: Send payload to service B and return success page
        description: Send payload to service B and return success page
        responses:
            200:
                description: Success page
                content:
                    application/html:
                        schema:
                            type: array
        """
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
        """Return search page
        ---
        tags: [search]
        summary: Return search page
        description: Return search page
        responses:
            200:
                description: Success page
                content:
                    application/html:
                        schema:
                            type: array
        """
        # Get env variables
        SERVICEB_HOST = os.getenv("SERVICEB_HOST", None)
        SERVICEB_PORT = os.getenv("SERVICEB_PORT", None)

        self.render(
            "pages/search.html",
            title="Search interface",
            serviceb_host=SERVICEB_HOST,
            serviceb_port=SERVICEB_PORT,
        )
