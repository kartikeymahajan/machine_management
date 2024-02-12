from django.core.management.base import BaseCommand
from machines.models import Booking
from machines.views import send_booking_expiry_notification, send_booking_expiry_notification_on_slack
from datetime import timedelta
from django.utils import timezone

class Command(BaseCommand):
    help = 'Send booking expiry notifications'
    msg = 'Your Booking has been expired'
    def handle(self, *args, **kwargs):
        # Get bookings that are expired (end_time <= current_time)
        expiring_bookings = Booking.objects.filter(
            end_time__lte=timezone.now(),
            notification_sent = False
            )
        for booking in expiring_bookings:
            send_booking_expiry_notification_on_slack(booking.user.first_name, booking.machine.name)
            # send_booking_expiry_notification(booking.user.first_name, booking.user.email, booking.machine.name)
            booking.notification_sent = True
            booking.save()