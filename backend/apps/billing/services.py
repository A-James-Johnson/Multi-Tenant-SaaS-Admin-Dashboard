from django.conf import settings
from apps.billing.models import Payment


class StripeService:
    """Integration-ready Stripe payment gateway service."""

    @staticmethod
    def is_configured():
        return bool(settings.STRIPE_SECRET_KEY)

    @staticmethod
    def create_payment_intent(amount, currency='usd', metadata=None):
        if not StripeService.is_configured():
            return {'error': 'Stripe not configured', 'mock': True, 'client_secret': 'mock_secret'}
        try:
            import stripe
            stripe.api_key = settings.STRIPE_SECRET_KEY
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),
                currency=currency,
                metadata=metadata or {},
            )
            return {'client_secret': intent.client_secret, 'payment_intent_id': intent.id}
        except ImportError:
            return {'error': 'stripe package not installed', 'mock': True}


class RazorpayService:
    """Integration-ready Razorpay payment gateway service."""

    @staticmethod
    def is_configured():
        return bool(settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET)

    @staticmethod
    def create_order(amount, currency='INR', receipt=None):
        if not RazorpayService.is_configured():
            return {'error': 'Razorpay not configured', 'mock': True, 'order_id': 'order_mock'}
        try:
            import razorpay
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            order = client.order.create({
                'amount': int(amount * 100),
                'currency': currency,
                'receipt': receipt or 'receipt_001',
            })
            return order
        except ImportError:
            return {'error': 'razorpay package not installed', 'mock': True}


class BillingService:
    @staticmethod
    def record_payment(tenant, amount, method='manual', status='completed', description=''):
        from django.utils import timezone
        return Payment.objects.create(
            tenant=tenant,
            amount=amount,
            payment_date=timezone.now(),
            method=method,
            status=status,
            description=description,
        )
