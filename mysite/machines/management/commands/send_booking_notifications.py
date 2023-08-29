from django.core.management.base import BaseCommand
from machines.models import Booking
from machines.views import send_booking_expiry_notification
from datetime import timedelta
from django.utils import timezone

class Command(BaseCommand):
    help = 'Send booking expiry notifications'

    def handle(self, *args, **kwargs):
        # Get bookings that are expired (end_time <= current_time)
        expiring_bookings = Booking.objects.filter(end_time__lte=timezone.now())

        for booking in expiring_bookings:
            # print(booking.user.first_name, booking.user.email, booking.machine.name)
            send_booking_expiry_notification(booking.user.first_name, booking.user.email, booking.machine.name)