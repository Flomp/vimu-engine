from pydantic.dataclasses import dataclass


@dataclass
class StripeSessionRequest:
    price_id: str
    email: str
    user_id: str
