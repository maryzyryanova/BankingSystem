from uuid import UUID

import pyotp
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session
from starlette.responses import JSONResponse

from app.services.auth_service import AuthService
from app.database import get_session
from app.models.models import Users

router = APIRouter()


@router.post("/login")
async def login(
        email: str,
        password: str,
        session: Session = Depends(get_session),
):
    auth_service: AuthService = AuthService ()
    user = session.query(Users).filter(Users.email == email).first()
    if user is None or user.password != password:
        raise HTTPException (status_code=401, detail="Incorrect login or password")

    auth_service.google_2f_auth(user)

    response = JSONResponse({"message": "Use QR Code for GA!"})
    response.set_cookie(key="user_id", value=user.id,)
    return response


@router.post("/verify_otp")
async def verify_otp(
        otp: str,
        request: Request,
        session: Session = Depends(get_session),
):
    auth_service: AuthService = AuthService ()
    user_id = UUID(request.cookies.get("user_id"))
    user: Users = session.query(Users).get({"id": user_id})

    if auth_service.verify_otp(otp, user):
        access_token = auth_service.generate_access_token(user_id)
    else:
        raise HTTPException(status_code=401, detail="verification failed")

    return JSONResponse({
        "message": "User is logged in",
        "access_token": access_token
    })




