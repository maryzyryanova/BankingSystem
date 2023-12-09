import datetime
from typing import Optional

from pydantic import BaseModel


class AccountsSchema(BaseModel):
    account_type: str
    currency: str


class PercentRateSchema(BaseModel):
    percent: Optional[float] = 0.0
    date_from: Optional[datetime.date] = None
    date_till: Optional[datetime.date] = None
    summa: Optional[float] = 0.0


class CreateAccountsSchema(BaseModel):
    account_type: str
    currency: str
    percent: Optional[str]
    date_from: Optional[datetime.date]
    date_till: Optional[datetime.date]
    summa: Optional[str]
