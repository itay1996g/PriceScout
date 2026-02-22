import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.subscription import Subscription

stripe.api_key = settings.stripe_secret_key

router = APIRouter(prefix="/api/billing", tags=["billing"])


@router.post("/create-checkout")
def create_checkout(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    session = stripe.checkout.Session.create(
        mode="subscription",
        payment_method_types=["card"],
        line_items=[{"price": settings.stripe_price_id, "quantity": 1}],
        success_url=f"{settings.frontend_url}?checkout=success",
        cancel_url=f"{settings.frontend_url}?checkout=canceled",
        client_reference_id=user.id,
        customer_email=user.email,
    )
    return {"url": session.url}


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        raise HTTPException(status_code=400, detail="Invalid webhook")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = session.get("client_reference_id")
        stripe_sub_id = session.get("subscription")

        if user_id and stripe_sub_id:
            subscription = Subscription(
                user_id=user_id,
                stripe_id=stripe_sub_id,
                status="active",
                plan="pro",
            )
            db.add(subscription)
            db.commit()

    elif event["type"] == "customer.subscription.deleted":
        sub_data = event["data"]["object"]
        subscription = (
            db.query(Subscription)
            .filter(Subscription.stripe_id == sub_data["id"])
            .first()
        )
        if subscription:
            subscription.status = "canceled"
            db.commit()

    return {"status": "ok"}
