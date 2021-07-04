import tornado.ioloop
import tornado.web
import json
import time
import os
import pika


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("pages/index.html", title="Send interface")

    def post(self):
        id = self.get_argument("id", None)  # Get id
        notification = self.get_argument("notification", None)  # Get notification
        payload = {"id": id, "notification": notification}  # Create payload

        credentials = pika.PlainCredentials("admin", "nimda")
        parameters = pika.ConnectionParameters(
            "rabbitmq", 5672, "notifications-vhost", credentials
        )
        connection = pika.BlockingConnection(parameters)

        channel = connection.channel()  # Open channel
        channel.queue_declare(
            queue="notifications-queue",
            durable=True,
            auto_delete=False,
            arguments={"x-max-length": 5, "x-queue-type": "classic"},
        )

        channel.basic_publish(
            exchange="notifications-exchange",
            routing_key="notifications",
            body=json.dumps(payload),
        )  # Publish message

        connection.close()

        self.render(
            "pages/success.html", title="Success page", notification=notification
        )


class SearchHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("pages/search.html", title="Search interface")


def check_rabit():
    """
    Check if RabitMQ is ready
    """
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


def make_app():
    settings = {
        "debug": True,
    }

    return tornado.web.Application(
        [
            (r"/", IndexHandler),
            (r"/search", SearchHandler),
        ],
        **settings,
    )


if __name__ == "__main__":
    check_rabit()
    app = make_app()
    app.listen(8888)
    print("Service A running in: 8888")
    tornado.ioloop.IOLoop.current().start()
