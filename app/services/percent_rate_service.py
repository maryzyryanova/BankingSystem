from uuid import uuid4

from sqlmodel import Session

from app.database import get_session
from app.models.models import PercentRate


class PercentRateService:
    def __init__(self):
        self.session: Session = get_session()

    def create_percent_rate(self, percent_rate_schema) -> PercentRate:
        percent_rate = PercentRate(
            id=uuid4(),
            valid_from=percent_rate_schema.date_from,
            valid_till=percent_rate_schema.date_till,
            percent_size=percent_rate_schema.percent
        )

        self.session.add(percent_rate)
        self.session.flush()
        self.session.commit()

        return percent_rate
