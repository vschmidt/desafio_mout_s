FROM python:3.8

ENV PYTHONUNBUFFERED 1

WORKDIR /code

ADD requirements/service_b/* /code/
RUN pip install -r dev.txt

CMD [ "sh", "docker/dev/service_b/container-start.sh"]
