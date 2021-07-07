FROM python:3.8

ENV PYTHONUNBUFFERED 1

WORKDIR /code

ADD requirements/service_a/* /code/
RUN pip install -r prd.txt

CMD [ "sh", "docker/prd/service_a/container-start.sh"]
