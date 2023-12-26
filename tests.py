import datetime
import os
import random
import unittest
from unittest.mock import patch
from uuid import uuid4
from fastapi import Request
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from app.models.models import Accounts, AccountsType, Currencies, PercentRate
from app.schemas.schemas import AccountsSchema, PercentRateSchema, CreateAccountsSchema
from app.services.accounts_service import AccountsService
from app.services.transactions_service import TransactionsService

templates = Jinja2Templates(directory=os.path.abspath(os.path.expanduser('app/templates')))


class AccountsServiceTest(unittest.TestCase):

    def setUp(self):
        self.accounts_service = AccountsService()

    def test_create_credit_account(self):
        account_schema = AccountsSchema(
            account_type='CreditAccount',
            currency='USD',
        )
        percent_rate_schema = PercentRateSchema(
            percent="10",
            date_from=datetime.date.today(),
            date_till = datetime.date.today() + datetime.timedelta(days=365),
            summa=1000
        )
        account: Accounts = self.accounts_service.create_account(
            account_schema,
            percent_rate_schema,
            "e15884da-12f0-40c1-8460-bb865166bc41"
        )

        self.assertEqual(account.rest_debit, percent_rate_schema.summa)
        self.assertEqual(account.rest_credit, percent_rate_schema.summa)
        self.assertEqual(account.max_rest, round(self.accounts_service.monthly_credit_payment(account).max_rest))

        self.accounts_service.session.delete (account)
        self.accounts_service.session.flush ()
        self.accounts_service.session.commit ()

    def test_create_deposit_account(self):
        account_schema = AccountsSchema(
            account_type='DepositAccount',
            currency='EUR',
        )
        percent_rate_schema = PercentRateSchema (
            percent="9",
            date_from=datetime.date.today (),
            date_till=datetime.date.today () + datetime.timedelta (days=365),
            summa=2000
        )

        account: Accounts = self.accounts_service.create_account (
            account_schema,
            percent_rate_schema,
            "f2a3f9d8-e230-45cf-b80a-e14d99a57282"
        )

        self.assertEqual (account.rest_debit, percent_rate_schema.summa)
        self.assertEqual (account.rest_credit, percent_rate_schema.summa)
        self.assertEqual (account.max_rest, 0)

        self.accounts_service.session.delete (account)
        self.accounts_service.session.flush ()
        self.accounts_service.session.commit ()

    def test_get_accounts_list (self):
        user_id = "f2a3f9d8-e230-45cf-b80a-e14d99a57282"
        currency_id = "198d15a0-67a6-443b-88bf-83816aef3a76"
        account1 = Accounts (
            id=uuid4 (),
            user_id=user_id,
            type_id="5e291af7-cc3d-4435-9f23-f8e6cb64fb86",
            currency_id=currency_id,
            rest_debit=0,
            rest_credit=0,
            max_rest=0,
            card_number=random.randint (10 ** 15, 10 ** 16 - 1),
            account_number=random.randint (10 ** 12, 10 ** 13 - 1),
            is_blocked=False
        )
        account2 = Accounts (
            id=uuid4 (),
            user_id=user_id,
            type_id="d872ce19-e195-472d-8a7d-b095b9cc10b6",
            currency_id=currency_id,
            rest_debit=0,
            rest_credit=500,
            max_rest=0,
            card_number=random.randint (10 ** 15, 10 ** 16 - 1),
            account_number=random.randint (10 ** 12, 10 ** 13 - 1),
            is_blocked=False
        )
        account3 = Accounts (
            id=uuid4 (),
            user_id=user_id,
            type_id="56cac666-9a6f-4d79-9a4a-60394a07fe06",
            currency_id=currency_id,
            rest_debit=300,
            rest_credit=0,
            max_rest=0,
            card_number=random.randint (10 ** 15, 10 ** 16 - 1),
            account_number=random.randint (10 ** 12, 10 ** 13 - 1),
            is_blocked=False
        )

        self.accounts_service.session.add (account1)
        self.accounts_service.session.add (account2)
        self.accounts_service.session.add (account3)
        self.accounts_service.session.flush ()
        self.accounts_service.session.commit ()

        accounts_list = self.accounts_service.get_accounts_list (user_id).all()

        self.assertEqual (len(accounts_list), 3)
        self.assertEqual (accounts_list[0].id, account1.id)
        self.assertEqual (accounts_list[1].id, account2.id)
        self.assertEqual (accounts_list[2].id, account3.id)

        self.accounts_service.session.delete (account1)
        self.accounts_service.session.delete (account2)
        self.accounts_service.session.delete (account3)
        self.accounts_service.session.flush ()
        self.accounts_service.session.commit ()

    def test_get_account_by_id (self):
        account_id = uuid4()
        account = Accounts (
            id=account_id,
            user_id="e15884da-12f0-40c1-8460-bb865166bc41",
            type_id="5e291af7-cc3d-4435-9f23-f8e6cb64fb86",
            currency_id="198d15a0-67a6-443b-88bf-83816aef3a76",
            rest_debit=0,
            rest_credit=0,
            max_rest=0,
            card_number=random.randint (10 ** 15, 10 ** 16 - 1),
            account_number=random.randint (10 ** 12, 10 ** 13 - 1),
            is_blocked=False
        )

        self.accounts_service.session.add(account)
        self.accounts_service.session.flush()
        self.accounts_service.session.commit()

        retrieved_account = self.accounts_service.get_account_by_id (account_id)

        self.assertEqual (retrieved_account.id, account.id)
        self.assertEqual (retrieved_account.user_id, account.user_id)
        self.assertEqual (retrieved_account.type_id, account.type_id)
        self.assertEqual (retrieved_account.currency_id, account.currency_id)
        self.assertEqual (retrieved_account.rest_debit, account.rest_debit)
        self.assertEqual (retrieved_account.rest_credit, account.rest_credit)
        self.assertEqual (retrieved_account.max_rest, account.max_rest)

        self.accounts_service.session.delete (account)
        self.accounts_service.session.flush ()
        self.accounts_service.session.commit ()

    def test_delete_account_by_id (self):
        account_id = uuid4()
        account = Accounts(
            id=account_id,
            user_id="e15884da-12f0-40c1-8460-bb865166bc41",
            type_id="5e291af7-cc3d-4435-9f23-f8e6cb64fb86",
            currency_id="198d15a0-67a6-443b-88bf-83816aef3a76",
            rest_debit=0,
            rest_credit=0,
            max_rest=0,
            card_number=random.randint (10 ** 15, 10 ** 16 - 1),
            account_number=random.randint (10 ** 12, 10 ** 13 - 1),
            is_blocked=False
        )

        self.accounts_service.session.add (account)
        self.accounts_service.session.flush ()
        self.accounts_service.session.commit ()

        self.accounts_service.delete_account_by_id (account_id)

        retrieved_account = self.accounts_service.get_account_by_id (account_id)
        self.assertEqual (retrieved_account, None)

    def test_withdraw_money_from_account_with_sufficient_balance (self):
        account_id = uuid4 ()
        account = Accounts (
            id=account_id,
            user_id="e15884da-12f0-40c1-8460-bb865166bc41",
            type_id="56cac666-9a6f-4d79-9a4a-60394a07fe06",
            currency_id="198d15a0-67a6-443b-88bf-83816aef3a76",
            rest_debit=300,
            rest_credit=0,
            max_rest=0,
            card_number=random.randint (10 ** 15, 10 ** 16 - 1),
            account_number=random.randint (10 ** 12, 10 ** 13 - 1),
            is_blocked=False
        )

        self.accounts_service.session.add (account)
        self.accounts_service.session.flush ()
        self.accounts_service.session.commit ()

        amount = 50
        self.accounts_service.withdraw_money_from_account (account_id, amount)

        updated_account = self.accounts_service.get_account_by_id (account_id)

        self.assertEqual (updated_account.rest_debit, account.rest_debit)

        self.accounts_service.session.delete (account)
        self.accounts_service.session.flush ()
        self.accounts_service.session.commit ()

    def test_withdraw_money_from_account_with_insufficient_balance (self):
        account_id = uuid4 ()
        account = Accounts (
            id=account_id,
            user_id="e15884da-12f0-40c1-8460-bb865166bc41",
            type_id="5e291af7-cc3d-4435-9f23-f8e6cb64fb86",
            currency_id="198d15a0-67a6-443b-88bf-83816aef3a76",
            rest_debit=0,
            rest_credit=0,
            max_rest=0,
            card_number=random.randint (10 ** 15, 10 ** 16 - 1),
            account_number=random.randint (10 ** 12, 10 ** 13 - 1),
            is_blocked=False
        )

        self.accounts_service.session.add (account)
        self.accounts_service.session.flush ()
        self.accounts_service.session.commit ()

        amount = 100
        with self.assertRaises (ValueError) as error:
            self.accounts_service.withdraw_money_from_account (account_id, amount)

        self.assertEqual (str (error.exception), "There is no money")

        self.accounts_service.session.delete (account)
        self.accounts_service.session.flush ()
        self.accounts_service.session.commit ()

    def test_transfer_money_between_accounts_with_sufficient_balance (self):
        account_from_id = uuid4 ()
        account_to_id = uuid4 ()

        account_to = Accounts (
            id=account_to_id,
            user_id="e15884da-12f0-40c1-8460-bb865166bc41",
            type_id="5e291af7-cc3d-4435-9f23-f8e6cb64fb86",
            currency_id="198d15a0-67a6-443b-88bf-83816aef3a76",
            rest_debit=0,
            rest_credit=0,
            max_rest=0,
            card_number=random.randint (10 ** 15, 10 ** 16 - 1),
            account_number=random.randint (10 ** 12, 10 ** 13 - 1),
            is_blocked=False
        )
        account_from = Accounts (
            id=account_from_id,
            user_id="e15884da-12f0-40c1-8460-bb865166bc41",
            type_id="56cac666-9a6f-4d79-9a4a-60394a07fe06",
            currency_id="198d15a0-67a6-443b-88bf-83816aef3a76",
            rest_debit=300,
            rest_credit=0,
            max_rest=0,
            card_number=random.randint (10 ** 15, 10 ** 16 - 1),
            account_number=random.randint (10 ** 12, 10 ** 13 - 1),
            is_blocked=False
        )

        self.accounts_service.session.add (account_from)
        self.accounts_service.session.add (account_to)
        self.accounts_service.session.flush ()
        self.accounts_service.session.commit ()

        amount = 50
        self.accounts_service.transfer_money (account_from.account_number, account_to.account_number, amount)

        updated_account_from = self.accounts_service.get_account_by_id (account_from_id)
        updated_account_to = self.accounts_service.get_account_by_id (account_to_id)

        self.assertEqual (updated_account_from.rest_debit, account_from.rest_debit)
        self.assertEqual (updated_account_to.rest_debit, account_to.rest_debit)

        self.accounts_service.session.delete (account_to)
        self.accounts_service.session.delete (account_from)
        self.accounts_service.session.flush ()
        self.accounts_service.session.commit ()

    def test_transfer_money_between_accounts_with_insufficient_balance (self):
        account_from_id = uuid4 ()
        account_to_id = uuid4 ()

        account_from = Accounts (
            id=account_to_id,
            user_id="e15884da-12f0-40c1-8460-bb865166bc41",
            type_id="5e291af7-cc3d-4435-9f23-f8e6cb64fb86",
            currency_id="198d15a0-67a6-443b-88bf-83816aef3a76",
            rest_debit=0,
            rest_credit=0,
            max_rest=0,
            card_number=random.randint (10 ** 15, 10 ** 16 - 1),
            account_number=random.randint (10 ** 12, 10 ** 13 - 1),
            is_blocked=False
        )
        account_to = Accounts (
            id=account_from_id,
            user_id="e15884da-12f0-40c1-8460-bb865166bc41",
            type_id="56cac666-9a6f-4d79-9a4a-60394a07fe06",
            currency_id="198d15a0-67a6-443b-88bf-83816aef3a76",
            rest_debit=300,
            rest_credit=0,
            max_rest=0,
            card_number=random.randint (10 ** 15, 10 ** 16 - 1),
            account_number=random.randint (10 ** 12, 10 ** 13 - 1),
            is_blocked=False
        )

        self.accounts_service.session.add (account_from)
        self.accounts_service.session.add (account_to)
        self.accounts_service.session.flush ()
        self.accounts_service.session.commit ()

        amount = 70
        with self.assertRaises (ValueError) as error:
            self.accounts_service.transfer_money (account_from.account_number, account_to.account_number, amount)

        self.assertEqual (str (error.exception), "There is no money")
        self.accounts_service.session.add (account_from)
        self.accounts_service.session.add (account_to)
        self.accounts_service.session.flush ()
        self.accounts_service.session.commit ()


