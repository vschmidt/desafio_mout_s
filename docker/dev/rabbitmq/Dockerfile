FROM rabbitmq:3.8.3-management

COPY ./docker/dev/rabbitmq/rabbitmq.conf /etc/rabbitmq/rabbitmq.conf
COPY ./docker/dev/rabbitmq/definitions.json /etc/rabbitmq/definitions.json

CMD ["rabbitmq-server"]