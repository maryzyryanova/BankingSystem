from fastapi import FastAPI

from app.routing.login import router as login_router
from app.routing.register import router as register_router
from app.routing.accounts import router as accounts_router


def create_app() -> FastAPI:
    app = FastAPI(debug=True)
    return app


app = create_app()
app.include_router(login_router)
app.include_router(register_router)
app.include_router(accounts_router)
