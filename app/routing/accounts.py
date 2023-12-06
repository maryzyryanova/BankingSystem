import os

from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from starlette.responses import JSONResponse

from app.models.models import Accounts
from app.schemas.schemas import AccountsSchema, PercentRateSchema, CreateAccountsSchema
from app.services.accounts_service import AccountsService
from app.services.auth_service import AuthService

router = APIRouter(prefix="/accounts", tags=["accounts"])

templates = Jinja2Templates(directory=os.path.abspath(os.path.expanduser('app/templates')))
accounts_service: AccountsService = AccountsService()

auth_service: AuthService = AuthService()


@router.get("/create")
async def create_account(request: Request):
    return templates.TemplateResponse(
        "create_account.html",
        {
            "request": request,
        }
    )


@router.post("/create")
async def create_account(
    request: Request,
    account: CreateAccountsSchema,
):
    access_token = request.cookies.get("access_token")
    user_id = auth_service.get_user_from_jwt(access_token)

    if user_id is None:
        return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

    start_date = account.date_from
    end_date = account.date_till

    account_schema = AccountsSchema(
        account_type=account.account_type,
        currency=account.currency
    )

    percent_rate_schema = PercentRateSchema(
        percent=float(account.percent),
        date_from=start_date,
        date_till=end_date,
        summa=float(account.summa)
    )
    accounts_service.create_account(account_schema, percent_rate_schema, user_id)

    return {"message": "Account created successfully!"}


@router.get("/")
async def get_accounts_list(
    request: Request,
):
    user_id = request.cookies.get('user_id')
    accounts: list[Accounts] = accounts_service.get_accounts_list(user_id)
    return templates.TemplateResponse("get_accounts_list.html", {"request": request, "accounts": accounts})


@router.get("/{account_id}")
async def get_account(
    request: Request
):
    account_id = request.path_params["account_id"]
    account = accounts_service.get_account_by_id(account_id)
    return templates.TemplateResponse("get_account_by_id.html", {"request": request, "account": account})


@router.delete("/{account_id}/delete")
async def delete_account(
    request: Request
):
    account_id = request.path_params["account_id"]
    accounts_service.delete_account_by_id(account_id)
    return templates.TemplateResponse("get_account_by_id.html", {"request": request})


@router.patch("/{account_id}/deposit")
async def deposit_money(
    request: Request,
    amount: str = Form(...),
):
    account_id = request.path_params["account_id"]
    accounts_service.deposit_account(account_id, float(amount))


@router.patch("/{account_id}/withdraw")
async def withdraw_money():
    ...


@router.patch("/{account_id}/transfer")
async def transfer_money():
    ...


@router.patch("/{account_id}/credit_payment")
async def pay_for_credit():
    ...
#
