import os

from fastapi import APIRouter, Depends, HTTPException, Request, Form
from sqlmodel import Session
from starlette.responses import JSONResponse
from starlette.templating import Jinja2Templates

from app.database import get_session
from app.models.models import Users
from app.services.auth_service import AuthService

templates = Jinja2Templates(directory=os.path.abspath(os.path.expanduser('app/templates')))
router = APIRouter()


@router.get("/login")
async def login(
    request: Request
):
    return templates.TemplateResponse (
        "login.html",
        {
            "request": request,
        }
    )


@router.post("/login")
async def login(
        email: str = Form(...),
        password: str = Form(...),
        session: Session = Depends(get_session),
):
    auth_service: AuthService = AuthService()
    user = session.query(Users).filter(Users.email == email).first()

    if user is None or user.password != password:
        raise HTTPException (status_code=401, detail="Incorrect login or password")

    access_token = auth_service.generate_access_token(user.id)
    response = JSONResponse({"message": "You're logged in"})
    response.set_cookie(key="access_token", value=access_token)
    return response


@router.get("/")
def login_signup(
    request: Request
):
    return templates.TemplateResponse (
        "homepage.html",
        {
            "request": request,
        }
    )

