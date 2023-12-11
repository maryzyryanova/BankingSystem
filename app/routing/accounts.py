import os
import VerifyOwner
import starlette.status as status
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app.database import get_session
from app.models.models import Accounts, Users, Currencies, AccountsType, PercentRate, TransactionsType, Transactions
from app.schemas.schemas import AccountsSchema, PercentRateSchema, CreateAccountsSchema
from app.services.accounts_service import AccountsService
from app.services.auth_service import AuthService
from app.services.transactions_service import TransactionsService

router = APIRouter(prefix="/accounts", tags=["accounts"])

templates = Jinja2Templates(directory=os.path.abspath(os.path.expanduser('app/templates')))
accounts_service: AccountsService = AccountsService()

auth_service: AuthService = AuthService()
transaction_service: TransactionsService = TransactionsService()


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
        RedirectResponse("/login")

    start_date = account.date_from
    end_date = account.date_till

    account_schema = AccountsSchema(
        account_type=account.account_type,
        currency=account.currency
    )

    if account_schema.account_type == 'DefaultAccount':
        percent_rate_schema = None
    else:
        percent_rate_schema = PercentRateSchema (
            percent=float(account.percent),
            date_from=start_date,
            date_till=end_date,
            summa=float(account.summa)
        )

    accounts_service.create_account(account_schema, percent_rate_schema, user_id)

    return {"message": "Account created successfully!"}


@router.get("")
async def get_accounts_list(
    request: Request,
    session: Session = Depends (get_session),
):
    access_token = request.cookies.get ("access_token")
    user_id = auth_service.get_user_from_jwt (access_token)

    if user_id is None:
        return RedirectResponse("/login")

    user: Users = session.query (Users).get ({"id": user_id})
    currencies: list[Currencies] = session.query (Currencies).all ()
    accounts_type: list[AccountsType] = session.query (AccountsType).all ()
    accounts: list[Accounts] = accounts_service.get_accounts_list(user_id)
    return templates.TemplateResponse(
        "get_accounts_list.html",
        {
            "request": request,
            "accounts": accounts,
            "user": user,
            "currencies": currencies,
            "accounts_type": accounts_type
        }
    )


@router.get("/{account_id}")
async def get_account(
    request: Request,
    session: Session = Depends (get_session),
):
    access_token = request.cookies.get ("access_token")
    user_id = auth_service.get_user_from_jwt (access_token)

    if user_id is None:
        return RedirectResponse("/login")

    account_id = request.path_params["account_id"]
    account = accounts_service.get_account_by_id(account_id)
    currencies: list[Currencies] = session.query(Currencies).all()
    accounts_type: list[AccountsType] = session.query (AccountsType).all ()
    percent_rate: list[PercentRate] = session.query(PercentRate).all()
    return templates.TemplateResponse(
        "get_account_by_id.html",
        {
            "request": request,
            "account": account,
            "currencies": currencies,
            "accounts_type": accounts_type,
            "percent_rate": percent_rate,
            "account_id": request.path_params["account_id"]
        }
    )


@router.get("/{account_id}/delete")
async def delete_account(
    request: Request,
):
    return templates.TemplateResponse (
        "delete_account_by_id.html",
        {
            "request": request,
            "account_id": request.path_params["account_id"]
        }
    )


@router.post("/{account_id}/delete")
async def delete_account(
    request: Request
):
    access_token = request.cookies.get ("access_token")
    user_id = auth_service.get_user_from_jwt (access_token)

    if user_id is None:
        return RedirectResponse("/login")

    account_id = request.path_params["account_id"]
    account = accounts_service.get_account_by_id(account_id)

    if user_id != str(account.user_id):
        return JSONResponse (status_code=403, content={"detail": "Forbidden"})

    transaction_service.delete_transactions_by_account_ids(account_id)
    accounts_service.delete_account_by_id(account_id)

    return RedirectResponse("/accounts", status_code=status.HTTP_302_FOUND)


@router.get("/{account_id}/deposit")
async def withdraw_money(
    request: Request,
):
    return templates.TemplateResponse (
        "top_up_account.html",
        {
            "request": request,
            "account_id": request.path_params["account_id"]
        }
    )


@router.post("/{account_id}/deposit")
async def deposit_money(
    request: Request,
    amount: str = Form(...)
):
    access_token = request.cookies.get ("access_token")
    user_id = auth_service.get_user_from_jwt (access_token)

    if user_id is None:
        return RedirectResponse ("/login")

    account_id = request.path_params["account_id"]
    transaction_service.add_transaction(account_id, amount, 'Deposit')
    transactions: list[Transactions] = transaction_service.get_all_transactions_by_account_id (account_id)
    accounts_service.deposit_money_to_account(account_id, int(amount), transactions)

    return RedirectResponse (f"/accounts/{account_id}", status_code=status.HTTP_302_FOUND)


@router.get("/{account_id}/withdraw")
async def withdraw_money(
    request: Request,
):
    return templates.TemplateResponse (
        "withdraw_money.html",
        {
            "request": request,
            "account_id": request.path_params["account_id"]
        }
    )


@router.post("/{account_id}/withdraw")
async def withdraw_money(
    request: Request,
    amount: str = Form(...)
):
    access_token = request.cookies.get ("access_token")
    user_id = auth_service.get_user_from_jwt (access_token)

    if user_id is None:
        return RedirectResponse ("/login")

    account_id = request.path_params["account_id"]
    accounts_service.withdraw_money_from_account (account_id, int (amount))
    transaction_service.add_transaction(account_id, amount, 'Withdrawal')
    return RedirectResponse(f"/accounts/{account_id}", status_code=status.HTTP_302_FOUND)


