from django.core.management.base import BaseCommand
from machines.models import Booking
from machines.views import auto_unbook_machine, send_booking_expiry_notification
from datetime import timedelta
from django.utils import timezone

class Command(BaseCommand):
    help = 'Send alert email and auto unbook the machine if booking expired'    
    msg = 'Your Booking has been expired, Please extend it or free up the machine'
    def handle(self, *args, **kwargs):
        # Get bookings that are expired (end_time <= current_time)
        expiring_bookings = Booking.objects.filter(end_time__lte=(timezone.now()-timedelta(minutes=5)))
        for booking in expiring_bookings:
            auto_unbook_machine(booking.machine.name)
            