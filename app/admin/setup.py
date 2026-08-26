from fastapi import FastAPI
from sqladmin import Admin

from app.admin.auth import build_admin_auth
from app.admin.views import ADMIN_VIEWS
from app.core.database import engine


def init_admin(app: FastAPI) -> Admin:
    admin = Admin(app=app, engine=engine, authentication_backend=build_admin_auth())
    for view in ADMIN_VIEWS:
        admin.add_view(view)
    return admin
