import random
from secrets import token_urlsafe
from uuid import uuid4, UUID

import pyotp
from fastapi import APIRouter, Body, Depends, HTTPException
from sqlmodel import Session

from app.database import get_session
from app.models.models import Users, Accounts, AccountsType, Currencies

router = APIRouter(prefix="/register", tags=["register"])


@router.post("", response_model=Users)
def register(email: str, password: str, first_name: str, surname: str,
             session: Session = Depends(get_session)):
    user = session.query(Users).filter(Users.email == email).first()

    if user:
        raise HTTPException(status_code=400, detail="Email already in use")
    else:
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

        account: Accounts = Accounts(
            id=uuid4(),
            user_id=user.id,
            type_id=session.query(AccountsType).filter(AccountsType.account_type == 'general'),
            currency_id=session.query(Currencies).filter(Currencies.currency_name == 'BYN'),
            card_number=random.randint(10 ** 15, 10 ** 16 - 1),
            account_number=random.randint(10 ** 12, 10 ** 13 - 1),
            debet_credit_type=0,
            rest_debit=0
        )

        session.add(account)
        session.flush()
        session.commit()

        return user
