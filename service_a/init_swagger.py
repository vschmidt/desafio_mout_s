import json
import os
from apispec import APISpec
from apispec.exceptions import APISpecError
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.tornado import TornadoPlugin

SERVICE_HOST = os.getenv("SERVICE_HOST", None)
SERVICE_PORT = os.getenv("SERVICE_PORT", None)


def generate_swagger_file(handlers, file_location):
    """Automatically generates Swagger spec file based on RequestHandler
    docstrings and saves it to the specified file_location.
    """
    spec = APISpec(
        title="Service A API",
        version="0.0.1",
        openapi_version="3.0.2",
        info=dict(description="Documentation for the Service A API"),
        plugins=[TornadoPlugin(), MarshmallowPlugin()],
        servers=[
            {
                "url": f"http://{SERVICE_HOST}:{SERVICE_PORT}/",
                "description": "Ambiente do sistema",
            },
        ],
    )
    # Looping through all the handlers and trying to register them.
    for handler in handlers:
        try:
            spec.path(urlspec=handler)
        except APISpecError: # Handlers without docstring will raise errors.            
            pass

    # Write the Swagger file into specified location.
    with open(file_location, "w", encoding="utf-8") as file:
        json.dump(spec.to_dict(), file, ensure_ascii=False, indent=4)
