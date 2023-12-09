import datetime
from typing import Optional, List
from uuid import UUID

from fastapi import HTTPException
from sqlmodel import SQLModel, Field, Relationship


class Accounts(SQLModel, table=True):
    id: UUID = Field(primary_key=True, unique=True, nullable=False)
    rest_debit: int
    rest_credit: int
    max_rest: int
    debit_credit_type: int
    card_number: int
    account_number: int

    user_id: Optional[UUID] = Field (foreign_key='users.id')
    users: Optional["Users"] = Relationship (back_populates="accounts")

    transactions: List["Transactions"] = Relationship(back_populates="accounts")

    currency_id: Optional[UUID] = Field(foreign_key='currencies.id')
    currencies: Optional["Currencies"] = Relationship(back_populates="accounts")

    type_id: Optional[UUID] = Field(foreign_key='accounts_type.id')
    accounts_type: Optional["AccountsType"] = Relationship(back_populates="accounts")

    percent_rate_id: Optional[UUID] = Field(foreign_key='percent_rate.id')
    percent_rate: Optional["PercentRate"] = Relationship(back_populates="accounts")


class AccountsType(SQLModel, table=True):
    __tablename__ = "accounts_type"

    id: UUID = Field(default=False, primary_key=True, unique=True, nullable=False)
    account_type: str

    accounts: List["Accounts"] = Relationship(back_populates="accounts_type")


class Currencies(SQLModel, table=True):
    id: UUID = Field(default=False, primary_key=True, unique=True, nullable=False)
    currency_name: str

    accounts: List["Accounts"] = Relationship(back_populates="currencies")

    transactions: List["Transactions"] = Relationship (back_populates="currencies")


class Transactions(SQLModel, table=True):
    id: UUID = Field(default=False, primary_key=True, unique=True, nullable=False)
    summa: int
    transaction_time: datetime.datetime

    account_id: Optional[UUID] = Field(default=False, foreign_key='accounts.id')
    accounts: Optional[Accounts] = Relationship(back_populates="transactions")

    currency_id: Optional[UUID] = Field (default=False, foreign_key='currencies.id')
    currencies: Optional[Currencies] = Relationship (back_populates="transactions")

    transactions_type_id: Optional[UUID] = Field (default=False, foreign_key='transactions_type.id')
    transactions_type: Optional["TransactionsType"] = Relationship (back_populates="transactions")


class TransactionsType(SQLModel, table=True):
    __tablename__ = "transactions_type"

    id: UUID = Field(default=False, primary_key=True, unique=True, nullable=False)
    type_name: str

    transactions: List[Transactions] = Relationship (back_populates="transactions_type")


class Users(SQLModel, table=True):
    id: UUID = Field(primary_key=True, unique=True, nullable=False)
    email: str = Field(default="", unique=True, nullable=False)
    password: str = Field(default="", nullable=False)
    first_name: str = Field(default="", nullable=False)
    surname: str = Field(default="", nullable=False)
    secret: str = Field(default="", nullable=False)

    accounts: List["Accounts"] = Relationship (back_populates="users")

    def read_from_database_by_id(self, session):
        user: Users = session.get(Users, self.id)
        if not user:
            raise HTTPException(status_code=404, detail="user not found")
        self = user
        return self


class PercentRate(SQLModel, table=True):
    __tablename__ = "percent_rate"

    id: UUID = Field(primary_key=True, unique=True, nullable=False)
    valid_from: datetime.datetime = Field(nullable=False)
    valid_till: datetime.datetime = Field(nullable=False)
    percent_size: int = Field(nullable=False)

    accounts: List["Accounts"] = Relationship(back_populates="percent_rate")