@router.get("/{account_id}/transactions")
async def get_transactions_list(
    request: Request,
    session: Session = Depends (get_session),
):
    access_token = request.cookies.get ("access_token")
    account_id = request.path_params["account_id"]
    user_id = auth_service.get_user_from_jwt (access_token)

    if user_id is None:
        return RedirectResponse ("/login")

    transactions = transaction_service.get_all_transactions_by_account_id(account_id)
    currencies: list[Currencies] = session.query(Currencies).all()
    transactions_type: list[TransactionsType] = session.query(TransactionsType).all()

    return templates.TemplateResponse (
        "transactions_list.html",
        {
            "request": request,
            "account_id": account_id,
            "transactions": transactions,
            "currencies": currencies,
            "transactions_type": transactions_type
        }
    )


@router.get("/{account_id}/transfer")
async def transfer_money(
    request: Request,
):
    account_id = request.path_params["account_id"]
    account: Accounts = accounts_service.get_account_by_id(account_id)
    accounts = accounts_service.filter_accounts_by_currency_id(account)
    return templates.TemplateResponse (
        "transfer_money.html",
        {
            "request": request,
            "account": account,
            "accounts": accounts
        }
    )


@router.post("/{account_id}/transfer")
async def transfer_money(
    request: Request,
    account_to: str = Form(...),
    amount: str = Form()
):
    access_token = request.cookies.get ("access_token")
    account_id = request.path_params["account_id"]
    account: Accounts = accounts_service.get_account_by_id(account_id)
    user_id = auth_service.get_user_from_jwt (access_token)

    if user_id is None:
        return RedirectResponse ("/login")

    if VerifyOwner.VerifyOwner('authenticate via Touch ID'):
        accounts_service.transfer_money(account.account_number, account_to, int(amount))
        transaction_service.add_transaction(account_id, amount, 'Transfer')
        transaction_service.add_transaction(accounts_service.get_account_by_account_number(account_to).id, amount, 'Transfer')
        return RedirectResponse(f"/accounts/{account_id}", status_code=status.HTTP_302_FOUND)


@router.get("/{account_id}/credit_payment")
async def pay_for_credit(
    request: Request,
):
    access_token = request.cookies.get ("access_token")
    user_id = auth_service.get_user_from_jwt (access_token)

    if user_id is None:
        return RedirectResponse ("/login")

    account_id = request.path_params["account_id"]
    account = accounts_service.get_account_by_id(account_id)
    default_accounts = accounts_service.filter_accounts_by_type("DefaultAccount", user_id)
    return templates.TemplateResponse (
        "credit_payment.html",
        {
            "request": request,
            "account": account,
            "default_accounts": default_accounts
        }
    )


@router.post("/{account_id}/credit_payment")
async def pay_for_credit(
    request: Request,
    account_from: str = Form(...)
):
    access_token = request.cookies.get ("access_token")
    user_id = auth_service.get_user_from_jwt (access_token)

    if user_id is None:
        return RedirectResponse("/login")

    account_id = request.path_params["account_id"]
    account_to: Accounts = accounts_service.get_account_by_id (account_id)
    account_from: Accounts = accounts_service.get_account_by_account_number (int(account_from))

    if VerifyOwner.VerifyOwner('authenticate via Touch ID'):
        accounts_service.update_account(account_from.id, {"rest_debit": account_from.rest_debit - account_to.max_rest})
        accounts_service.update_account(account_to.id, {"rest_credit": account_to.rest_credit - account_to.max_rest})
        transaction_service.add_transaction(account_id, account_to.max_rest, 'CreditPayment')
        return RedirectResponse(f"/accounts/{account_id}", status_code=status.HTTP_302_FOUND)


@router.get("/{account_id}/withdraw_deposit")
async def withdraw_deposit(
    request: Request,
):
    account_id = request.path_params["account_id"]
    transactions: list[Transactions] = transaction_service.get_all_transactions_by_account_id (account_id)
    funds, fee = accounts_service.return_money_from_deposit (account_id, transactions)
    return templates.TemplateResponse (
        "withdraw_deposit.html",
        {
            "request": request,
            "account_id": account_id,
            "funds": funds,
            "fee": fee
        }
    )


@router.post("/{account_id}/withdraw_deposit")
async def withdraw_deposit(
    request: Request,
    funds: str = Form(...),
    fee: str = Form(...)
):
    account_id = request.path_params["account_id"]
    access_token = request.cookies.get ("access_token")
    user_id = auth_service.get_user_from_jwt (access_token)

    if user_id is None:
        return RedirectResponse ("/login")

    if VerifyOwner.VerifyOwner('authenticate via Touch ID'):
        funds = float(funds) - float(fee)
        accounts_service.withdraw_money_from_account(account_id, funds)
        transaction_service.add_transaction(account_id, funds, 'DepositWithdrawal')
        return RedirectResponse(f"/accounts/{account_id}", status_code=status.HTTP_302_FOUND)


@router.get("/{account_id}/change_status")
async def change_status(
    request: Request,
):
    account: Accounts = accounts_service.get_account_by_id(request.path_params["account_id"])
    return templates.TemplateResponse (
        "change_status.html",
        {
            "request": request,
            "account": account
        }
    )


@router.post("/{account_id}/change_status")
async def change_status(
    request: Request,
    is_blocked = Form(...)
):
    account = accounts_service.get_account_by_id (request.path_params["account_id"])
    accounts_service.change_account_status (account, is_blocked)
    return RedirectResponse (f"/accounts/{account.id}", status_code=status.HTTP_302_FOUND)

