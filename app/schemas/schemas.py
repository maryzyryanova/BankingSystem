import datetime

from pydantic import BaseModel


class AccountsSchema(BaseModel):
    account_type: str
    currency: str


class PercentRateSchema(BaseModel):
    percent: int
    date_from: datetime.datetime
    date_till: datetime.datetime
    summa: int