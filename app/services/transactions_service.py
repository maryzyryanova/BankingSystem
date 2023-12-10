from datetime import datetime
from uuid import uuid4

from sqlmodel import Session

from app.database import get_session
from app.models.models import TransactionsType, Transactions
from app.services.accounts_service import AccountsService


class TransactionsService:
    def __init__(self):
        self.session: Session = get_session()
        self.accounts_service: AccountsService = AccountsService()

    def get_transaction_type_id_by_name(self, transaction_name):
        return self.session.query(TransactionsType).filter(TransactionsType.type_name == transaction_name).first()

    def add_transaction(self, account_id, amount, transaction_type):
        account = self.accounts_service.get_account_by_id (account_id)
        currency_id = account.currency_id
        transaction = self.get_transaction_type_id_by_name(transaction_type)

        transaction = Transactions (
            id=uuid4(),
            account_id=account_id,
            currency_id=currency_id,
            transactions_type_id=transaction.id,
            summa=int(amount),
            transaction_time=datetime.now(),
        )

        self.session.add(transaction)
        self.session.flush()
        self.session.commit()

    def get_all_transactions_by_account_id(self, account_id):
        return self.session.query (Transactions).filter (Transactions.account_id == account_id)

    def delete_transactions_by_account_ids (self, account_id):
        transactions = self.session.query (Transactions).filter(Transactions.account_id == account_id).all()
        for transaction in transactions:
            self.session.delete (transaction)
        self.session.commit()