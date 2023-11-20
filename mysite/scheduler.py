from apscheduler.schedulers.background import BackgroundScheduler
from django.core.management import call_command
from datetime import datetime

def send_booking_notifications_job():
    call_command('send_booking_notifications')

def send_daily_message():
    call_command('send_hardware_updates')

scheduler = BackgroundScheduler()
scheduler.add_job(send_booking_notifications_job, 'interval', hours=2)  # setting of time interval  minutes=1
# 'cron' style scheduling to run every day at 8:00 AM. You can adjust the time as needed.
scheduler.add_job(send_daily_message, 'cron', hour=00, minute=30)

scheduler.start()
