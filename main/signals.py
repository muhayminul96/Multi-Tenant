from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order, OrderItem
from django.core.mail import send_mail

@receiver(post_save, sender=Order)
def notify_vendor_on_order(sender, instance, created, **kwargs):
    if created:
        # Get all unique vendors from the order's items
        vendors = set()
        for item in instance.items.all():
            vendors.add(item.product.vendor)

        for vendor in vendors:
            # Example notification via email (you could switch to any notifier service)
            send_mail(
                subject="New Order Received",
                message=f"Hello {vendor.user.username},\nYou have received a new order containing your product(s).",
                from_email="noreply@hungrytiger.com",
                recipient_list=[vendor.user.email],
                fail_silently=True
            )
