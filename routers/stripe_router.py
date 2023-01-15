import stripe
from fastapi import APIRouter, Request

from config import settings
from models.api import APIResponse
from models.stripe import StripeSessionRequest
from models.vimu import VimuSubscription
from pocketbase.pocketbase import Pocketbase

router = APIRouter()
pb = Pocketbase(settings.pocketbase_url, settings.pocketbase_admin_email, settings.pocketbase_admin_password)


@router.post("/stripe/session")
async def stripe_create_session(session_request: StripeSessionRequest):
    stripe.api_key = settings.stripe_api_key

    try:
        session = stripe.checkout.Session.create(
            success_url='https://vimu.app/dashboard/account?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='https://vimu.app/dashboard/account',
            customer_email=session_request.email,
            client_reference_id=session_request.user_id,
            mode='subscription',
            line_items=[{
                'price': session_request.price_id,
                'quantity': 1
            }],
        )
    except Exception as e:
        return APIResponse("error", None, str(e))

    return APIResponse("success", session.url, None)


@router.post('/stripe/webhook')
async def stripe_webhook_received(request: Request):
    webhook_secret = 'whsec_9c4d7e6c81a614a78778ad4975a24bf8baa65e3d6eae2af0101ee3e8528b6adf'
    raw_request_data = await request.body()
    signature = request.headers.get('stripe-signature')
    try:
        event = stripe.Webhook.construct_event(
            payload=raw_request_data, sig_header=signature, secret=webhook_secret)
        data = event['data']
    except Exception as e:
        return e

    event_type = event['type']
    data_object = data['object']

    if event_type == 'checkout.session.completed':
        user_id = data_object['client_reference_id']
        stripe_subscription_id = data_object['subscription']
        stripe_customer_id = data_object['customer']
        status = data_object['status']

        subscription = VimuSubscription(stripe_customer_id, stripe_subscription_id, status, user_id)
        pb.create_subscription(subscription)

    elif event_type == 'invoice.paid':
        stripe_subscription_id = data_object['subscription']

        subscription = pb.get_subscription(stripe_subscription_id)
        if subscription is not None:
            subscription.status = data_object['status']
            pb.update_subscription(subscription)

    elif event_type == 'invoice.payment_failed':
        stripe_subscription_id = data_object['subscription']

        subscription = pb.get_subscription(stripe_subscription_id)
        if subscription is not None:
            subscription.status = data_object['status']
            pb.update_subscription(subscription)

    elif event_type == 'customer.subscription.deleted':
        stripe_subscription_id = data_object.stripe_id
        subscription = pb.get_subscription(stripe_subscription_id)

        if subscription is not None:
            pb.delete_subscription(subscription)
    else:
        print('Unhandled event type {}'.format(event_type))

    return APIResponse('success', {}, None)
