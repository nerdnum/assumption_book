from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Header, HTTPException, Request

# Temporary imports for development
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from typing_extensions import Annotated

from app.config import config_manager, get_config
from app.services.database import sessionmanager


async def verify_auth(authorization: Annotated[str, Header()]):
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")


def check_request(request: Request):
    return request


def init_app(config_file: str = "config.json"):

    config_manager.init(config_file)
    config = get_config()

    api_prefix = "/api/" + config["api_version"]

    sessionmanager.init(config["db_url"], config["config_name"])

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        yield
        if sessionmanager._engine is not None:
            await sessionmanager.close()

    server = FastAPI(
        title="AssumptionBook",
        lifespan=lifespan,
    )
    if config["config_name"] == "testing":
        server.title = "testing"

    from app.views.auth_view import get_current_user

    @server.middleware("http")
    async def db_session_middleware(request, call_next):
        # unauthenticated_response = JSONResponse(
        #     status_code=401, content={"error_msg": "Not authenticated"}
        # )
        # if config["enforce_authentication"] and request.url.path not in [
        #     "/docs",
        #     "/openapi.json",
        #     "/redoc",
        #     api_prefix + "/auth/token",
        # ]:
        #     auth_token = request.headers.get("Authorization")
        #     if not auth_token:
        #         return unauthenticated_response
        #     try:
        #         user = await get_current_user(auth_token)
        #         if not user:
        #             return unauthenticated_response
        #     except HTTPException:
        #         return unauthenticated_response
        response = await call_next(request)
        return response

    server.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # from app.views.projects import router as project_router
    # server.include_router(project_router, prefix=api_prefix, tags=["projects"])

    # top_router = APIRouter(prefix="/api/v1/{projectSlug}")

    # from app.views.components import router as component_router
    # top_router.include_router(component_router)

    # server.include_router(top_router)

    from app.views.components_view import router as component_router
    from app.views.projects_view import router as project_router

    project_router.include_router(
        component_router,
        prefix="/{project_id:int}",
        tags=["components"],
    )

    server.mount(
        api_prefix + "/static",
        StaticFiles(directory="app/static", html=True),
        name="static",
    )

    server.include_router(project_router, prefix=api_prefix, tags=["projects"])

    from app.views.auth_view import router as auth_router

    server.include_router(auth_router, prefix=api_prefix, tags=["auth"])

    from app.views.users_view import router as user_router

    server.include_router(user_router, prefix=api_prefix, tags=["users"])

    from app.views.roles_view import router as role_router

    server.include_router(role_router, prefix=api_prefix, tags=["roles"])

    from app.views.setting_types_view import router as setting_type_router

    server.include_router(
        setting_type_router, prefix=api_prefix, tags=["setting-types"]
    )

    from app.views.settings_view import router as setting_router

    server.include_router(setting_router, prefix=api_prefix, tags=["settings"])

    from app.views.documents_view import router as document_router

    server.include_router(document_router, prefix=api_prefix, tags=["documents"])

    from app.views.websocket import router as websocket_router

    server.include_router(websocket_router, prefix=api_prefix, tags=["doc_export"])

    return server
