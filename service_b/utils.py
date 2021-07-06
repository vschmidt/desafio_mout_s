import os
import pika
import time


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
