from pydantic.dataclasses import dataclass


@dataclass
class VimuSubscription:
    stripe_customer_id: str
    stripe_subscription_id: str
    status: str
    user: str
    id: str = None
