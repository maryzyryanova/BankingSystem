import datetime
import random
from uuid import UUID, uuid4

from sqlmodel import Session

from app.database import get_session
from app.models.models import AccountsType, Currencies, Accounts, PercentRate
from app.schemas.schemas import AccountsSchema, PercentRateSchema
from app.services.percent_rate_service import PercentRateService


class AccountsService:
    def __init__(self):
        self.session: Session = get_session()
        self.percent_rate_service = PercentRateService()

    def create_account(self, accounts_schema: AccountsSchema,
                       percent_rate_schema: PercentRateSchema, user_id: UUID) -> Accounts:
        rest_credit, rest_debet = 0, 0
        if accounts_schema.account_type == 'CreditAccount':
            rest_credit, rest_debet = percent_rate_schema.summa, percent_rate_schema.summa
        elif accounts_schema.account_type == 'DepositAccount':
            rest_debet = percent_rate_schema.summa
            rest_credit = percent_rate_schema.summa
        elif accounts_schema.account_type == 'DefaultAccount':
            rest_credit, rest_debet = 0, 0

        if percent_rate_schema is not None:
            percent_rate = self.percent_rate_service.create_percent_rate(percent_rate_schema)
            percent_rate_id = percent_rate.id
        else:
            percent_rate_id = ''

        type_id: UUID= self.session.query(AccountsType).filter(AccountsType.account_type == accounts_schema.account_type).first().id
        currency_id: UUID= self.session.query(Currencies).filter(Currencies.currency_name == accounts_schema.currency).first().id

        account = Accounts(
            id=uuid4(),
            user_id=user_id,
            percent_rate_id=(percent_rate_id if percent_rate_id else None),
            type_id=type_id,
            currency_id=currency_id,
            rest_debit=rest_debet,
            rest_credit=rest_credit,
            max_rest=0,
            card_number=random.randint(10 ** 15, 10 ** 16 - 1),
            account_number=random.randint(10**12, 10**13 - 1),
            is_blocked=False
        )

        if accounts_schema.account_type == 'CreditAccount':
            account = self.monthly_credit_payment(account)

        self.session.add(account)
        self.session.flush()
        self.session.commit()

        return account

    def get_accounts_list(self, user_id):
        return self.session.query(Accounts).filter(Accounts.user_id == user_id)

    def get_account_by_id(self, account_id):
        return self.session.query(Accounts).filter(Accounts.id == account_id).first()

    def delete_account_by_id(self, account_id):
        account = self.get_account_by_id(account_id)
        self.session.delete(account)
        self.session.commit()

    def withdraw_money_from_account(self, account_id, amount):
        account = self.get_account_by_id(account_id)

        if account.rest_debit < amount:
            raise ValueError("There is no money")

        params = {"rest_debit": account.rest_debit - amount}
        self.update_account(account_id, params)

    def update_account(self, account_id, params):
        self.session.query(Accounts).filter(Accounts.id == account_id).update(params)
        self.session.commit()

    def deposit_money_to_account(self, account_id, amount, transactions):
        account: Accounts = self.get_account_by_id(account_id)
        account_type: str = self.session.query(AccountsType).filter(AccountsType.id == account.type_id).first().account_type
        if account_type != 'DepositAccount':
            self.session.query(Accounts).filter (Accounts.id == account_id).update ({"rest_debit": account.rest_debit + amount})
        else:
            self.top_up_deposit(account, transactions)
        self.session.commit ()

    def get_account_by_account_number(self, account_number):
        return self.session.query(Accounts).filter(Accounts.account_number == account_number).first()

    def transfer_money(self, account_from, account_to, amount):
        account_from: Accounts = self.get_account_by_account_number(account_from)
        account_to: Accounts = self.get_account_by_account_number (account_to)

        if account_from.rest_debit < amount:
            raise ValueError("There is no money")

        self.session.query(Accounts).filter(Accounts.id == account_from.id).update({"rest_debit": account_from.rest_debit - amount})
        self.session.query(Accounts).filter(Accounts.id == account_to.id).update({"rest_debit": account_to.rest_debit + amount})

    def top_up_deposit(self, account, transactions):
        percent_rate: PercentRate = self.session.query(PercentRate).filter(PercentRate.id == account.percent_rate_id).first()

        days_since_open = (datetime.datetime.now() - percent_rate.valid_from).days

        interest_earned_before = 0
        for transaction in transactions:
            duration = datetime.date.today() - transaction.transaction_time.date()
            days_since_transaction = duration.days
            interest_earned_before += transaction.summa * (percent_rate.percent_size / 100) * (
                        days_since_open - days_since_transaction) / 365
        total_amount = account.rest_credit + interest_earned_before
        account.rest_debit = total_amount
        self.session.commit()

    def monthly_credit_payment(self, account: Accounts):
        percent_rate: PercentRate = self.session.query(PercentRate).filter(PercentRate.id == account.percent_rate_id).first()
        rest_credit = account.rest_credit

        monthly_percent = percent_rate.percent_size / 12 / 100
        period = (percent_rate.valid_till - percent_rate.valid_from).days // 12
        monthly_payment = rest_credit * monthly_percent / (1 - (1 + monthly_percent) ** (-period))

        account.max_rest = monthly_payment
        return account

    def filter_accounts_by_type (self, type, user_id):
        default_account_numbers: list[Accounts] = self.session.query (
            Accounts
        ).filter (
            Accounts.type_id == AccountsType.id
        ).filter (
            AccountsType.account_type == type
        ).filter (
            Accounts.user_id == user_id
        ).all ()
        return default_account_numbers

    def return_money_from_deposit(self, account_id, transactions):
        account: Accounts = self.get_account_by_id(account_id)
        percent_rate: PercentRate = self.session.query(PercentRate).filter(PercentRate.id == account.percent_rate_id).first()

        date_of_withdrawal = datetime.datetime.now()
        end_of_deposit = percent_rate.valid_till
        start_of_deposit = percent_rate.valid_from

        self.top_up_deposit(account, transactions)
        funds = account.rest_debit

        if date_of_withdrawal < end_of_deposit:
            fee = funds * (date_of_withdrawal - start_of_deposit).days / (end_of_deposit - start_of_deposit).days
        else:
            fee = 0
        return funds, fee

    def filter_accounts_by_currency_id (self, account):
        default_account_numbers = []
        for a in self.session.query (
                Accounts
        ).filter (
            Accounts.currency_id == account.currency_id
        ).all ():
            if a.id != account.id:
                default_account_numbers.append(a)

        return default_account_numbers

    def change_account_status(self, account: Accounts, status):
        if status == 'false':
            account.is_blocked = False
        elif status == 'true':
            account.is_blocked = True
        self.session.commit()


