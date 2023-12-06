import os
import random
from uuid import uuid4, UUID

import pyotp
from fastapi import APIRouter, Depends, HTTPException, Request, Form
from sqlmodel import Session
from starlette.responses import JSONResponse
from starlette.templating import Jinja2Templates

from app.database import get_session
from app.models.models import Users, Accounts, AccountsType, Currencies
from app.services.auth_service import AuthService

router = APIRouter(prefix="", tags=["register"])
templates = Jinja2Templates(directory=os.path.abspath(os.path.expanduser('app/templates')))

auth_service: AuthService = AuthService()


@router.get("/register")
async def register(request: Request):
    return templates.TemplateResponse (
        "register_user.html",
        {
            "request": request,
        }
    )


@router.post("/register")
async def register(
        email: str = Form(...),
        password: str = Form(...),
        first_name: str = Form(...),
        surname: str = Form(...),
        session: Session = Depends(get_session)
):
    if session.query(Users).filter(Users.email == email).first():
        raise HTTPException(status_code=400, detail="Email already in use")

    user = Users(
        id=uuid4(),
        email=email,
        password=password,
        first_name=first_name,
        surname=surname,
        secret=pyotp.random_base32(),
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    file_name: str = auth_service.google_2f_auth(user)

    response = JSONResponse ({"qr_url": f"http://localhost:8000/static/{file_name}"})
    response.set_cookie (key="user_id", value=str (user.id))

    return response


@router.get("/verify_otp")
async def verify_otp(
    request: Request
):
    return templates.TemplateResponse(
        "verify_otp.html",
        {
            "request": request,
        }
    )


@router.post("/verify_otp")
async def verify_otp(
    request: Request,
    otp: str = Form(...),
    session: Session = Depends(get_session),
):
    user_id = UUID(request.cookies.get("user_id"))
    user: Users = session.query(Users).get({"id": user_id})

    if auth_service.verify_otp(otp, user):
        access_token = auth_service.generate_access_token(user_id)
        response = JSONResponse({})
        response.set_cookie(key="access_token", value=access_token)
        response.headers["Location"] = "http://localhost:8000/accounts"
    else:
        raise HTTPException(status_code=401, detail="verification failed")

    return response

