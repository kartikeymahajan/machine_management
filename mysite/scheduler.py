from apscheduler.schedulers.background import BackgroundScheduler
from django.core.management import call_command


def send_booking_notifications_job():
    call_command('send_booking_notifications')

scheduler = BackgroundScheduler()
scheduler.add_job(send_booking_notifications_job, 'interval', minutes=1)  # setting of time interval  minutes=1

scheduler.start()
