import tornado.ioloop
import tornado.web
import os
import swagger_ui
from init_swagger import generate_swagger_file
from utils import check_rabit
from handlers import IndexHandler, SearchHandler

SWAGGER_API_OUTPUT_FILE = "./docs/swagger_service_a.json"


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
