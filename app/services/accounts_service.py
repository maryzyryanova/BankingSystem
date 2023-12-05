import random
from uuid import UUID, uuid4

from sqlmodel import Session

from app.database import get_session
from app.models.models import AccountsType, Currencies, Accounts
from app.schemas.schemas import AccountsSchema, PercentRateSchema
from app.services.percent_rate_service import PercentRateService


class AccountsService:
    def __init__(self):
        self.session: Session = get_session()
        self.percent_rate_service = PercentRateService()

    def create_account(self, accounts_schema: AccountsSchema,
                       percent_rate_schema: PercentRateSchema, user_id: UUID) -> Accounts:
        debet_credit, rest_credit, rest_debet = 0, 0, 0

        if accounts_schema.account_type == 'CreditAccount':
            debet_credit, rest_credit, rest_debet = 1, percent_rate_schema.summa, percent_rate_schema.summa
        elif accounts_schema.account_type == 'DepositAccount':
            rest_debet = percent_rate_schema.summa

        if percent_rate_schema.percent is not None:
            percent_rate = self.percent_rate_service.create_percent_rate(percent_rate_schema)
            percent_rate_id = percent_rate.id
        else:
            percent_rate = ''
            percent_rate_id= ''

        account = Accounts(
            id=uuid4(),
            user_id=user_id,
            percent_rate_id=percent_rate_id,
            type_id=self.session.query(AccountsType).filter(AccountsType.account_type == accounts_schema.account_type),
            currency_id=self.session.query(Currencies).filter(Currencies.currency_name == accounts_schema.currency),
            rest_debet=rest_debet,
            rest_credit=rest_credit,
            max_rest=0,
            debet_credit_type=debet_credit,
            card_number=random.randint(10 ** 15, 10 ** 16 - 1),
            account_number=random.randint(10**12, 10**13 - 1),
        )

        self.session.add(account)
        self.session.flush()
        self.session.commit()

        return account

    def get_accounts_list(self, user_id):
        return self.session.query(Accounts).filter(Accounts.user_id == user_id)