class CreateAccountEndpointTest(unittest.TestCase):

    def setUp(self):
        self.accounts_service = AccountsService()

    @patch("accounts_service.auth_service.get_user_from_jwt")
    async def test_create_account_with_valid_data(self, mock_get_user_from_jwt):
        user_id = uuid4()
        mock_get_user_from_jwt.return_value = user_id

        create_account_schema = CreateAccountsSchema(
            account_type="CreditAccount",
            currency="USD",
            percent="10",
            date_from="2024-10-10",
            date_till="2023-10-10",
            summa="1000"
        )

        request = Request()
        request.cookies["access_token"] = "mock_access_token"

        response = await self.accounts_service.create_account(request, create_account_schema)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Account created successfully!"})

        created_account = self.accounts_service.get_account_by_id(user_id)
        self.assertEqual(created_account.id, user_id)
        self.assertEqual(created_account.account_type, AccountsType.CREDIT_ACCOUNT)
        self.assertEqual(created_account.currency, "USD")

        if created_account.account_type == AccountsType.CREDIT_ACCOUNT:
            created_percent_rate = self.accounts_service.get_percent_rate_by_id(created_account.percent_rate_id)
            self.assertEqual(created_percent_rate.percent, 10)
            self.assertEqual(created_percent_rate.date_from, datetime.strptime("2023-10-10", "%Y-%m-%d"))
            self.assertEqual(created_percent_rate.date_till, datetime.strptime("2024-10-10", "%Y-%m-%d"))
            self.assertEqual(created_percent_rate.summa, 1000)

        self.accounts_service.session.add (created_account)
        self.accounts_service.session.flush ()
        self.accounts_service.session.commit ()


