from app.sqlalchemy_models import users_sql
from app.config import config as app_config
from app.services.database import Base


config = context.config
config.set_main_option("sqlalchemy.url", app_config.DB_CONFIG)
target_metadata = Base.metadata
