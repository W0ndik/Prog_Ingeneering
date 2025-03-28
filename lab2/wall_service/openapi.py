from fastapi.openapi.utils import get_openapi
from main import app
import json, os

os.makedirs("/app/api_specs", exist_ok=True)
with open("/app/api_specs/wall_service.openapi.json", "w") as f:
    json.dump(get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes
    ), f, indent=2)