class GetAccountEndpointTest(unittest.TestCase):

    def setUp(self):
        self.accounts_service = AccountsService()

    @patch("accounts_service.auth_service.get_user_from_jwt")
    async def test_get_account_with_valid_account_id(self, mock_get_user_from_jwt):
        user_id = uuid4()
        account_id = uuid4()
        mock_get_user_from_jwt.return_value = user_id
        account = Accounts(
            id=account_id,
            user_id=user_id,
            account_type=AccountsType.DEFAULT_ACCOUNT,
            currency="USD",
            rest_debit=100,
            rest_credit=0,
            max_rest=0
        )

        self.accounts_service.session.add(account)
        self.accounts_service.session.commit()

        request = Request()

        response = await self.accounts_service.get_account(
            request=request,
            account_id=account_id
        )
        self.assertEqual(type(response), templates.TemplateResponse)

        self.assertEqual(response.context["account"], account)
        currencies = [Currencies(code="USD", name="US Dollar")]
        accounts_type = [AccountsType(name="Default Account")]
        percent_rate = [PercentRate(percent=0, date_from=datetime.now(), date_till=datetime.now())]
        self.assertEqual(response.context["currencies"], currencies)
        self.assertEqual(response.context["accounts_type"], accounts_type)
        self.assertEqual(response.context["percent_rate"], percent_rate)
        self.assertEqual(response.context["account_id"], account_id)

        self.accounts_service.session.add (account)
        self.accounts_service.session.flush ()
        self.accounts_service.session.commit ()


