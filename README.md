# Mout's challenge

This project performs 2 microservices (A and B) and integrates 3 main technologies:
1. [Tornado](https://www.tornadoweb.org/)
2. [RabbitMQ](https://www.rabbitmq.com/)
3. [Minio S3](https://min.io/)

## How it works

In **service A**, messages can be sent via UI or API to **RabbtMQ** queue and retrieve messages from **service B**.

The **service B** processes the **RabbitMQ** queues, saves the messages in **MinioS3** and processes the **service A** requests.

The image below show how this works:



![challenge](https://i.imgur.com/0FV3xZZ.png)


# How do I run?

To run this project, you need internet access and the docker configured on your machine.

The project has 2 configurations:
* Development Mode
* Production Mode

### Develop mode

```
$ docker-compose up -d
```

### Production mode

```
$ docker-compose -f docker-compose-prod.yaml up -d
```

### Environment variables

Environment variables can be defined in the **.env** files in the folder for development and production modes.

### The UI

After docker is ready, you can access the UI in 127.0.0.1:"SERVICE_PORT" set in **service_a/.env** file.


**Index page**

![index](https://i.imgur.com/2ZqF6M0.png)

**Search page**


![search](https://i.imgur.com/mFgZk0f.png)


**Success page**


![success](https://i.imgur.com/bpStxMV.png)


# Swagger docs
Swagger docs is present in **docs** folder.  