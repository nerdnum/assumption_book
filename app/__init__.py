from contextlib import asynccontextmanager

from fastapi import FastAPI

# Temporary imports for development
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import config_manager, get_config
from app.services.database import sessionmanager


def init_app(config_file: str = "config.json"):
    lifespan = None

    config_manager.init(config_file)
    config = get_config()

    sessionmanager.init(config["db_url"], config["config_name"])

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        yield
        if sessionmanager._engine is not None:
            await sessionmanager.close()

    server = FastAPI(title="AssumptionBook", lifespan=lifespan)
    if config["config_name"] == "testing":
        server.title = "testing"

    server.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # from app.views.projects import router as project_router
    # server.include_router(project_router, prefix="/api/v1", tags=["projects"])

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
        "/api/v1/static",
        StaticFiles(directory="app/static", html=True),
        name="static",
    )

    server.include_router(project_router, prefix="/api/v1", tags=["projects"])

    from app.views.auth_view import router as auth_router

    server.include_router(auth_router, prefix="/api/v1", tags=["auth"])

    from app.views.users_view import router as user_router

    server.include_router(user_router, prefix="/api/v1", tags=["users"])

    from app.views.roles_view import router as role_router

    server.include_router(role_router, prefix="/api/v1", tags=["roles"])

    from app.views.setting_types_view import router as setting_type_router

    server.include_router(setting_type_router, prefix="/api/v1", tags=["setting_types"])

    from app.views.settings_view import router as setting_router

    server.include_router(setting_router, prefix="/api/v1", tags=["settings"])

    from app.views.documents_view import router as document_router

    server.include_router(document_router, prefix="/api/v1", tags=["documents"])

    return server