class DepositMoneyEndpointTest(unittest.TestCase):

    def setUp(self):
        self.accounts_service = AccountsService()
        self.transaction_service = TransactionsService()

    @patch("accounts_service.auth_service.get_user_from_jwt")
    async def test_deposit_money_with_valid_account_id(self, mock_get_user_from_jwt):
        user_id = uuid4()
        account_id = uuid4()
        mock_get_user_from_jwt.return_value = user_id
        account = Accounts(
            id=account_id,
            user_id=user_id,
            account_type=AccountsType.DEFAULT_ACCOUNT,
            currency="USD",
            rest_debit=500,
            rest_credit=0,
            max_rest=0
        )

        # Add the mock account to the database
        self.accounts_service.session.add(account)
        self.accounts_service.session.commit()

        request = Request()
        amount = 200
        response = await self.accounts_service.deposit_money(
            request=request,
            account_id=account_id,
            amount=amount
        )

        self.assertEqual(type(response), RedirectResponse)

        updated_account = self.accounts_service.get_account_by_id(account_id)
        self.assertEqual(updated_account.rest_debit, account.rest_debit + int(amount))

        transactions = self.transaction_service.get_all_transactions_by_account_id(account_id)
        self.assertEqual(len(transactions), 1)
        transaction = transactions[0]
        self.assertEqual(transaction.account_id, account_id)
        self.assertEqual(transaction.amount, int(amount))
        self.assertEqual(transaction.type, "Deposit")


