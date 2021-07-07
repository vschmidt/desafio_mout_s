FROM rabbitmq:3.8.3-management

COPY ./docker/prd/rabbitmq/rabbitmq.conf /etc/rabbitmq/rabbitmq.conf
COPY ./docker/prd/rabbitmq/definitions.json /etc/rabbitmq/definitions.json

CMD ["rabbitmq-server"]