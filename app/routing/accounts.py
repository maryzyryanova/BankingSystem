import os
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Request
from starlette.responses import JSONResponse, HTMLResponse

from app.models.models import Accounts
from app.schemas.schemas import AccountsSchema, PercentRateSchema
from app.services.accounts_service import AccountsService
from fastapi.templating import Jinja2Templates


router = APIRouter(prefix="/accounts", tags=["accounts"])

templates = Jinja2Templates(directory=os.path.abspath(os.path.expanduser('app/templates')))
accounts_service: AccountsService = AccountsService()


@router.post("/create", response_class=HTMLResponse)
def create_account(
    request: Request,
    account_data: AccountsSchema,
    percent_rate_data: PercentRateSchema,
):
    print (os.path.abspath (os.path.expanduser ('templates')))
    user_id = request.cookies.get('user_id')
    account: Accounts = accounts_service.create_account(account_data, percent_rate_data, user_id)
    return templates.TemplateResponse("create_account.html", {"request": request, "account": account})


@router.get("/")
async def get_accounts_list(
    request: Request,
):
    user_id = request.cookies.get('user_id')
    accounts: list[Accounts] = accounts_service.get_accounts_list(user_id)
    return templates.TemplateResponse("get_accounts_list.html", {"request": request, "accounts": accounts})


@router.get("/{account_id}")
async def get_account():
    ...


@router.post("/{account_id}/delete")
async def delete_account():
    ...


@router.patch("/{account_id}/deposit")
async def deposit_money():
    ...


@router.patch("/{account_id}/withdraw")
async def withdraw_money():
    ...


@router.patch("/{account_id}/transfer")
async def transfer_money():
    ...


@router.patch("/{account_id}/credit_payment")
async def pay_for_credit():
    ...