class WithdrawMoneyEndpointTest(unittest.TestCase):

    def setUp(self):
        self.accounts_service = AccountsService()
        self.transaction_service = TransactionsService()

    @patch("accounts_service.auth_service.get_user_from_jwt")
    async def test_withdraw_money_with_valid_account_id(self, mock_get_user_from_jwt):
        # Create a mock user ID and a mock account
        user_id = uuid4()
        account_id = uuid4()
        mock_get_user_from_jwt.return_value = user_id
        account = Accounts(
            id=account_id,
            user_id=user_id,
            account_type=AccountsType.DEFAULT_ACCOUNT,
            currency="USD",
            rest_debit=500,
            rest_credit=0,
            max_rest=0
        )
        self.accounts_service.session.add(account)
        self.accounts_service.session.commit()

        # Create a Request object
        request = Request()

        # Simulate an amount of money to be withdrawn
        amount = 300

        # Call the withdraw_money endpoint
        response = await self.accounts_service.withdraw_money(
            request=request,
            account_id=account_id,
            amount=amount
        )

        # Verify that the response is a redirect response
        self.assertEqual(type(response), RedirectResponse)

        # Verify that the account's balance is updated
        updated_account = self.accounts_service.get_account_by_id(account_id)
        self.assertEqual(updated_account.rest_debit, account.rest_debit - int(amount))

        # Verify that a transaction is created
        transactions = self.transaction_service.get_all_transactions_by_account_id(account_id)
        self.assertEqual(len(transactions), 1)
        transaction = transactions[0]
        self.assertEqual(transaction.account_id, account_id)
        self.assertEqual(transaction.amount, int(amount))
        self.assertEqual(transaction.type, "Withdrawal")


if __name__ == '__main__':
    unittest.main()
